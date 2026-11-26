#!/usr/bin/env python3
"""Ubisoft Connect achievement fixer.

Double-click this file (Windows, Python 3.8+). It reads your achievement file,
shows what you already have, and writes a NEW file with the numbers you type in
next to this script. It never changes or replaces any existing file.
"""
import os, sys, glob, shutil, datetime as dt

SPOOL = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ubisoft Game Launcher", "spool")
HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
GAMES = {"5184": "Assassin's Creed III Remastered"}


def varint(v):
    out = bytearray()
    while True:
        b, v = v & 0x7F, v >> 7
        out.append(b | 0x80 if v else b)
        if not v:
            return bytes(out)


def read_varint(b, i):
    v = s = 0
    while True:
        v |= (b[i] & 0x7F) << s
        s += 7
        i += 1
        if b[i - 1] < 0x80:
            return v, i


def load(path):
    b, i, entries = open(path, "rb").read(), 0, []
    while i < len(b):
        n = b[i + 1]
        rec = b[i + 2:i + 2 + n]
        i += 2 + n
        aid, j = read_varint(rec, 3)
        t, _ = read_varint(rec, j + 1)
        entries.append((aid, t))
    return entries


def encode(entries):
    data = b""
    for aid, t in entries:
        key = b"\x08" + varint(aid)
        inner = b"\x0a" + bytes([len(key)]) + key + b"\x10" + varint(t)
        data += b"\x0a" + bytes([len(inner)]) + inner
    return data


def save(path, entries):
    # Ubisoft keeps entries in unlock order
    open(path, "wb").write(encode(sorted(entries, key=lambda e: e[1])))


def pick(files):
    print("Achievement files found:\n")
    for n, f in enumerate(files, 1):
        gid = os.path.splitext(os.path.basename(f))[0]
        print(f"  {n}. {gid}  {GAMES.get(gid, '')}")
    while True:
        choice = input("\nWhich one? Type its number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]


def main():
    print("=== Ubisoft Connect achievement fixer ===\n")
    files = sorted(glob.glob(os.path.join(SPOOL, "*", "*.spool")))
    if not files:
        print(f"No achievement files found in:\n  {SPOOL}\nPlay the game once with Ubisoft Connect first.")
        return
    path = files[0] if len(files) == 1 else pick(files)

    try:
        entries = load(path)
        ok = encode(entries) == open(path, "rb").read()
    except (IndexError, ValueError):
        ok = False
    if not ok:
        print("\nThis file doesn't look like a normal achievement file. Nothing was created.")
        return
    have = sorted(a for a, _ in entries)
    print(f"\nYou have {len(have)} achievements: {' '.join(map(str, have))}")

    gid = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(HERE, f"{gid}.spool")
    original = os.path.join(HERE, f"{gid}_original.spool")
    taken = [f for f in (out, original) if os.path.exists(f)]
    if taken:
        print("\nThese files already exist next to the script, and they won't be replaced:")
        for f in taken:
            print(f"  {f}")
        print("Move or delete them, then run the script again.")
        return

    typed = input("\nType the achievement numbers to add, separated by spaces (e.g. 41 42 70): ")
    wanted = [int(x) for x in typed.replace(",", " ").split() if x.isdigit()]
    new = [a for a in dict.fromkeys(wanted) if a not in have]
    if not new:
        print("Nothing to add.")
        return

    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    shutil.copy2(path, original)
    save(out, entries + [(a, now + k) for k, a in enumerate(new)])

    print(f"\nAdded: {' '.join(map(str, new))}")
    print(f"\nCreated next to this script:\n  {out}   <- new file\n  {original}   <- backup of your current file")
    print("\nNext:\n  1. Close Ubisoft Connect completely (also the tray icon).")
    print(f"  2. Copy the new {gid}.spool into this folder and choose 'Replace':\n     {os.path.dirname(path)}")
    print("  3. Start Ubisoft Connect (online) and launch the game.")
    if os.name == "nt":
        os.startfile(os.path.dirname(path))  # opens the folder for step 2


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nSomething went wrong: {e}\nYour Ubisoft files were not changed.")
    input("\nPress Enter to close...")
