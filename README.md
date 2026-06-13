![GitHub License](https://img.shields.io/github/license/daniilkorochansky/spawn)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Language](https://img.shields.io/badge/language-Python-yellow.svg)
![Tests](https://github.com/daniilkorochansky/spawn/actions/workflows/tests.yml/badge.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

<div align="center">
  [English
  /
  <a href="https://github.com/daniilkorochansky/spawn/blob/master/README_ru.md">Русский</a>]
</div>

# Spawn
<img width="180" height="180" alt="spawn_new" src="https://github.com/user-attachments/assets/18435694-229c-468d-87af-11f9ed4d243e" />

A fast and modern development environment (IDE), created specifically for creating open.mp and SA-MP servers, in the Pawn programming language.

## Overview
<img width="1920" height="1049" alt="ui" src="https://github.com/user-attachments/assets/505d6a46-33cc-45ae-bed3-f011474a4dc7" />

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
  - [Project Creation](#project-creation)
  - [Split Editor View](#split-editor-view)
  - [RGBA/HEX Color Highlighting](#rgbahex-color-highlighting)
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
- [Development](#development)
  - [Requirements](#requirements)
  - [Install Dependencies](#install-dependencies)
  - [Run](#run)
  - [Tests](#tests)
- [Stability](#stability)
- [Contributors](#contributors)
  - [Bug Report](#bug-report)
- [Donations](#donations)
- [License](#license)

## Features
+ Integration with [SAMPCTL](https://github.com/Southclaws/sampctl)
+ Developed specifically for [open.mp](https://github.com/openmultiplayer) & SA-MP
+ Dependency Manager for server components and packages
+ RGBA/HEX color highlighting directly in the code editor
+ Integrated Git support with source control panel
+ Split Editor View for working with multiple files side-by-side
+ Project Tree optimized for large gamemode projects
+ Integrated build and server output panels

## Screenshots
### Project Creation

### Split Editor View

### RGBA/HEX Color Highlighting

### Dependency Manager

### Git and Source Control

### Project Tree

## Installation
### Download
1. Download the latest release from the Releases page.
2. Run 'Spawn.exe'.

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
+ To 'ensure', click the button with the same name.

### Use Git
1. Right-click the root folder in the Project Tree → choose 'Initialize Repository'. (If the repository wasn't on the server)
2. Create your first commit.
3. Track changes directly from the IDE.

If the repository is already on the server, Spawn will automatically detect it (provided Git is enabled in the settings)

### Build and Run Server
1. Open the project.
2. Build your server.
3. Start the server.
4. Monitor output in the integrated console.

You're ready to develop open.mp and SA-MP servers with Spawn.

## Development
### Requirements
+ Python 3.13+
+ wxPython
+ GitPython
+ Markdown
+ watchdog
+ pytest

### Install Dependencies
```python
pip install -r requirements.txt
```
### Run
```python
python main.py
```

### Tests
You can conduct tests to verify the functionality of new features or changes to key system components.
To run the tests, follow these steps:
1. Create a file named ‘pytest.ini’ in the root folder with the following contents (if it doesn't already exist)
```
[pytest]
pythonpath = .
```
3. Open a command prompt in the root folder
4. Execute the following command: ```pytest -v```

All tests must return a ‘PASSED’ result.
Otherwise, you need to find and fix the error or bug in the code, and then run the tests again.

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
1. Select 'Help' -> 'Bug Report'
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
