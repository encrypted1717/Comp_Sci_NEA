# Comp_Sci_NEA

A 2D local multiplayer fighting game built in Python as my A-Level Computer Science NEA. Two players compete in a best-of-3 series on a randomly selected stage, with a full combat system, special abilities, and an AI opponent option. The long-term goal is to release this as a free game on Steam.

---

## Overview

The game runs at a fixed virtual resolution of 1920x1080, scaled and letterboxed to fit any window size via a custom `VirtualRenderer`. All screens are managed through a navigation stack (`WindowManager`), and the game loop is driven by delta time for frame-rate-independent physics and animation.

Players log in (or register) before playing. Player 1's display settings are applied on login and persist across sessions. A SQLite leaderboard records Player 1's fastest CPU victories.

---

## Features

### Gameplay
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

### Graphics & Rendering
- Virtual renderer at 1920x1080 - scales to any window size with black letterbox bars
- Multi-layer parallax scrolling background (5 mountain landscape layers)
- Sprite sheet animation manager with looping, freeze-on-last-frame, and priority interrupts
- Energy charge overlay rendered on top of the active animation while charged
- Animated portal effect with per-player colour tinting (blue / red)
- HUD - health bars, energy bars (with 5 segment dividers), block count, round label, win counter
- Countdown sequence (3, 2, 1, FIGHT!) at the start of every round with drop shadow text
- Debug mode - toggle from settings to overlay physics bodies, sprite bounds, and attack hitboxes

### Map & Collision
- 3 handcrafted tile maps (48x27 grid, 40px tiles = 1920x1080), selected randomly each round
- Rectangle merging algorithm reduces adjacent solid tiles into the minimum number of colliders
- One-way platform physics - land from above, pass through from below and sides
- Fully solid tall-platform collision - blocks ceiling and walls
- Step detection allows entities to auto-climb small ledges without jumping
- Player-vs-player separation resolved along the shortest overlap axis with partial velocity transfer

### Combat System
- Per-attack hitbox configs with frame-accurate active damage windows
- Hit registry prevents the same swing landing on the same defender more than once
- Hitboxes mirror horizontally when the attacker is facing left
- Blocking consumes one block charge and resets the block regen timer
- Energy is gained by landing hits

### Authentication & Persistence
- Login and registration with bcrypt password hashing
- Password validation (uppercase, lowercase, digit, special character, length rules)
- Per-player config files (resolution, display mode, FPS, vsync, keybinds)
- Leaderboard backed by SQLite - tracks fastest Player 1 CPU victories (rank, username, time, date)
- Duplicate login prevention - the same account cannot be logged in as both players

### CPU AI
- Decision loop fires on a configurable reaction timer (not every frame) to simulate human delay
- Distance-based positioning: chase, preferred range, retreat
- Probability-weighted attack, block, jump, sprint, and ability usage
- Slide attack combo (sprint + crouch + punch) triggered at close range
- Detects when opponent is airborne and jumps to intercept

---

## Project Structure

```
Comp_Sci_NEA/
├── main.py                          # Entry point - game loop, display setup, event processing
├── assets/
│   ├── game_settings/
│   │   ├── config_default.ini       # Default settings template (resolution, FPS, keybinds)
│   │   └── users/                   # Per-user config files generated on first login
│   ├── characters/                  # Sprite sheets and animation assets
│   ├── fonts/                       # OldeTome and GothicPixel font files
│   ├── images/background/           # Parallax mountain layer PNGs
│   └── data/
│       ├── login_credentials.db     # SQLite - user accounts (hashed passwords)
│       ├── leaderboard.db           # SQLite - CPU victory times
│       └── debug.log                # Runtime log output
├── core/
│   ├── button.py                    # UI sprite - static label, clickable button, and text input field
│   ├── collider.py                  # Static rectangular platform sprite
│   ├── collision_manager.py         # Positional physics resolution (platform + player-player)
│   ├── config_manager.py            # .ini file reader/writer (wraps configparser)
│   ├── cpu.py                       # AI opponent entity - extends Entity with a decision loop
│   ├── entity.py                    # Player entity - physics, combat, animation, input binds
│   ├── window.py                    # Base screen class - surface, buttons, ESC, back button
│   └── window_manager.py            # Navigation stack - creates, caches, and switches screens
├── graphics/
│   ├── animation_manager.py         # Sprite sheet loader and frame-advance system
│   ├── map_generation.py            # Tile grid to merged Collider list conversion
│   ├── parallax_background.py       # 5-layer scrolling background with seamless wrapping
│   └── virtual_renderer.py          # Fixed-resolution rendering with letterbox scaling
├── utils/
│   ├── combat_system.py             # Hitbox construction, hit detection, block logic, hit registry
│   ├── portal.py                    # Teleport portal - open/close animation, lifetime, colour tinting
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
└── requirements.txt
```

---

## Technologies Used

| Category | Technology |
|---|---|
| Language | Python 3 |
| Game Framework | Pygame CE |
| Database | SQLite3 |
| Password Hashing | bcrypt |
| Configuration | configparser |
| Logging | Python logging module |

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/encrypted1717/Comp_Sci_NEA.git
cd Comp_Sci_NEA
pip install -r requirements.txt
```

### Running the Game

```bash
python main.py
```

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

## Notes

This is my first substantial Python project, written and submitted as A-Level Computer Science coursework. The goal beyond the NEA is to release it as a free game on Steam.
