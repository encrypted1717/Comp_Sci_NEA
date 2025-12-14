import pygame
import logging

class AnimationManager:
    def __init__(self, animation_cooldown : float = 0.2) -> None:
        # Logging setup
        self.log = logging.getLogger(__name__)
        self.log.info("Initialising Animation Manager module")

        # Animation setup
        self.animation_cooldown = animation_cooldown # Seconds per frame
        self.animations = {}
        self.elapsed_time = 0
        self.current_frame = 0

        self.current_animation_frames = []
        self.loop = True
        self.freeze = False

    # Gets spritesheet and returns frames of the animation, frames have to be square
    def load_animation(self, name: str, path: str, scale: float = 1.0, frame_indices: list = None, dimension: int = None) -> None:
        """
                Load an animation from a single-row sprite sheet of square frames.

                - dimension: if None, uses the image height (assumes square frames).
                - frame_indices: which frames to slice; if None, slices all frames.
                  Use [0] to make a single-frame 'default' from the first frame.
        """

        # Exception handler
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            self.log.exception("Error loading sprite sheet from path %s", path)
            raise RuntimeError(f"Error loading sprite_sheet: {path} {error}") # Runtime errors are for when an error doesn't fall into any of the other categories

        # Because all frames are square I don't need length and width, I just name it the dimension
        if dimension is None:
            dimension = sheet.get_height()

        total_frames = sheet.get_width() // dimension
        if frame_indices is None:
            frame_indices = list(range(total_frames)) # Int division necessary for later... range function

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

    def set_animation(self, name: str, loop = True, reset = True) -> None:
        """
                Switch to a named animation.

                - loop: whether the animation should wrap when reaching the end.
                - reset: restart at frame 0. If False and switching to the same
                         animation, keeps the current frame position.
                """
        if name not in self.animations:
                self.log.error("Animation %s does not exist", name)
                raise KeyError(f"Animation {name} does not exist")

        if self.animations[name] != self.current_animation_frames:
            self.current_animation_name = name
            self.current_animation_frames = self.animations[name]

        if reset:
            self.current_frame = 0
            self.elapsed_time = 0

        self.loop = loop

    # Pause animation on current frame
    def pause(self) -> None:
        self.freeze = True

    # Resume animation
    def play(self) -> None:
        self.freeze = False

    def update(self, dt) -> None:
        if not self.freeze and self.current_animation_frames:
            self.elapsed_time += dt
            if self.elapsed_time >= self.animation_cooldown:
                self.elapsed_time = 0
                self.current_frame += 1
                if self.current_frame >= len(self.current_animation_frames):
                    if self.loop:
                        self.current_frame = 0
                    else:
                        # freeze on last frame if not looping
                        self.current_frame = len(self.current_animation_frames) - 1
                        self.freeze = True

    def get_frame(self):
        if not self.current_animation_frames:
            self.log.exception("No animation had been loaded into the manager")
            raise RuntimeError("No animation selected")
        return self.current_animation_frames[self.current_frame]

    def get_name(self):
        return self.current_animation_name

    # Check animation is looping or hasn't reached the end in non-looping mode.
    def is_playing(self) -> bool:
        if self.freeze:
            return False
        if self.loop:
            return True
        return self.current_frame < len(self.current_animation_frames) - 1