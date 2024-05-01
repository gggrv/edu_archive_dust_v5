# Educational Archive for "dust v5"

*Please note, that this project is obsolete, and is no longer maintained. No additional documentation will be released. No additional installation support will be provided*.

*Please note, that the artifacts of this project were used as a basis for several other projects. These new projects address, extend, enhance and fix any issues this project may have had. Please see the dedicated repositories for necessary information*.

## What is This

| Item | Description |
| ------------- | ------------- |
| What is this? | A project, saved into `git` repository, hosted at `GitHub` website. |
| What does it contain? | It contains a set of pre-alpha `python` tools. |
| Whom are they for? | For beginner python developers. |
| What is the current project status? | Archived, obsolete, no longer maintained. |
| Why is it obsolete? | Because the complex multipurpose multi-license code, developed here, is more useful, when reorganized and split into several other independent projects. |
| What is the purpose of this repository? | Host an educational archive with working code. |
| Why is it named like that? | Inspired by the real-world dust --- it is small (see `followindow`), floats in air (see `followindow`), present everywhere (see `HostApp.py`), hard to get rid of (see `GuiLogHandler` class and `ExceptionViewer.py`), beautifully sparkles in the sun (the only positive property). |

## Available Tools

The python tools, available in this project, are abstract enough to be used independently. They are organized into convenient subfolders with different `.py` source code flies. Additionally, for educational purposes, they are combined into the PyQt5 demo app, named `grimoire`.

Please see the hierarchy of the python subpackages:

```
■─host.pyw (demo app launcher)
■─sparkling (top-level namespace)
  ├─■ common (context-unaware helper classes, functions, usable anywhere)
  ├─■ contech (tools for ConTeXt word processor)
  ├─■ followindow (PyQt5 window that follows mouse cursor)
  ├─■ grimoire (demo app source code)
  ├─■ host_app (demo app launcher source code)
  ├─■ neo4j (tools for Neo4J database)
  └─■ path_eater (obsolete unused PyQt5 widget)
```

## Demo App

The demo application, which combines all the tools in this package, is named `grimoire`, and can be launched via the top-level `host.pyw` python file.

| Item | Description |
| ------------- | ------------- |
| What is this? | A python application with `Graphical User Interface`. |
| How is it made? | With `PyQt5` library. |
| What does it do? | It allows the user to create metadata for anything (files, photos, folders, web links, ...) and to automatically move local files into appropriate subfolders according to given metadata. |
| How does it work? | <ol><li>The developer installs a [Neo4J desktop server](https://neo4j.com/download/) (and creates a local database, user credentials, etc).</li><li>The developer starts the `host.pyw` file.</li><li>The developer sees a small dark gray pixel (`followindow`), following his mouse cursor.</li><li>The developer hovers the small grey pixel with his mouse cursor.</li><li>The small grey pixel becomes a large grey square.</li><li>The developer inputs a mouse gesture in this square (for example, swipe down while holding the right mouse button).</li><li>The `grimoire/pyqt5/MainWindow.py` is initialized.</li><li>Optionally, the developer is asked to add the link to the Neo4J server and user credentials to the auto-generated `data/grimoire/neo4j_settings.yaml` file.</li><li>The next time an appropriate mouse gesture is given to `followindow`, the developer will see a `gmiroire/pyqt5/MainWindow.py` widget and will be able to use the app.</li><li>At any point in time the developer can access the small yellow `tray icon` in the system tray. Right-clickling it will open a dedicated context menu with some default actions.</li></ol> |
| Why is it named like this? | Inspired by the word "grimoire" --- an old ugly dusty book with lots of mysterious information (can host metadata) and unknown unstable magical properties (see `followindow` and `data/grimoire/plugins` subfolder). |

### Purpose

This is a highly experimental GUI demo app that allowed the developer to learn the basics of the `Qt` library via python. Additionally, it acted as a stress-test for the underlying abstract python tools, software project structure and project management approaches.

### Dependencies

```
fundamental A:
  pandas v. 1.3.5
  numpy
  pyyaml

fundamental B:
  pyqt5
  neo4j

important:
  moosegesture
  pyautogui
```

## License

To reiterate what was stated above, this project, named "dust v5", contains:
- Pre-alpha python tools for general python development (mostly 0BSD)
- Pre-alpha python tools for `PyQt5` (GPL v3)
- Pre-alpha python tools for `Neo4J` (GPL v3)
- Pre-alpha python tools for `ConTeXt` (mostly 0BSD)
- Pre-alpha demo app, written in `PyQt5` (GPL v3).

Each of these require different licenses.  
The actual licenses are available at the beginning of each source code file.  
Any other file is implied to be subject to 0BSD.
