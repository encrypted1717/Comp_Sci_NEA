"""
    Window management utilities for game.

    This module provides the WindowManager class, which owns the entire window
    lifecycle - creating, caching, switching, and destroying Window instances.
    Navigation is modelled as a stack: the top of the stack is the active window,
    and pushing/popping moves between screens while preserving history.
"""

import pygame
from . import Window
from windows import (
    Game,
    GameSetup,
    Login,
    MainMenu,
    Controls,
    PauseMenu,
    Settings,
    VictoryMenu,
    Leaderboard,
    ExitMenu
)


class WindowManager:
    """
        Manage the full lifecycle of Window instances using a navigation stack.

        Windows are created and cached in self.windows so they preserve
        their state across visits. Overlay windows (pause, settings, controls,
        exit) are deleted from the cache on pop so they reset the next time they
        are opened. Hard resets via __reset_to clear the stack and cache entirely.
    """

    def __init__(self, display, renderer):
        """
            Initialise the manager and open the login screen.

            Args:
                display: the pygame Surface to render onto.
                renderer: the VirtualRenderer instance used by all windows.
        """
        self.display = display
        self.renderer = renderer

        # Player data is (user_id, username), populated after each player logs in
        self.player1 = None
        self.player2 = None
        self.login_player = 1  # tracks which player slot the next login screen is for

        # Navigation stack - top of stack is the active window
        self.stack = ["login"]

        # Window cache - maps state name to its Window instance.
        # Type hint clarifies the dict shape and suppresses IDE warnings.
        self.windows: dict[str, Window] = {"login": Login(self.display, self.renderer, self.login_player)}

        self.pause_background = None # last rendered game frame, passed to PauseMenu as its background
        self.winner = None # set when a best-of-3 winner is determined, passed to VictoryMenu
        self.cpu_difficulty = None # None means PvP; "easy"/"medium"/"hard" means PvCPU

    def get_state(self) -> str:
        """Return the name of the currently active window (top of the stack)."""
        return self.stack[-1]

    def __ensure_window(self, state: str) -> None:
        """
            Create and cache a window instance if one does not already exist for the given state.

            Each state maps to a specific Window subclass. Windows that need player
            data or other runtime values receive them as constructor arguments here.

            Args:
                state: the name of the window to create (e.g. "main", "game", "pause").
        """
        if state in self.windows:
            return

        if state == "main":
            self.windows[state] = MainMenu(self.display, self.renderer, self.player1, self.player2)
        elif state == "game":
            self.windows[state] = Game(self.display, self.renderer, self.player1, self.player2, cpu_difficulty=self.cpu_difficulty)
        elif state == "setup":
            self.windows[state] = GameSetup(self.display, self.renderer)
        elif state == "controls":
            self.windows[state] = Controls(self.display, self.renderer, self.player1, self.player2)
        elif state == "settings":
            self.windows[state] = Settings(self.display, self.renderer, self.player1)
        elif state == "pause":
            self.windows[state] = PauseMenu(self.display, self.renderer, self.pause_background)
        elif state == "login":
            self.windows[state] = Login(self.display, self.renderer, self.login_player)
        elif state == "victory":
            self.windows[state] = VictoryMenu(self.display, self.renderer, self.winner)
        elif state == "leaderboard":
            self.windows[state] = Leaderboard(self.display, self.renderer)
        else:
            self.windows[state] = ExitMenu(self.display, self.renderer)

    def __get_window(self) -> Window:
        """
            Return the active Window instance, creating it first if needed.

            Returns:
                The Window at the top of the navigation stack.
        """
        state = self.get_state()
        self.__ensure_window(state)
        return self.windows[state]

    def __push(self, state: str) -> None:
        """
            Push a new window onto the stack, making it the active window.

            Creates the window if it isn't cached yet, then hides the mouse
            cursor while the game window is active.

            Args:
                state: the name of the window to push.
        """
        self.__ensure_window(state)
        self.stack.append(state)
        pygame.mouse.set_visible(state != "game")  # hide cursor during gameplay

    def __pop(self) -> None:
        """
            Return to the previous window by popping the top of the stack.

            Overlay windows (pause, settings, controls, exit) are evicted from the
            cache on pop so they are rebuilt fresh the next time they are opened.
            If the stack only has one entry, this is a no-op to prevent going below root.
        """
        if len(self.stack) <= 1:
            return
        top = self.stack.pop()
        if top in ("pause", "settings", "controls", "exit"):  # overlays reset on close
            self.windows.pop(top, None)
        pygame.mouse.set_visible(self.get_state() != "game")

    def __reset_to(self, state: str) -> None:
        """
            Hard-navigate to a state, clearing the entire stack and window cache.

            Used when returning to a root screen (e.g. main menu or login) where
            all previous window state should be discarded rather than preserved.

            Args:
                state: the name of the window to reset to.
        """
        self.stack = [state]
        self.windows = {}           # discard all cached windows and their state
        self.pause_background = None
        self.__ensure_window(state)
        pygame.mouse.set_visible(state != "game")

    def update_window(self, events) -> tuple | None:
        """
            Process events for the active window and handle any navigation action it returns.

            Each window's event_handler returns either None (no action) or a string/tuple
            describing what should happen next. This method interprets those actions and
            drives all stack mutations, player data updates, and display changes.

            Args:
                events: list of mapped pygame events from the current frame.

            Returns:
                A tuple passed back to main.py when the display needs to be recreated
                (e.g. ("update_display", user_id) after player 1 logs in), or None otherwise.
        """
        action = self.__get_window().event_handler(events)
        if not action:
            return None

        if isinstance(action, tuple):
            if action[0] == "game":
                self.windows.pop("game", None)  # always rebuild Game so it starts fresh
                if action[1] == "pvp":
                    self.cpu_difficulty = None
                elif action[1] == "cpu":
                    self.cpu_difficulty = action[2]  # "easy" / "medium" / "hard"
                self.__push("game")
                return None

            if action[0] == "victory":
                # action[1] is (winner_label, winner_name, elapsed_time_or_None)
                winner_data = action[1]
                self.winner = winner_data
                winner_label  = winner_data[0]   # "Player 1" or "Player 2"
                elapsed_time  = winner_data[2] if len(winner_data) > 2 else None

                # Record to leaderboard only when Player 1 beats the CPU
                if winner_label == "Player 1" and self.cpu_difficulty and elapsed_time is not None and self.player1:
                    Leaderboard.record_result(self.player1[1], elapsed_time)

                self.windows.pop("victory", None)  # rebuild so it shows the new winner
                self.__push("victory")
                return None

            if action[0] == "main":
                player_data = action[1]  # (user_id, username)
                self.windows.pop("main", None)  # rebuild so it receives updated player data
                if not self.player1:
                    # First login - this is player 1. Their display settings are applied
                    # since they are physically on this machine.
                    self.player1 = player_data
                    self.__push("main")
                    return "update_display", self.player1[0]  # pass user_id to main.py to load their config
                else:
                    self.player2 = player_data
                    self.__push("main")
                    return None

            if action[0] == "pause":
                self.pause_background = action[1]  # frozen game frame used as the pause menu backdrop
                self.windows.pop("pause", None)
                self.__push("pause")
                return None

            if action[0] == "login":
                self.login_player = action[1]  # which player slot (1 or 2) the next login is for
                self.windows.pop("login", None)
                self.__push("login")
                return None

        if action == "back":
            self.__pop()
            return None

        if action in ("setup", "settings", "controls", "exit", "leaderboard"):
            self.__push(action)
            return None

        if action == "main":
            self.__reset_to(action)  # hard reset - discard game and all other windows
            return None

        if action == "logout":
            # Clear all player state and return to a fresh login screen
            self.player1 = None
            self.player2 = None
            self.login_player = 1
            self.__reset_to("login")
            return None

        if action == "reload_controls":
            if "game" in self.windows:
                self.windows["game"].reload_controls()
            return None

        if action == "update_display":
            if "game" in self.windows:
                self.windows["game"].reload_settings()
            return "update_display", self.player1[0]  # pass through to main.py so it can recreate the display surface

        return None

    def update_display(self, new_display) -> None:
        """
            Swap in a new display surface and propagate it to all cached windows.

            Called by main.py after the display is recreated (e.g. on window resize
            or after applying player 1's display settings on login).

            Args:
                new_display: the new pygame Surface to render onto.
        """
        self.display = new_display
        for window in self.windows.values():
            window.set_display(self.display)  # each window holds a reference that must also be updated

    def draw(self, dt) -> None:
        """
            Draw the active window for this frame.

            Args:
                dt: delta time in seconds since the last frame.
        """
        self.__get_window().draw(dt)