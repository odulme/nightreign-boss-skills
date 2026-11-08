# Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
"""Install one dev OVERLAY package into a layered me3 dev entry (additive, verified, with backup).

The overlay folder holds ONLY the files that changed this round (relative paths as in the game, e.g. event/m19_00_00_00.emevd.dcx).
It is copied into a NEW package folder (never overwritten), and exactly ONE [[packages]] block

    [[packages]]
    id = "<id>"
    source = "<dest relative to the entry's folder>"
    load_after = [{ id = "<after>", optional = false }]

is inserted after the entry's last package block. <after> must be the entry's current LAST package (protects against stale
assumptions). The entry is re-parsed and compared: nothing but the new block may change. The previous entry text is saved
first; an install manifest (files, sha256, packages, natives, backup) is written next to it.
Rollback = delete the inserted block (or restore the saved text) and the new package folder.

Usage:
  python publish_overlay.py --entry <dev.me3> --overlay <overlay mod folder> --dest <new package folder, e.g. <dev>/<mod>_v012/mod>
                            --id <NewPackageId> --after <CurrentLastPackageId> --note "<what changed>"
                            [--manifest <json {"files": {rel: {"sha256": hex}}}>] [--stage <second copy folder>]
                            [--backup-dir <folder>] [--dry-run]
Requires Python 3.11+ (tomllib). Standard library only. Check that the game is not using the files you replace: this script only
ADDS files and edits the entry text, which is safe while the game runs (the change applies at the next launch).
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import tomllib
from pathlib import Path


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def toml_str(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser(description='Append one overlay package to a layered me3 dev entry.')
    ap.add_argument('--entry', required=True, type=Path)
    ap.add_argument('--overlay', required=True, type=Path)
    ap.add_argument('--dest', required=True, type=Path)
    ap.add_argument('--id', required=True)
    ap.add_argument('--after', required=True)
    ap.add_argument('--note', required=True)
    ap.add_argument('--manifest', type=Path)
    ap.add_argument('--stage', type=Path)
    ap.add_argument('--backup-dir', type=Path)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    entry = a.entry.resolve()
    src = a.overlay.resolve()
    dest = a.dest.resolve()
    backup_dir = (a.backup_dir or entry.parent / 'backups' / 'entry_archive').resolve()

    files = sorted(p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file())
    if not files:
        sys.exit('empty overlay folder')
    hashes = {f: sha256(src / f) for f in files}
    if a.manifest:
        man = json.loads(a.manifest.read_text(encoding='utf-8'))
        want = {k.replace('\\', '/'): v['sha256'].lower() for k, v in man['files'].items()}
        if sorted(want) != files:
            sys.exit('overlay file list differs from its manifest')
        for f in files:
            if not (hashes[f] == want[f] or hashes[f].startswith(want[f])):
                sys.exit(f'hash mismatch: {f}')

    old_bytes = entry.read_bytes()
    old = old_bytes.decode('utf-8')
    cfg = tomllib.loads(old)
    pkgs = cfg.get('packages', [])
    ids = [p['id'] for p in pkgs]
    if not ids or ids[-1] != a.after:
        sys.exit(f'entry packages are {ids}; expected the last one to be {a.after!r}')
    if a.id in ids:
        sys.exit(f'package id {a.id!r} already in the entry')
    if dest.exists():
        sys.exit(f'{dest} already exists; this installer only adds new folders')

    rel = os.path.relpath(dest, entry.parent).replace('\\', '/')
    source = rel if rel.startswith('.') else './' + rel
    block = (f'\n# dev overlay {a.id}: {a.note}\n# Remove this block to go back to {a.after}.\n'
             f'[[packages]]\nid = {toml_str(a.id)}\nsource = {toml_str(source)}\n'
             f'load_after = [{{ id = {toml_str(a.after)}, optional = false }}]\n')

    # Insert right after the last package block (its source line and an optional load_after line); else append at the end.
    last_src = pkgs[-1]['source']
    anchors = [f'source = "{last_src}"\n', f"source = '{last_src}'\n"]
    pos = None
    for anc in anchors:
        if old.count(anc) == 1:
            pos = old.index(anc) + len(anc)
            if old[pos:].startswith('load_after'):
                pos += old[pos:].index('\n') + 1
            break
    if pos is None:
        new = old + ('' if old.endswith('\n') else '\n') + block
    else:
        new = old[:pos] + block + old[pos:]

    c2 = tomllib.loads(new)
    want_new = {'id': a.id, 'source': source, 'load_after': [{'id': a.after, 'optional': False}]}
    ok = ([p['id'] for p in c2['packages']] == ids + [a.id] and c2['packages'][:-1] == pkgs
          and c2['packages'][-1] == want_new
          and {k: v for k, v in c2.items() if k != 'packages'} == {k: v for k, v in cfg.items() if k != 'packages'})
    if not ok:
        sys.exit('re-parsed entry differs from the expected result; nothing written')

    print(f'{len(files)} files -> {dest}')
    print(f'entry block: id={a.id} source={source} after={a.after}')
    if a.dry_run:
        print('dry run: nothing written')
        return 0

    for base in [dest] + ([a.stage.resolve()] if a.stage else []):
        for f in files:
            d = base / f
            d.parent.mkdir(parents=True, exist_ok=True)
            if base is not dest and d.exists():
                if sha256(d) != hashes[f]:
                    sys.exit(f'stage copy differs: {d}')
                continue
            with open(src / f, 'rb') as s, open(d, 'xb') as t:   # exclusive create: never overwrite
                shutil.copyfileobj(s, t, 1 << 20)
            if sha256(d) != hashes[f]:
                sys.exit(f'copy verification failed: {d}')

    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    backup = backup_dir / f'{entry.stem}_before_{a.id}_{stamp}.me3.txt'
    with open(backup, 'xb') as f:
        f.write(old_bytes)
    entry.write_bytes(new.encode('utf-8'))
    if tomllib.loads(entry.read_bytes().decode('utf-8')) != c2:
        entry.write_bytes(old_bytes)
        sys.exit('entry read-back failed; previous text restored')
    log = backup_dir / f'install_manifest_{a.id}.json'
    log.write_text(json.dumps(dict(package=a.id, after=a.after, note=a.note, dest=str(dest), files=hashes,
                                   entry=str(entry), entry_packages=ids + [a.id],
                                   natives=[n.get('path') for n in c2.get('natives', [])], entry_backup=str(backup)),
                              indent=1, ensure_ascii=True), encoding='utf-8')
    print(f'installed {a.id} after {a.after}; previous entry text: {backup}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
