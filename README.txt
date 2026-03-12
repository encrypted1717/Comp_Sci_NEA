1. Download folder in your preferred directory
2. In pycharm open project from the folder,
3. Select Trust all projects in the folder
4. Then this will prompt you to create a venv and do so within the folder then double click main.py to open it then run the current file
5. Once open, pygame-ce is required however normal pygame may work (not tested)
6. If not installed already close pycharm and then open command prompt
7. Enter the directory of the folder by typing: cd (directory)
8. Then type the directory of the activate file within the venv by itself. This is always within the Scripts folder for example: C:\Comp_Sci_NEA\.venv\Scripts\activate
9. This would have activated the venv which should change your console to (venv) then the directory... now type: pip install pygame-ce
10. All done now you can close the command prompt and re-open pycharm.

Comp_Sci_NEA

A 2D local multiplayer fighting game built in Python as my A-Level Computer Science NEA. Two players compete in a best-of-3 series on a randomly selected stage, with a full combat system, special abilities, and an AI opponent option.

---

INSTALLATION GUIDE

PREREQUISITES
-------------
Before starting, ensure you have the following installed:
- Python 3.x        (download from python.org)
- PyCharm IDE       (Community or Professional edition)

PART 1 - OPENING THE PROJECT
-----------------------------
1. Download the project folder and place it in your preferred directory.

2. Open PyCharm and select Open, then navigate to and select the project folder.

3. When prompted, select "Trust all projects in the folder".

4. PyCharm will prompt you to create a virtual environment (venv) - accept this
   and create it within the project folder.

5. Double-click main.py to open it, then click Run > Run Current File.

NOTE: Do not open main.py directly by double-clicking it in File Explorer - this
will not use the virtual environment and the game will not launch correctly.
Always open it through PyCharm.


PART 2 - INSTALLING DEPENDENCIES
----------------------------------
The project includes a requirements.txt file listing all required packages.
PyCharm will automatically detect this and display a banner at the top of the
editor saying "Package requirements are not satisfied" - simply click Install
and PyCharm will handle everything.

If the banner does not appear:

1. Close PyCharm if it is currently open.

2. Open Command Prompt (search for cmd in the Windows search bar).

3. Navigate to the project folder by typing:
      cd <path to your project folder>
   For example:
      cd C:\Projects\MyGame

4. Activate the virtual environment by typing the full path to the activate
   script. This is always found in the Scripts folder inside the venv.
   For example:
      C:\Projects\MyGame\.venv\Scripts\activate

   Your command prompt should now show (.venv) at the start of the line,
   confirming the venv is active.

5. Install all dependencies by typing:
      pip install -r requirements.txt

6. Once installation is complete, close Command Prompt and reopen PyCharm.
   The game is now ready to run.

Tested on Python 3.14 with pygame-ce 2.5.7 and bcrypt on Windows 11.

---

Getting Started

Controls
--------

Default keybinds (configurable in-game via the Controls screen):

| Action | Player 1 | Player 2 |
|---|---|---|
| Move Left | A | Left Arrow |
| Move Right | D | Right Arrow |
| Jump | W | Up Arrow |
| Crouch / Fast Fall | S | Down Arrow |
| Sprint | Left Shift | Right Shift |
| Punch | Space | Enter |
| Block | E | Backspace |
| Side Ability (Teleport) | 1 | Numpad 0 |
| Main Ability (Energy Punch) | 2 | Numpad 1 |

Project Structure

Comp_Sci_NEA/
├── main.py                          # Entry point - game loop, display setup, event processing
├── assets/
│   ├── game_settings/
│   │   ├── config_default.ini       # Default settings template (resolution, FPS, keybinds)
│   │   └── users/                   # Per-user config files generated on first login | Created after game run
│   │       └── config_#             # User config that is assigned per user id | Created after game run
│   ├── characters/                  # Sprite sheets and animation assets
│   ├── fonts/                       # OldeTome and GothicPixel font files
│   ├── images/background/           # Parallax mountain layer PNGs
│   └── data/
│       ├── login_credentials.db     # SQLite - user accounts (hashed passwords) | Created after game run
│       ├── leaderboard.db           # SQLite - CPU victory times | Created after game run
│       └── debug.log                # Runtime log output | Created after game run
├── core/
│   ├── button.py                    # UI sprite - static label, clickable button, and text input field
│   ├── collider.py                  # Static rectangular platform sprite
│   ├── cpu.py                       # AI opponent entity - extends Entity with a decision loop
│   ├── entity.py                    # Player entity - physics, combat, animation, input binds
│   ├── window.py                    # Base screen class - surface, buttons, ESC, back button
│   └── window_manager.py            # Navigation stack - creates, caches, and switches screens
├── graphics/
│   ├── animation_manager.py         # Sprite sheet loader and frame-advance system
│   ├── map_generation.py            # Tile grid to merged Collider list conversion
│   ├── parallax_background.py       # 5-layer scrolling background with seamless wrapping
│   ├── portal.py                    # Teleport portal - open/close animation, lifetime, colour tinting
│   └── virtual_renderer.py          # Fixed-resolution rendering with letterbox scaling
├── utils/
│   ├── collision_manager.py         # Positional physics resolution (platform + player-player)
│   ├── combat_system.py             # Hitbox construction, hit detection, block logic, hit registry
│   ├── config_manager.py            # .ini file reader/writer (wraps configparser)
│   └── tile_map.py                  # Static tile grid data for all 3 maps
├── windows/
│   ├── controls.py                  # Keybind viewer/editor screen
│   ├── exit_menu.py                 # Exit confirmation overlay
│   ├── game.py                      # Active match - round lifecycle, HUD, entities, combat, portals
│   ├── game_setup.py                # Pre-match setup (PvP vs CPU, difficulty selection)
│   ├── leaderboard.py               # Ranked table of fastest CPU victories
│   ├── login.py                     # Login and registration with inline validation feedback
│   ├── main_menu.py                 # Main menu
│   ├── pause_menu.py                # Pause overlay (uses frozen game frame as backdrop)
│   ├── settings.py                  # Display settings (resolution, mode, FPS, debug toggle)
│   └── victory_menu.py              # Match result screen
└── requirements.txt                 # Libraries that should be installed in order to run the project
---



### Prerequisites

- Python 3.10+
- pip

On first launch, register an account on the login screen. Player 1's display settings are applied immediately after login. Player 2 can log in separately from the main menu before starting a match.

---

## Controls

Default keybinds (configurable in-game via the Controls screen):

| Action | Player 1 | Player 2 |
|---|---|---|
| Move Left | A | Left Arrow |
| Move Right | D | Right Arrow |
| Jump | W | Up Arrow |
| Crouch / Fast Fall | S | Down Arrow |
| Sprint | Left Shift | Right Shift |
| Punch | Space | Enter |
| Block | E | Backspace |
| Side Ability (Teleport) | 1 | Numpad 0 |
| Main Ability (Energy Punch) | 2 | Numpad 1 |

---

## Configuration

Settings are stored in `assets/game_settings/config_default.ini` and copied to a per-user file on first login. They can be changed through the in-game Settings screen or by editing the `.ini` directly.

Available options include screen resolution, display mode (Windowed / Borderless / Fullscreen), FPS cap, Vsync, debug overlay toggle, and all keybinds for both players.

---

## Not Yet Implemented / In Progress

- Additional character types and sprite sets
- In-game map editor
- Additional tile types beyond sky and dirt
- Sound and music
- Full Steam build and packaging

---
