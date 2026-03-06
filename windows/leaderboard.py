"""
    Leaderboard window for game.

    This module provides the LeaderboardMenu class, which displays a ranked table
    of Player 1's fastest CPU victories. Records are stored in a SQLite database
    and sorted by elapsed time ascending (fastest first). Only wins by Player 1
    against a CPU opponent are eligible - losses and PvP results are never stored.

    The table shows: Rank | Username | Time (mm:ss.cc) | Date
"""

import sqlite3
import pygame
from datetime import date
from core.window import Window
from core.button import Button


class Leaderboard(Window):
    """
        Read-only leaderboard screen displaying the top CPU-defeat times.

        Inherits display surface, renderer, button group, font registry, and the
        auto back button from Window. Reads all records fresh from the database on
        every open so new entries (written by WindowManager immediately after a win)
        are always visible. Uses the same visual language as ControlsMenu - white
        text on black, GothicPixel and OldeTome fonts, bordered Button labels.
    """

    def __init__(self, display, renderer):
        """
            Initialise the leaderboard window and build its UI.

            Args:
                display:  the pygame display surface.
                renderer: the renderer managing the virtual surface and scaling.
        """
        super().__init__(display, renderer)

        self.db_path  = "assets\\data\\leaderboard.db"
        self._records = self._fetch_records()
        self.__create_buttons()

    def _ensure_db(self):
        """
            Open (or create) the leaderboard database and guarantee the schema exists.

            Returns:
                An open sqlite3.Connection to the leaderboard database.
        """
        con = sqlite3.connect(self.db_path)
        con.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                elapsed_time REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        con.commit()
        return con

    def record_result(self, username: str, elapsed_time: float) -> None:
        """
            Insert a new leaderboard entry for a Player 1 CPU victory.

            Called by WindowManager immediately after the win is confirmed, before
            the VictoryMenu is pushed, so the record is available the next time
            the leaderboard is opened.

            Args:
                username:     Player 1's display name.
                elapsed_time: total active combat time in seconds (countdown and
                              post-round delays excluded).
        """
        con      = self._ensure_db()
        date_str = date.today().isoformat()
        con.execute(
            "INSERT INTO leaderboard (username, elapsed_time, date) VALUES (?, ?, ?)",
            (username, elapsed_time, date_str)
        )
        con.commit()
        con.close()
        self.log.info("Leaderboard entry saved: %s  %.2fs  %s", username, elapsed_time, date_str)

    def _fetch_records(self, limit: int = 15) -> list:
        """
            Retrieve the top records sorted by elapsed time ascending. Displays 15 fastest times

            Args:
                limit: maximum number of rows to return (default 15).

            Returns:
                List of (rank, username, elapsed_time, date) tuples.
        """
        con  = self._ensure_db()
        rows = con.execute(
            "SELECT username, elapsed_time, date FROM leaderboard "
            "ORDER BY elapsed_time ASC LIMIT ?",
            (limit,)
        ).fetchall()
        con.close()
        return [(i + 1,) + row for i, row in enumerate(rows)]

    def draw(self, dt):
        """Fill with solid black then render all buttons."""
        self.surface.fill((0, 0, 0))
        super().draw(dt)

    def __create_buttons(self):
        """Build and register all static labels and the leaderboard table rows."""
        title_font  = pygame.font.Font(self.fonts["OldeTome"],    56)
        header_font = pygame.font.Font(self.fonts["GothicPixel"], 16)
        row_font    = pygame.font.Font(self.fonts["GothicPixel"], 14)
        empty_font  = pygame.font.Font(self.fonts["OldeTome"],    36)

        # Shared styling
        header_kwargs = {
            "font":          header_font,
            "text_colour":   "#000000",
            "rect_colour":   "#ffffff",
            "border":        4,
            "border_colour": "#000000",
            "offset_y":      4,
        }

        title_label = Button(
            (self.center_x, 70),
            (450, 70),
            "Leaderboard",
            title_font,
            "#ffffff", "#000000",
            offset_y=4
        )

        header_y = 175
        header_height = 55

        rank_label = Button(
            (310, header_y),
            (200, header_height),
            "Rank",
            **header_kwargs
        )
        user_label = Button(
            (700, header_y),
            (500, header_height),
            "Username",
            **header_kwargs
        )
        time_label = Button(
            (1220, header_y),
            (350, header_height),
            "Time",
            **header_kwargs
        )
        date_label = Button(
            (1620, header_y),
            (350, header_height),
            "Date",
            **header_kwargs
        )

        self.buttons.add(title_label, rank_label, user_label, time_label, date_label)

        if not self._records:
            no_data = Button(
                (self.center_x, self.center_y),
                (900, 80),
                "No records yet - beat the CPU to get on the board!",
                empty_font,
                "#ffffff", "#000000",
                offset_y=4
            )
            self.buttons.add(no_data)
            return

        row_start_y = 255
        row_step = 70
        row_height = 60

        row_kwargs = {
            "font": row_font,
            "text_colour": "#ffffff",
            "border": 3,
            "border_colour": "#333333",
            "offset_y": 4,
        }

        for index, (rank, username, elapsed_time, date) in enumerate(self._records):
            y = row_start_y + index * row_step
            rect_colour = "#1a1a1a" if index % 2 == 0 else "#000000" # Have a change of colour every row

            self.buttons.add(
                Button(
                    (310, y),
                    (200, row_height),
                    str(rank),
                    rect_colour=rect_colour,
                    **row_kwargs
                ),
                Button(
                    (700, y),
                    (500, row_height),
                    username,
                    rect_colour=rect_colour,
                    **row_kwargs),
                Button(
                    (1220, y),
                    (350, row_height),
                    self._format_time(elapsed_time),
                    rect_colour=rect_colour,
                    **row_kwargs
                ),
                Button(
                    (1620, y),
                    (350, row_height),
                    date,
                    rect_colour=rect_colour,
                    **row_kwargs
                ),
            )

    def _format_time(self, seconds: float) -> str:
        """
            Convert a raw elapsed-seconds float into a mm:ss.cc display string.

            Args:
                seconds: total elapsed time in seconds.

            Returns:
                A string like "01:23.45".
        """
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        centis = int(round((seconds - int(seconds)) * 100))
        return f"{minutes:02d}:{secs:02d}.{centis:02d}"