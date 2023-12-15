# dust v5 (legacy version)

This version is obsolete and is no longer maintained. Please see another repository for the up-to-date version.

GUI python application made with `PyQt5`. Resides in system icon tray. Allows to launch any other python/???/custom applications. Comes with the following optional `subpackages`:
- `contech`
- `followindow`
- `grimoire`

Requires a `data` subfolder to function properly. This `data` folder is created/managed automatically.

Development progress: [click](https://gggrv.github.io/something/2022/05/17/devinfo-dust/#development-status).  
Documentation: `to be added`.

## Architecture

### Folder structure

```
■ application folder
├─■ data folder
├─> host.pyw (entry point)
└─■ sparkling (top-level package)
  ├─■ common
  ├─■ contech
  ├─■ followindow
  ├─■ host_app
  └─■ grimoire
```

## Optional subpackages

### `followindow`

Appears as a large pixel near mouse cursor. Follows mouse cursor while the user naturally moves it across the screen, can receive mouse gestures, expands to a much larger pixel on hover. Can be toggled on and off from system tray menu or via gesture.

Primary use: receive mouse gestures and launch custom python scripts / other programs.

### `grimoire`

Allows to edit and organise custom metadata for web links, paths to local files, nothing in particular. Saves that custom metadata on the user's `neo4j` server (it needs to be set up separately) as individual `nodes`. Similarly to `foobar2000` music player, allows the user to browse all databases on the [Neo4j](https://neo4j.com/download/) server as if it was a giant partitioned music library. Can remember chosen `nodes` into `playlists`. Allows to edit metadata, rename files on disk (according to metadata fields), delete files from disk, quickly open files/links (launches corresponding system program: `.docx` → MS Word, folder → system file explorer, etc). Each `playlist` can run custom `python` `plugins` that provide user-defined context menu options and functionality.

Primary use: keep custom metadata of physical files and quickly sort them to subfolders according to user-defined rules.

### `contech`

A collection of tools that allow to easily manage typesetting projects powered by [ConTeXt](https://wiki.contextgarden.net/Main_Page) (it needs to be installed separately).

Primary use: track, navigate and print projects using `grimoire`.

end of document
