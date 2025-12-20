"""
    Animation management utilities for game.

    This module provides the AnimationManager class, which handles loading,
    switching, updating, and retrieving frames from sprite-sheet-based animations.
    Animations are assumed to be stored as single-row sprite sheets composed of square frames.
"""

import pygame
import logging


class AnimationManager:
    """
        Manage sprite sheet animations for a single animated entity.

        The AnimationManager loads animations from sprite sheets, tracks
        the current animation state, advances frames over time, and provides
        access to the active frame. Only one animation can be active at a time.
        Animations may optionally loop or freeze on their final frame.
    """
    def __init__(self) -> None:
        # Logging setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Animation Manager module")
        # Animation setup
        self.animations = {}
        self.elapsed_time = 0
        self.current_frame = 0
        self.current_animation_name = None
        self.current_animation_frames = []
        self.loop = True
        self.freeze = False

    def load_animation(self,
                       name: str,
                       path: str,
                       scale: float = 1.0,
                       frame_indices: list | tuple | None = None,
                       dimension: int | None = None
                       ) -> None:
        """
            Load an animation from a single-row sprite sheet of square frames.

            The sprite sheet is assumed to contain frames arranged horizontally,
            where each frame is a square. Frames are extracted, optionally scaled,
            and stored under the given animation name.

            Args:
                name: the key used to store the animation.
                path: the path to the sprite sheet file.
                scale: scale factor applied to every frame.
                frame_indices: slice frames given. If None, all frames in sprite sheet are used.
                dimension: width and height of each square frame. If None, the frame size is inferred from the sprite sheet height.

            Raises:
                RuntimeError: If the sprite sheet cannot be loaded.
                ValueError: If no valid frames are extracted.
        """

        # Exception handler
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            self.log.exception("Error loading sprite sheet from path %s", path)
            raise RuntimeError(
                f"Error loading sprite_sheet: {path} {error}")  # Runtime errors are for when an error doesn't fall into any of the other categories

        if dimension is None:
            dimension = sheet.get_height()

        total_frames = sheet.get_width() // dimension
        if frame_indices is None:
            frame_indices = list(range(total_frames))  # Int division necessary for later... range function

        # Store each frame
        frames = []

        for index in frame_indices:
            if index < 0 or index >= total_frames:
                self.log.warning("Frame index %s out of range for file: %s", index, path)
                continue
            rect = pygame.Rect(index * dimension, 0, dimension, dimension)
            frame_img = sheet.subsurface(rect)

            if scale != 1.0:
                frame_img = pygame.transform.scale_by(frame_img, scale)

            frames.append(frame_img)

        if not frames:
            self.log.exception("No frames were loaded for animation: %s in path %s", name, path)
            raise ValueError(f"No frames were loaded for animation: {name}, {path}")

        self.animations[name] = frames

    def set_animation(self,
                      name: str,
                      loop: bool = False,
                      restart: bool = False
                      ) -> None:
        """
            Switch to a named animation.

            Sets the current animation to the specified one if it has been already loaded and stored.
            If the animation is already active, it may optionally be restarted.

            Args:
                name: the name of the animation to set.
                loop: whether the animation should loop when it reaches the end.
                restart: whether to restart the animation. If False and the animation is already active, the current frame position is preserved.

            Raises:
                KeyError: If the specified animation has not been loaded.
        """

        if name not in self.animations:
            self.log.error("Animation %s does not exist or hasn't been loaded", name)
            raise KeyError(f"Animation {name} does not exist or hasn't been loaded")

        if self.animations[name] != self.current_animation_frames:
            self.current_animation_name = name
            self.current_animation_frames = self.animations[name]
            self.current_frame = 0
            self.elapsed_time = 0

        elif restart:
            self.current_frame = 0
            self.elapsed_time = 0

        self.loop = loop
        self.freeze = False

    def pause(self) -> None:
        """Pause animation on current frame"""
        self.freeze = True

    def play(self) -> None:
        """Resume animation from current frame"""
        self.freeze = False

    def is_playing(self) -> bool:
        """Returns True if the current animation is playing."""
        if self.freeze:
            return False
        if self.loop:
            return True
        return self.current_frame < len(self.current_animation_frames) - 1  # Checks if the animation has played all its frames

    def update(self,
               dt: float,
               cooldown: float = 0.1
               ) -> None:
        """
            Updates the animation by switching to the next frame once elapsed time is larger than the cooldown.

            Args:
                dt: delta time to measure time passed
                cooldown: time in seconds before the next frame can be switched
        """

        if not self.freeze and self.current_animation_frames:
            self.elapsed_time += dt
            if self.elapsed_time >= cooldown:
                self.elapsed_time = 0
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation_frames):
                    if self.loop:
                        self.current_frame = 0
                    else:
                        # freeze on last frame if not looping
                        self.current_frame = len(self.current_animation_frames) - 1
                        self.freeze = True

    def get_frame(self) -> pygame.Surface:
        """Returns the current frame."""

        if not self.current_animation_frames:
            self.log.exception("No animation had been loaded into the manager")
            raise RuntimeError("No animation selected")

        return self.current_animation_frames[self.current_frame]

    def get_frame_index(self) -> int:
        """Returns the current frame index."""

        if not self.current_animation_frames:
            self.log.exception("No animation had been loaded into the manager")
            raise RuntimeError("No animation selected")

        return self.current_frame

    def get_name(self) -> str:
        """Returns the name of current animation selected."""

        if not self.current_animation_frames:
            self.log.exception("No animation had been loaded into the manager")
            raise RuntimeError("No animation selected")
        return self.current_animation_name
