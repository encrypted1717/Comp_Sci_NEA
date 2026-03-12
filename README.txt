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

GETTING STARTED

REGISTER
--------

On first launch, register an account on the login screen. Player 1's display settings are applied immediately after login. Player 2 can log in separately from the main menu before starting a match.


CONTROLS
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


SETTINGS
--------

Settings are stored in `assets/game_settings/config_default.ini` and are copied to a per-user file on first login. They can be changed through the in-game Settings screen.


PROJECT STRUCTURE
-----------------

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

FEATURES

GAMEPLAY
--------

    - Best-of-3 round system with per-round countdown, result screen, and win tracking
    - Player vs Player (local) and Player vs CPU modes
    - Three difficulty levels for the CPU opponent: Easy, Medium, Hard
    - Double jump, sprint, crouch, and fast-fall movement
    - 5-attack combo system: Punch 1, Punch 2, Jump Strike, Slide Attack, Energy Punch
    - Block system with a limited block count per round and a regeneration timer
    - Guard break - blocking all hits causes a temporary movement lock
    - Teleport ability - place a portal, then warp back to it at any time
    - Energy system that regenerates over time and gates special moves
    - Knockback and launch effects on Slide Attack and Energy Punch
    - Killzone - entities that fall off the stage are removed from play


Graphics & Rendering
--------------------

    - Virtual renderer at 1920x1080 - scales to any window size with black letterbox bars
    - Multi-layer parallax scrolling background (5 mountain landscape layers)
    - Sprite sheet animation manager with looping, freeze-on-last-frame, and priority interrupts
    - Energy charge overlay rendered on top of the active animation while charged
    - Animated portal effect with per-player colour tinting (blue / red)
    - HUD - health bars, energy bars (with 5 segment dividers), block count, round label, win counter
    - Countdown sequence (3, 2, 1, FIGHT!) at the start of every round with drop shadow text
    - Debug mode - toggle from settings to overlay physics bodies, sprite bounds, and attack hitboxes


MAP & COLLISION
---------------

    - 3 handcrafted tile maps (48x27 grid, 40px tiles = 1920x1080), selected randomly each round
    - Rectangle merging algorithm reduces adjacent solid tiles into the minimum number of colliders
    - One-way platform physics - land from above, pass through from below and sides
    - Fully solid tall-platform collision - blocks ceiling and walls
    - Step detection allows entities to auto-climb small ledges without jumping
    - Player-vs-player separation resolved along the shortest overlap axis with partial velocity transfer


COMBAT SYSTEM
-------------

    - Per-attack hitbox configs with frame-accurate active damage windows
    - Hit registry prevents the same swing landing on the same defender more than once
    - Hitboxes mirror horizontally when the attacker is facing left
    - Blocking consumes one block charge and resets the block regen timer
    - Energy is gained by landing hits


AUTHENTICATION
--------------

    - Login and registration with bcrypt password hashing
    - Password validation (uppercase, lowercase, digit, special character, length rules)
    - Per-player config files (resolution, display mode, FPS, vsync, keybinds)
    - Leaderboard backed by SQLite - tracks fastest Player 1 CPU victories (rank, username, time, date)
    - Duplicate login prevention - the same account cannot be logged in as both players


CPU AI
------

    - Decision loop fires on a configurable reaction timer (not every frame) to simulate human delay
    - Distance-based positioning: chase, preferred range, retreat
    - Probability-weighted attack, block, jump, sprint, and ability usage
    - Slide attack combo (sprint + crouch + punch) triggered at close range
    - Detects when opponent is airborne and jumps to intercept