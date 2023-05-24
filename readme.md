# dust

Work in progress.

GUI python application made with `PyQt5`. Resides in system icon tray. Allows to launch any other python/???/custom applications. Comes with the following extensions:
- `followindow`
- `grimoire`

Requires a `data` subfolder to function properly.

### Links

Development progress: [click](https://gggrv.github.io/something/2022/05/17/devinfo-dust/#development-status).  
Documentation: `to be added`.

## Architecture

root folder  
→ `host_app`  
→→ reusable common tools  
→→ various user-defined `extensions`   
→ `data` folder  
→→ all `extensions` can save items here

## Extensions

### `followindow`

Appears as a large pixel near mouse cursor. Follows mouse cursor while the user naturally moves it across the screen, can receive mouse gestures, expands to a much larger pixel on hover. Can be toggled on and off from system tray menu or via gesture.

Primary use: receive mouse gestures and launch custom python scripts / other programs.

### `grimoire`

Allows to create custom personal metadata for web links, paths to local files, nothing in particular. Saves that custom personal metadata on the user's `neo4j` server (it needs to be set up separately). Similarly to `foobar2000` music player, allows the user to browse all databases on the `neo4j` server as if it was a giant partitioned music library. Can remember chosen `nodes` into `playlists`. Allows to edit metadata, rename (move) files on disk (according to metadata fields), delete files from disk, quickly open files/links (launches corresponding system program: `.docx` → MS Word, folder → system file explorer, etc). Each `playlist` can run custom `python` `plugins` that provide unique context menus and underlying functionality (user-customizeable, work in progress).

Primary use: keep custom personal metadata of physical files and quickly sort them to subfolders according to personal rules.

# end of document
