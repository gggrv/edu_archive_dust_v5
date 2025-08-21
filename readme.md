# Educational Archive "Dust v5"

*Note: This project is archived and no longer maintained. No additional documentation or installation support will be provided.*

*The components of this project have been used as a foundation for several newer projects that address, extend, and enhance parts of its functionality. Please refer to their respective repositories for newer information.*

*This readme document was optimised with AI*.

<p style="text-align:right;"><a href="https://gggrv.github.io/something/2022/05/17/devinfo-dust/">Homepage for "Dust"</a> | <a href="https://gggrv.github.io/something/2024/12/09/devinfo-grimoire/">Homepage for "Grimoire"</a></p>

## What is This

| Item | Description |
| ------------- | ------------- |
| What is this? | A GitHub repository containing Python tools and two-in-one demo applications. |
| Contents | - Abstract Python tools<br>- Demo GUI applications:<br>  - "Dust" (small and simple).<br>  - "Grimoire" (large and complex). |
| Target Audience | Beginner Python and Qt developers |
| Project Status | ✔️ Functional and archived<br>😴 No longer maintained |
| Purpose | Educational archive with working code examples |
| Name Origin | - "Dust" refers to its small, floating nature (see `followindow`).<br>- "Grimoire" refers to its ugly, complex, metadata-rich nature. |

## Structure

```
■ host.pyw (demo application launcher)
■ sparkling (main package)
  ├─■ common (general-purpose helper classes and functions)
  ├─■ contech (ConTeXt word processor tools)
  ├─■ followindow (Dust program - simple PyQt5 application)
  ├─■ grimoire (Grimoire program - complex PyQt5 application)
  ├─■ host_app (launcher source code)
  ├─■ neo4j (Neo4J database tools)
  └─■ path_eater (deprecated PyQt5 widget)
```

## Installation

This project is best used with [Visual Studio Code](https://code.visualstudio.com) (VS Code).

1. Clone this repository
2. Open the folder in VS Code
3. Set up Python environment:
   - Create virtual environment: `python -m venv .virtual_env`
   - Select the interpreter: VS Code Command Palette → "Python: Select Interpreter" → Enter path
4. Install dependencies:
   ```
   pip install setuptools
   pip install -r requirements.txt
   ```

For the basic features (Dust program), this is all you need.

For the advanced features (Grimoire program), also:
1. Install [Neo4J Desktop Server](https://neo4j.com/download/)
2. Set up a local database with appropriate credentials

## Usage

1. Run `host.pyw` through VS Code (recommended for first run to catch any setup issues)
2. The Dust program starts automatically
3. Use Dust to launch Grimoire when needed
4. Explore both applications' features

### Dust Program

A system tray icon (<img src="data/host_qtapp/tray.png" width="15px" alt="Tray icon">) provides access to the program. Right-click for available actions.

#### Demo Videos

| Function | Usage |
|--|--|
| <ul><li>Launch</li><li>Hover</li><li>Input correct gesture</li><li>Encounter errors</li></ul> | *If the video does not render, please see `docs/followindow_errors.mp4`*<br><video width="320" height="240" controls><source src="docs/followindow_errors.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Input unknown gesture</li></ul> | *If the video does not render, please see `docs/followindow_help.mp4`*<br><video width="320" height="240" controls><source src="docs/followindow_help.mp4" type="video/mp4" alt="Video"></video> |

### Grimoire Program

To launch: In Dust, hover over the grey pixel and swipe down with the right mouse button.

First launch:
- Creates and opens `data/grimoire/neo4j_settings.yaml`
- Enter your Neo4J server credentials

On the subsequent launches, the `grimoire/pyqt5/MainWindow.py` widget will be shown.

#### Demo Videos

| Function | Usage |
|--|--|
| <ul><li>Launch</li><li>Create one new "playlist"</li></ul> | *If the video does not render, please see `docs/grimoire_new_playlist.mp4`*<br><video width="320" height="240" controls><source src="docs/grimoire_new_playlist.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Edit multiple items</li><li>Encounter errors</li></ul> | *If the video does not render, please see `docs/grimoire_edit_multiple_simple.mp4`*<br><video width="320" height="240" controls><source src="docs/grimoire_edit_multiple_simple.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>`auto_query` VS manual "playlist" content editing</li><li>`parsing line`</li><li>`FileRenamer`</li></ul> | *If the video does not render, please see `docs/grimoire_edit_complex.mp4`*<br><video width="320" height="240" controls><source src="docs/grimoire_edit_complex.mp4" type="video/mp4" alt="Video"></video> |
| <ul><li>Add/remove `plugins`</li></ul> | <ol><li>Start editing the "playlist"</li><li>Create reserved field named `plugins`</li><li>Add/remove your plugin name as value</li><li>Save changes, close the editor</li><li>Open the "playlist"</li><li>Right-click to see context menus</li><li>See your plugin functionality in the context menu.</li></ol> |

### Purpose

This is a highly experimental GUI demo app that allowed the developer to learn the basics of the `Qt` library via python. Additionally, it acted as a stress-test for the underlying abstract python tools, software project structure and project management approaches.

## Licenses

License details are provided in each source file. Overview:
- General Python tools: 0BSD
- PyQt5-related tools: GPL v3
- Neo4J tools: GPL v3
- ConTeXt tools: 0BSD
- Demo applications: GPL v3
- All other files: implied 0BSD
