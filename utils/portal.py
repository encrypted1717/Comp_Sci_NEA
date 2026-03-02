import pygame
from graphics.animation_manager import AnimationManager


class Portal:
    """
    A placed portal effect for the teleport ability.
    Tracks its own position, animation state, and open lifetime.
    Spawned and managed by game.py; entity.py signals when to create or use one.
    """

    OPEN_DURATION = 7.0  # seconds the portal stays open before auto-closing

    def __init__(self, position: tuple, scale: float = 1.0, tint: tuple = (255, 255, 255)):
        """
        Args:
            position — (x, y) midbottom of the entity when the portal was placed.
            scale    — sprite scale to match the entity's size, passed in from game.py.
            tint     — RGB colour to multiply over every frame. (255, 255, 255) means no tint.
                       Pass (100, 100, 255) for player 1 (blue) or (255, 80, 80) for player 2 (red).
        """
        self.position = position  # midbottom anchor, same coordinate system as entity body
        self.anim = AnimationManager()
        self.lifetime = 0.0
        self.closing = False  # True once lifetime expires or the teleport is triggered
        self.done = False     # True once portal_close finishes — safe to remove

        # Load portal animations directly from disk — these belong to the portal, not the entity
        path = "assets\\characters\\default\\other\\animations\\"
        self.anim.load_animation("portal_open",  path + "portal.png", scale=scale, frame_indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.anim.load_animation("portal_close", path + "portal.png", scale=scale, frame_indices=[11, 12, 13, 14, 15])

        # Apply colour tint to every loaded frame by multiplying each pixel's RGB channels.
        # The original sprite is pink/magenta — multiplying shifts it to the target colour.
        if tint != (255, 255, 255):
            for anim_name in ("portal_open", "portal_close"):
                frames, cooldown = self.anim.animations[anim_name]
                tinted_frames = []
                for frame in frames:
                    tinted = frame.copy()
                    tinted.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
                    tinted_frames.append(tinted)
                self.anim.animations[anim_name] = (tinted_frames, cooldown)

        self.anim.set_animation("portal_open", loop=False)

    def get_img_rect(self) -> pygame.Rect:
        """
        Returns a pygame Rect for the current portal frame, positioned so its
        midbottom sits exactly at self.position (the anchor point where the portal
        was placed — same coordinate as the entity's feet).
        """
        if not self.anim.current_animation_frames:
            return pygame.Rect(self.position, (0, 0))
        frame_rect = self.anim.get_frame().get_rect()
        frame_rect.midbottom = self.position
        return frame_rect

    def update(self, dt: float) -> None:
        self.anim.update(dt)

        if not self.closing:
            # Once the open anim finishes, freeze on the last frame (freeze=True is set by
            # the animation manager automatically when loop=False and all frames are done)
            self.lifetime += dt
            if self.lifetime >= self.OPEN_DURATION:
                self.begin_close()
        else:
            if not self.anim.is_playing():
                self.done = True

    def begin_close(self) -> None:
        """Trigger the close animation. Safe to call multiple times."""
        if not self.closing:
            self.closing = True
            if "portal_close" in self.anim.animations:
                self.anim.set_animation("portal_close", loop=False, restart=True)
            else:
                self.done = True  # no close anim loaded, remove immediately

    def draw(self, surface: pygame.Surface) -> None:
        if self.anim.current_animation_frames:
            surface.blit(self.anim.get_frame(), self.get_img_rect().topleft)