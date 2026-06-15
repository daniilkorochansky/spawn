![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Language](https://img.shields.io/badge/language-Python-yellow.svg)
![Tests](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml/badge.svg)
![Coverage](https://raw.githubusercontent.com/daniilkorochansky/spawn/master/coverage.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

<div align="center">
  [English
  /
  <a href="https://github.com/daniilkorochansky/spawn/blob/master/README_ru.md">Русский</a>]
</div>

# Spawn
<img width="180" height="180" alt="spawn_new" src="https://github.com/user-attachments/assets/18435694-229c-468d-87af-11f9ed4d243e" />

A fast and modern development environment (IDE), created specifically for developing open.mp and SA-MP servers, in the Pawn programming language.

It combines Pawn editing, SAMPCTL integration, dependency management, Git version control, and project navigation tools into a single development environment designed around the needs of multiplayer server developers.

Portable, extensible, and focused on productivity, Spawn helps you build, manage and maintain Pawn projects without relying on generic code editors.

## Overview
<img width="1920" height="1049" alt="ui" src="https://github.com/user-attachments/assets/505d6a46-33cc-45ae-bed3-f011474a4dc7" />

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
  - [Project Creation](#project-creation)
  - [Split Code Editor View](#split-code-editor-view)
  - [RGBA/HEX Color Preview](#rgbahex-color-preview)
  - [Dependency Manager](#dependency-manager)
  - [Git and Source Control](#git-and-source-control)
  - [Project Tree](#project-tree)
- [Installation](#installation)
  - [Download](#download)
  - [Optional Tools](#optional-tools)
- [Quick Start](#quick-start)
  - [Create a Project](#create-a-project)
  - [Manage Dependencies](#manage-dependencies)
  - [Build and Run Server](#build-and-run-server)
  - [Working with Individual Files](#working-with-individual-files)
  - [Encoding Detection](#encoding-detection)
- [Development](#development)
  - [Requirements](#requirements)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Run](#run)
  - [Build Executable (Windows)](#build-executable-windows)
  - [Tests](#tests)
- [Stability](#stability)
- [Contributors](#contributors)
  - [Bug Report](#bug-report)
- [Donations](#donations)
- [License](#license)

## Features
+ Designed specifically for [open.mp](https://github.com/openmultiplayer) & SA-MP development.
+ Built-in [SAMPCTL](https://github.com/Southclaws/sampctl) integration for building, running and managing projects.
+ Dependency Manager for easy installation and updating of server packages and components.
+ Integrated Git support with repository status indicators and commit history.
+ Change History markers for tracking modified and saved lines.
+ Automatic brace matching and highlighting.
+ Color preview for RGBA and HEX values directly inside the editor.
+ Color Picker integration for quick color insertion into Pawn code.
+ Split Code Editor mode for working with multiple files simultaneously.
+ Project Tree optimized for large projects.
+ Integrated build output and server console panels.
+ Automatic project files monitoring and refresh.
+ Portable distribution (no installation required).

## Screenshots
### Project Creation
<img width="1920" height="1080" alt="Project Creation" src="https://github.com/user-attachments/assets/14b70c29-96b4-4d7d-94ff-6307cfa35cac" />

### Split Code Editor View
<img width="1920" height="1080" alt="Split Code Editor" src="https://github.com/user-attachments/assets/f0caa6e9-607b-48f1-8b58-ae95ef12f7b1" />

### RGBA/HEX Color Preview
<img width="1920" height="1080" alt="Color Preview" src="https://github.com/user-attachments/assets/ae6a367a-3b04-4a23-a6ad-71ae51b0edc8" />

### Dependency Manager
<img width="1920" height="1080" alt="Dependency Manager" src="https://github.com/user-attachments/assets/e60a1bad-9a9d-43da-938d-fa94d43401b7" />

### Git and Source Control
<img width="1920" height="1080" alt="Git and Source Control" src="https://github.com/user-attachments/assets/b6198ac3-97b4-4392-b29a-87ab6bdfc818" />

### Project Tree
<img width="1920" height="1080" alt="Project Tree" src="https://github.com/user-attachments/assets/c942516b-6e18-406d-b9be-cb8e24d54a94" />

## Installation
### Download
1. Download the latest release from the Releases page.
2. Extract the archive to any location
3. Run 'Spawn.exe'.

### Optional Tools
To use all features of Spawn, you may also install:
+ Git
+ [SAMPCTL](https://github.com/Southclaws/sampctl)

These tools can be configured later in Settings.

## Quick Start
### Create a Project
1. Select 'File' → 'New Project...'.
2. Enter project name and choose a project location.
3. After clicking 'Create', the SAMPCTL command-line tool will be launched. Follow the on-screen instructions to complete project creation.
4. Once the process is complete, close the SAMPCTL command-line tool. Spawn will pick up the new project.

### Manage Dependencies
1. Select 'Project' → 'Dependency Manager...'.
2. Enter the package name in the 'Dependency' field
3. Click 'Install'.

+ To uninstall a dependency, select the one you want from the list and click 'Uninstall'.
+ To verify that all dependencies are in order, click the button labeled 'Ensure'.

### Use Git
1. Right-click the root folder in the Project Tree → choose 'Initialize Repository'. (If the repository wasn't on the server)
2. Create your first commit.
3. Track changes directly from the IDE.

If the repository is already on the server, Spawn will automatically detect it (provided Git is enabled in the settings)

### Build and Run Server
1. Open the root folder containing the server by selecting 'File' → 'Open Server Folder...' (The server must contain the 'pawn.json' file generated via [SAMPCTL](https://github.com/Southclaws/sampctl))
2. Go to 'Build' → 'Build Server' or click the corresponding button on the toolbar.
3. Start your server by going to 'Server' → 'Run / Stop Server' or by clicking the corresponding button on the toolbar.
4. Monitor output in the integrated console.

You're ready to develop open.mp and SA-MP servers with Spawn.

### Working with Individual Files
Spawn can also be used without opening a project.

To edit a single file:
1. Select 'File' → 'Open File...'.
2. Choose a Pawn source file, include file, or configuration file.
3. Start editing immediately.

When working with individual files, editor features such as syntax highlighting, color previews, brace matching, split view, and change history markers remain fully available.

Project-specific functionality such as the Project Tree, Git integration, Dependency Manager, and SAMPCTL tools requires an opened project.

### Encoding Detection
Spawn automatically detects file encoding when opening files.

In some cases, automatic detection of Windows-1251 (CP1251) may be inaccurate.

If a file is displayed incorrectly, you can reopen it using a different encoding:
Select in 'Edit' → 'Encoding' → 'Reopen'

Supported encodings include:
+ UTF-8
+ Windows-1251 (CP1251)

*This does not modify the file on disk and only affects how the file is displayed in the editor.*

## Development
### Requirements
+ Python 3.12+
+ wxPython
+ GitPython
+ Markdown
+ watchdog

### Clone the Repository
```
https://github.com/daniilkorochansky/spawn.git
```
or
```bash
gh repo clone daniilkorochansky/spawn
```

### Install Dependencies
In the root folder, run:
```bash
pip install -r requirements.txt
```
### Run
Also in the root folder, run:
```bash
python main.py
```

### Build Executable (Windows)
Spawn uses Nuitka to create standalone executable builds.

1. Install Microsoft Visual Studio Build Tools with the C++ workload and Windows SDK:
https://visualstudio.microsoft.com/downloads/
2. Restart your computer
3. Install Nuitka:
```bash
pip install nuitka
```
4. Open a command prompt in the root folder and build the executable:
```bash
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --assume-yes-for-downloads --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
or (Windows x86):
```bash
nuitka --standalone --onefile --include-data-dir=assets=assets --windows-console-mode=disable --assume-yes-for-downloads --target=x86 --company-name="Spawn Project" --product-name="Spawn" --copyright="Copyright (C) 2026 Daniil Korochansky" --output-filename=Spawn.exe --file-version="1.0.0" --product-version="1.0.0" --file-description="IDE for open.mp and SA-MP development" --windows-icon-from-ico=assets/spawn.ico --output-dir=dist --include-package=wx main.py
```
If you are unsuccessful on a 32-bit system, try adding the option: ```--msvc=latest``` (as a last resort, instead of this option, add: ```--mingw64```)

The order of actions is **important**!

*The generated executable will be available in the dist directory.*

### Tests
You can conduct tests to verify the functionality of new features or changes to key system components.
To run the tests, follow these steps:
1. Install pytest
```bash
pip install pytest
```   
2. Create a file named `pytest.ini` in the root folder with the following contents (if it doesn't already exist)
```
[pytest]
pythonpath = .
```
3. Open a command prompt in the root folder
4. Execute the following command: ```pytest -v```

All tests must return a ‘PASSED’ result.
Otherwise, you need to find and fix the error or bug in the code, and then run the tests again.

### Code Coverage
Automated tools track how much of the `core` and `ui` logic is verified by tests. You can see the current percentage in the **Coverage** badge at the top of this README.

* **What it means:** The coverage percentage reflects the ratio of code lines executed during testing. A higher percentage means more logic has been double-checked for bugs.
* **The focus:** Testing visual UI elements is intentionally avoided because graphical components change frequently. Instead, the focus is entirely on securing the stability of the `core` and `ui` logic.

## Stability

Spawn includes automated tests for:
- Git integration
- Project Tree management
- Configuration system
- Dependency management
- File loading and encoding detection

All tests are executed automatically on every commit through GitHub Actions.

## Contributors
Spawn is an open-source project built for the open.mp and SA-MP community.

Contributions of all sizes are welcome, including:
+ Bug reports
+ Feature requests
+ UI/UX suggestions
+ Code contributions
+ Testing and feedback

Thank you for helping make Spawn better for everyone.

### Bug Report
If you encounter an error or bug while using Spawn, follow these steps:
1. Select 'Help' → 'Bug Report'
2. Click the ‘Copy’ button (If 'Log Output' is empty, proceed immediately to the next step.)
3. Click the ‘Open GitHub Issue’ button
4. Paste the completed report into the description and enter a title (If the ‘Log Output’ field was empty, please describe the error or bug yourself.)

## Donations
Spawn is developed in free time and will always remain free and open source.

If you enjoy using Spawn and would like to support its future development, you can make a donation.
Every contribution helps improve the IDE and keep the project moving forward.

Thank you for your support ❤️

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y4L421BNPH)

[Donate via Boosty (Россия / International)](https://boosty.to/daniilkorochansky)

## License
Spawn is licensed under the GNU General Public License v3.0.

See the [LICENSE](https://github.com/daniilkorochansky/spawn/blob/master/LICENSE) file for details.
