# ubisoft-achievement-fixer

A small Python script to **fix bugged achievements** in Ubisoft Connect's local achievement files (`.spool`).

Sometimes a game doesn't unlock an achievement you clearly earned. A sequence gets skipped after a connection drop, or a challenge never triggers. Ubisoft Connect keeps your unlocked achievements in a small local file, and this tool lets you add the missing entry to it.

Tested on **Assassin's Creed III Remastered**: three bugged achievements (Sequence 7, Sequence 8, and the Jäger notoriety challenge) unlocked after adding them.

> **Only use this for achievements you actually earned.** This is an unofficial tool, not affiliated with or supported by Ubisoft. Use at your own risk, and always keep a backup.

## Requirements

- [Python 3.8+](https://www.python.org/downloads/). No extra packages needed.

## Where the files are

```
%LOCALAPPDATA%\Ubisoft Game Launcher\spool\<your account ID>\<game ID>.spool
```

Each game has its own file, named after its Ubisoft game ID. For example:

| Game | File |
|---|---|
| Assassin's Creed III Remastered | `5184.spool` |

## Usage

1. Download `spool_tool.py` into any folder, for example `Desktop\spool_fix\`.
2. **Double-click `spool_tool.py`.** (If it opens in a text editor instead: right-click → Open with → Python.)
3. Pick the game if asked, then type the achievement numbers to add, for example `41 42 70`, and press Enter.
4. **Close Ubisoft Connect completely**, including the tray icon.
5. Copy the new `5184.spool` from the script's folder into the spool folder and choose **Replace**. The script opens the folder for you; if it doesn't, paste `%LOCALAPPDATA%\Ubisoft Game Launcher\spool` into the File Explorer address bar and open the folder inside it (named after your Ubisoft account ID).
6. Start Ubisoft Connect **while online**, launch the game, and check that the achievements appeared.

**The script never changes or replaces any existing file.** It reads your achievement file and creates two new files next to the script:

- `5184.spool`: your achievements plus the new ones, ready to copy in
- `5184_original.spool`: an untouched copy of your current file

It skips numbers you already have, and it won't create anything from a file that doesn't look like a valid achievement file. If files with those names are already next to the script, it stops instead of overwriting them.

**Double-check the numbers before step 5.** Once Ubisoft Connect syncs an achievement, it most likely can't be removed again.

**To restore your original file:** close Ubisoft Connect, rename `5184_original.spool` to `5184.spool`, and copy it into the spool folder. This only helps before Ubisoft Connect has synced; it doesn't remove achievements that already unlocked.

## Achievement IDs

The file only stores numbers, not names. For AC3 Remastered, find the achievement on [SteamDB](https://steamdb.info/app/911400/stats/) and use the number at the end of its API name, for example `AC3Remaster_Ach_41` → `41`.

### Assassin's Creed III Remastered (5184) – confirmed examples

| ID | Achievement |
|---|---|
| 40 | Complete Sequence 6 |
| 41 | Complete Sequence 7 |
| 42 | Complete Sequence 8 |
| 43 | Complete Sequence 9 |
| 70 | After becoming fully Notorious, kill 10 Jägers before losing your notoriety |


## File format

A `.spool` file is a plain [protobuf](https://protobuf.dev/programming-guides/encoding/) message. It has no header and no checksum, just one entry per unlocked achievement:

```proto
message SpoolFile {
  repeated Entry entries = 1;
}
message Entry {
  AchievementKey key = 1;
  uint64 unlocked_at = 2;   // Unix time, seconds, UTC
}
message AchievementKey {
  uint32 id = 1;            // Ubisoft achievement ID
}
```

(Field names are made up. Protobuf only stores field numbers.)

One entry, byte by byte:

```
0a 0a  0a 02 08 1f  10 d8 f2 87 d8 06
│  │   │  │  │  │   │  └─ timestamp varint (2026-11-21 20:04:40 UTC)
│  │   │  │  │  │   └─ field 2, varint
│  │   │  │  │  └─ ID 31
│  │   │  │  └─ field 1, varint
│  │   │  └─ key length 2
│  │   └─ field 1 (key), length-delimited
│  └─ entry length 10
└─ field 1 (entry), length-delimited
```

You can inspect any file with `protoc --decode_raw < 5184.spool`.

## Troubleshooting

- **"doesn't look like a normal achievement file"**: the file is damaged or a different format, so it was left alone. To send a spool file to someone, zip it first, because some upload paths corrupt binary files.
- **"No achievement files found"**: play the game at least once through Ubisoft Connect so the file exists.
- **"These files already exist"**: move or delete the old `5184.spool` and `5184_original.spool` next to the script, then run it again.
- **Achievements didn't appear**: Ubisoft Connect was probably still running when you copied the file. Close it fully and copy the file again.

## Other games

The file format appears to be the same for every game in the spool folder, and the script lets you pick any of them. It has only been tested on AC3 Remastered, and the achievement numbers differ for every game. If you get it working for another game, please [open an issue](../../issues) with the game and the numbers you used.

## License

[MIT](LICENSE)
