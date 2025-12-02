import pygame


class AnimationManager:
    def __init__(self):
        self.rect = None
        self.animation = []
        self.path = None
        # Sprite setup
        self.sprite = None
        self.frames = None
        self.scaled_frame_img = None
        self.frame_img = None
        self.sheet_width = None
        self.sheet_height = None
        self.sprite_sheet = None
        self.frame_width = None
        self.frame_height = None

    # Gets spritesheet and returns frames of the animation
    def get_animation(self, path: str, scale = 1) -> list:
        self.path = path
        # Exception handler
        try:
            self.sprite_sheet = pygame.image.load(path).convert_alpha()
        except pygame.error as error:
            print(f"Error loading image: {path} {error}")
            return [] # No animation
        
        # Sprite sheets are all (width) x 128
        self.sheet_height = self.sprite_sheet.get_height()
        self.sheet_width = self.sprite_sheet.get_width()
        self.frames = self.sheet_width // self.sheet_height # Int division necessary for later... range function
        self.animation = [] # Reset any stored animations
        self.frame_width = self.sheet_width // self.frames

        for frame in range(self.frames):
            self.rect = pygame.Rect(self.frame_width * frame, 0, self.frame_width, self.sheet_height) # This creates a rect for every frame
            self.frame_img = self.sprite_sheet.subsurface(self.rect)
            self.scaled_frame_img = pygame.transform.scale_by(self.frame_img, scale)
            self.animation.append(self.scaled_frame_img)


        return self.animation