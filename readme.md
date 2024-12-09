# Educational Archive "Dust v5"

*Please note, that this project is obsolete, and is no longer maintained. No additional documentation will be released. No additional installation support will be provided*.

*Please note, that the artifacts of this project were used as a basis for several other projects. These new projects address, extend, enhance and fix any issues this project may have had. Please see the dedicated repositories for necessary information*.

## What is This

| Item | Description |
| ------------- | ------------- |
| What is this? | A project, saved into `git` repository, hosted at `GitHub` website. |
| What does it contain? | <ul><li>Several abstract `python` tools.</li><li>Demo app with graphical user interface:<ul><li>Contains `small and simple program` named "Dust"</li><li>And `big and complex program` named "Grimoire"</li></ul></li></ul> |
| Whom are they for? | For beginner `python`+`Qt` developers. |
| What is the current project status? | <ul><li>✔️Functional.</li><li>😴Archived, outdated, no longer maintained.</li></ul> |
| Why is it obsolete? | Because the complex multipurpose multi-license code, developed here, is more useful, when reorganized, simplified and split into several other independent projects. |
| What is the purpose of this repository? | Host an educational archive with working code. |
| Why is it named like that? | `small and simple program` name was inspired by the real-world dust:<ol><li>It is small (see `followindow`),</li><li>Floats in air (see `followindow`),</li><li>Present everywhere (see `HostApp.py`),</li><li>Hard to get rid of (see `GuiLogHandler` class and `ExceptionViewer.py`),</li><li>Beautifully sparkles in the sun (the only positive property).</li></ol><br> `big and complex program` name was inspired by the word "grimoire":<ol><li>An old and ugly dusty book (it *is* old and ugly)</li><li>With lots of mysterious information (can host metadata)</li><li>And unknown unstable magical properties (see `data/grimoire/plugins` subfolder).</li></ol> |

## Structure

```
■─host.pyw (demo app launcher)
■─sparkling (top-level namespace)
  ├─■ common (context-unaware helper classes, functions, usable anywhere)
  ├─■ contech (tools for ConTeXt word processor)
  ├─■ followindow (small and simple PyQt5 program)
  ├─■ grimoire (big and complex PyQt5 program)
  ├─■ host_app (source code of the demo app launcher)
  ├─■ neo4j (tools for Neo4J database)
  └─■ path_eater (obsolete unused PyQt5 widget)
```

## Installation

For the best experience, please use the specific version of the `Spyder` python IDE. It can be installed via `pip install spyder==5.5.6` command.

<ol>
<li>Clone this repository in a directory of choice.</li>
<li>Navigate to this directory.</li>
<li>Follow <a href="https://medium.com/analytics-vidhya/5-steps-setup-python-virtual-environment-in-spyder-ide-da151bafa337">this manual</a> in order to:<ol><li>Create the virtual environment,</li><li>Activate this virtual environment,</li><li>Make the <code>Spyder</code> work in this virtual environment.</li></ol></li>
<li>Install the setuptools via the command <code>pip install setuptools</code> into this virtual environment.</li>
<li>Install the dependencies, listed in the <code>requirements.txt</code>, into this virtual environment.</li>
<li>In <code>Spyder</code>, open the menu option "Projects"->"New Project...", select "Existing directory", set "Location" to the dir of the cloned repository and click "Create".</li>
<li>Open the menu option "Tools"->"Preferences", select "Run", set "Working directory settings" to "The current working directory" option.</li>
<li>Make sure that current working dir is the cloned repository dir.</li>
</ol>

After completing these instructions, the user will be able to use this repository to:
1. Launch and exlore the `small and simple` part of the demo app.
2. Inspect the underlying abstract python tools.

In order to use the `big and complex` part of this demo app, several additional steps must be completed:
1. Install the [Neo4J desktop server](https://neo4j.com/download/) (click to open).
2. Create a local database, user credentials, etc.

## Demo App Usage

The event sequence is as follows:
1. The user runs the `host.pyw` file (although it can be launched directly from the file explorer with the doubleclick, it is recommended to run it via `IDE` at least on the first try — this way the developer will be able to see if any depencencies have failed to set up correctly).
2. The `small and simple` program is automatically started.
3. The user may use this `small and simple program` to launch the `big and complex program`.
4. The user actually uses the `small and simple program` to launch the `big and complex program`.
5. The user explores the `big and complex program` to their leisure.
6. The user decides to modify something.
7. ???
8. Profit.

### More on the `small and simple program`

At any point in time the developer can access the small `system tray icon` that looks as follows: <img src="data/host_qtapp/tray.png" width="15px" alt="Image of the tray icon">. Right-clickling it will open a dedicated context menu with some default actions.

| Function | Usage |
|--|--|
| <ul><li>Launch</li><li>Hover</li><li>Input correct gesture</li><li>Encounter errors</li></ul> | <video width="320" height="240" controls><source src="docs/followindow_errors.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Input unknown gesture</li></ul> | <video width="320" height="240" controls><source src="docs/followindow_help.mp4" type="video/mp4" alt="Video"></video> |


### More on the `big and complex program`

In order to launch it from the `small and simple program`, hover the grey pixel and swipe down while holding the right mouse button.

On the first ever launch, the following file will be created and opened automatically: `data/grimoire/neo4j_settings.yaml`. The user is expected to provide valid server credentials.  
After this, on the subsequent launches, the `grimoire/pyqt5/MainWindow.py` widget will be shown.

| Function | Demonstration |
|--|--|
| <ul><li>Launch</li><li>Create one new "playlist"</li></ul> | <video width="320" height="240" controls><source src="docs/grimoire_new_playlist.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Edit multiple items</li><li>Encounter errors</li></ul> | <video width="320" height="240" controls><source src="docs/grimoire_edit_multiple_simple.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>`auto_query` VS manual "playlist" content editing</li><li>`parsing line`</li><li>`FileRenamer`</li></ul> | <video width="320" height="240" controls><source src="docs/grimoire_edit_complex.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Add/remove `plugins`</li></ul> | <ol><li>Start editing the "playlist"</li><li>Create reserved field named `plugins`</li><li>Add/remove your plugin name as value</li><li>Save changes, close the editor</li><li>Open the "playlist"</li><li>Right-click to see context menus</li><li>See your plugin functionality in the context menu.</li></ol> |

### Purpose

This is a highly experimental GUI demo app that allowed the developer to learn the basics of the `Qt` library via python. Additionally, it acted as a stress-test for the underlying abstract python tools, software project structure and project management approaches.

More information could be found at the following links:  
[[Dev Info] Dust](https://gggrv.github.io/something/2022/05/17/devinfo-dust/) (click to open) — detailed information regarding the `small and simple program` and its future.  
[[Dev Info] Grimoire](https://gggrv.github.io/something/2024/12/09/devinfo-grimoire/) (click to open) — detailed information regarding the `big and complex program` and its future.

## License <a name="license"></a>

The actual licenses are available at the beginning of each source code file; superficial overview:
- Abstract python tools for general python development are generally subject to 0BSD.
- Abstract python tools for `PyQt5` are generally subject to GPL v3.
- Abstract python tools for `Neo4J` are generally subject to GPL v3.
- Abstract python tools for `ConTeXt` are generally subject to 0BSD.
- The `PyQt5` demo app is generally subject to GPL v3.

Any other file is implied to be subject to 0BSD.
