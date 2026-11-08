# Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
"""Privacy cross-check for native DLLs before shipping: prints the PE debug directory (CodeView / PDB path), the linker time
stamp, and every ASCII / UTF-16 string that looks like a path, URL, mail address, or names a file the DLL may write.
  python dll_strings.py <dll> [...]        read only; prints ASCII-safe text
A clean release DLL shows no PDB path and no drive / user paths. Standard library only."""
import re
import struct
import sys


def strings(b, minlen=5):
    for m in re.finditer(rb'[\x20-\x7e]{%d,}' % minlen, b):
        yield 'a', m.start(), m.group().decode('ascii')
    for m in re.finditer(rb'(?:[\x20-\x7e]\x00){%d,}' % minlen, b):
        yield 'w', m.start(), m.group().decode('utf-16-le')


def pe_info(b):
    pe = struct.unpack_from('<i', b, 0x3C)[0]
    assert b[pe:pe + 4] == b'PE\0\0', 'not a PE file'
    machine, nsec, ts = struct.unpack_from('<HHI', b, pe + 4)
    opt = pe + 24
    magic = struct.unpack_from('<H', b, opt)[0]
    dd = opt + (112 if magic == 0x20B else 96)
    secs = pe + 24 + struct.unpack_from('<H', b, pe + 20)[0]
    sec = [struct.unpack_from('<8sIIII', b, secs + 40 * i) for i in range(nsec)]

    def rva2off(rva):
        for _name, vs, va, rs, ro in sec:
            if va <= rva < va + max(vs, rs):
                return rva - va + ro
        return None

    dbg_rva, dbg_size = struct.unpack_from('<II', b, dd + 8 * 6)
    out = dict(machine=hex(machine), timestamp=ts, debug=[])
    if dbg_rva and dbg_size:
        off = rva2off(dbg_rva)
        for i in range(dbg_size // 28):
            _ch, _tds, _maj, _mnr, typ, size, _addr, ptr = struct.unpack_from('<IIHHIIII', b, off + 28 * i)
            e = dict(type=typ, size=size)
            if typ == 2 and b[ptr:ptr + 4] == b'RSDS':
                e['pdb'] = b[ptr + 24:b.index(b'\0', ptr + 24)].decode('utf-8', 'replace')
            out['debug'].append(e)
    return out


def main():
    rx = re.compile(r'[A-Za-z]:[\\/]|\\\\|/home/|Users|https?:|@[A-Za-z0-9-]+\.|'
                    r'\.(pdb|log|ini|off|txt|json|cfg|dat|bin|tmp|bak|cpp|h|hpp|obj|lib|exp)\b', re.I)
    for p in sys.argv[1:]:
        b = open(p, 'rb').read()
        info = pe_info(b)
        print('==', p.replace('\\', '/').split('/')[-1], len(b), 'bytes | machine', info['machine'],
              '| timestamp', info['timestamp'], '| debug directory entries', info['debug'])
        seen = set()
        for kind, off, s in strings(b):
            if rx.search(s) and s not in seen:
                seen.add(s)
                print('  %s @%06x %s' % (kind, off, s[:200].encode('ascii', 'replace').decode()))


if __name__ == '__main__':
    main()
