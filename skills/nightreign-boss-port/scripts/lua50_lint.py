#!/usr/bin/env python3
# Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
"""Lint a Lua AI script for constructs that Lua 5.0 (Nightreign's AI Lua) does not accept or that cost heap / privacy.

  python lua50_lint.py my_battle.lua [more.lua ...]

Reports (line: message). Exit code 1 if any ERROR was found. Checks:
  ERROR  non-ASCII bytes (keep scripts ASCII; strings / comments included)
  ERROR  '#' length operator (5.1+)        -> table.getn(t) / string.len(s)
  ERROR  '%' modulo operator (5.1+)        -> math.mod(a, b)
  ERROR  'goto' / '::label::' (5.2+), '//' floor division (5.3+), bitwise & | << >> ~x (5.3+)
  ERROR  '[=[' / ']=]' leveled long brackets (5.1+)
  ERROR  'continue' (not Lua)
  WARN   '...' outside a function parameter list (5.0 uses the implicit 'arg' table)
  WARN   method call on a string literal, e.g. ("x"):format (no string metatable in 5.0)
  WARN   string literal that looks like a local file path (privacy; precompiling keeps string constants)
  INFO   top-level chunk size estimate (lines outside any function) - large main chunks cost AI heap
This is a token-level check, not a parser: confirm with `luac50 -p` afterwards.
"""
import re
import sys

KEYWORDS_BAD = {"goto": "goto (5.2+)", "continue": "continue (not Lua)"}
PATH_RE = re.compile(r"([A-Za-z]:[\\/])|(\\\\[A-Za-z0-9_.-]+\\)|(/(home|Users)/)|(\\Users\\)", re.I)


def tokenize(src):
    """Yield (kind, text, line). kind in: str, comment, name, num, op, ws."""
    i, n, line = 0, len(src), 1
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
            continue
        if c in " \t\r\f\v":
            i += 1
            continue
        if src.startswith("--", i):
            m = re.match(r"--\[(=*)\[", src[i:])
            if m:
                close = "]" + m.group(1) + "]"
                j = src.find(close, i + len(m.group(0)))
                j = n if j < 0 else j + len(close)
                text = src[i:j]
                yield ("comment", text, line, m.group(1) != "")
                line += text.count("\n")
                i = j
                continue
            j = src.find("\n", i)
            j = n if j < 0 else j
            yield ("comment", src[i:j], line, False)
            i = j
            continue
        m = re.match(r"\[(=*)\[", src[i:])
        if m:
            close = "]" + m.group(1) + "]"
            j = src.find(close, i + len(m.group(0)))
            j = n if j < 0 else j + len(close)
            text = src[i:j]
            yield ("str", text, line, m.group(1) != "")
            line += text.count("\n")
            i = j
            continue
        if c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == "\\":
                    j += 1
                if j < n and src[j] == "\n":
                    line += 1
                j += 1
            yield ("str", src[i:j + 1], line, False)
            i = j + 1
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", src[i:])
        if m:
            yield ("name", m.group(0), line, False)
            i += len(m.group(0))
            continue
        m = re.match(r"0[xX][0-9A-Fa-f]+|\d+\.?\d*([eE][+-]?\d+)?|\.\d+([eE][+-]?\d+)?", src[i:])
        if m and m.group(0):
            yield ("num", m.group(0), line, False)
            i += len(m.group(0))
            continue
        for op in ("...", "..", "==", "~=", "<=", ">=", "//", "::", "<<", ">>"):
            if src.startswith(op, i):
                yield ("op", op, line, False)
                i += len(op)
                break
        else:
            yield ("op", c, line, False)
            i += 1


def lint(path):
    raw = open(path, "rb").read()
    msgs = []
    for ln, bline in enumerate(raw.split(b"\n"), 1):
        if any(b > 127 for b in bline):
            msgs.append((ln, "ERROR", "non-ASCII bytes"))
    src = raw.decode("latin-1")
    toks = list(tokenize(src))
    depth_fn = 0          # function nesting (rough: function ... end with block keywords)
    block_stack = []
    in_params = False
    prev = None
    top_lines = set()
    for k, (kind, text, line, leveled) in enumerate(toks):
        if kind in ("str", "comment") and leveled:
            msgs.append((line, "ERROR", "leveled long bracket [=[ (5.1+)"))
        if kind == "str" and PATH_RE.search(text):
            msgs.append((line, "WARN", "string looks like a file path: " + text[:60]))
        if kind == "comment":
            continue
        if kind == "name":
            if text in KEYWORDS_BAD:
                msgs.append((line, "ERROR", KEYWORDS_BAD[text]))
            if text == "function":
                block_stack.append("function")
                depth_fn += 1
                # parameter list starts at the next '('
                in_params = "pending"
            elif text in ("do", "then", "repeat"):
                if text == "do" and prev and prev[1] in ("while", "for"):
                    pass
                block_stack.append(text)
            elif text in ("end", "until"):
                if block_stack:
                    top = block_stack.pop()
                    if top == "function":
                        depth_fn -= 1
            elif text in ("elseif",):
                # 'elseif ... then' pushes again on 'then'; drop the previous 'then'
                if block_stack and block_stack[-1] == "then":
                    block_stack.pop()
        if kind == "op":
            if text == "(" and in_params == "pending":
                in_params = True
            elif text == ")" and in_params is True:
                in_params = False
            elif text == "#":
                msgs.append((line, "ERROR", "'#' length operator (5.1+): use table.getn / string.len"))
            elif text == "%":
                msgs.append((line, "ERROR", "'%' operator (5.1+): use math.mod"))
            elif text == "//":
                msgs.append((line, "ERROR", "'//' floor division (5.3+)"))
            elif text == "::":
                msgs.append((line, "ERROR", "'::label::' (5.2+)"))
            elif text in ("&", "|", "<<", ">>"):
                msgs.append((line, "ERROR", f"bitwise operator '{text}' (5.3+)"))
            elif text == "~":
                msgs.append((line, "ERROR", "unary '~' (5.3+)"))
            elif text == "...":
                if in_params is not True:
                    msgs.append((line, "WARN", "'...' outside a parameter list: Lua 5.0 uses the 'arg' table"))
            elif text == ":" and prev and prev[0] == "op" and prev[1] == ")" and k >= 2 and toks[k - 2][0] == "str":
                msgs.append((line, "WARN", "method call on a string literal (no string metatable in 5.0)"))
        if depth_fn == 0 and kind != "comment":
            top_lines.add(line)
        prev = (kind, text)
    msgs.sort()
    for ln, level, msg in msgs:
        print(f"{path}:{ln}: {level}: {msg}")
    print(f"{path}: INFO: ~{len(top_lines)} lines of top-level (main chunk) code; wrap big sections in functions "
          f"before precompiling (see ai_port.md 6)")
    return any(level == "ERROR" for _, level, _ in msgs)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    bad = False
    for p in argv:
        bad |= lint(p)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
