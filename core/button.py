import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self): #consider adding a log as image
        super().__init__()
        self.btn = None
        self.rect = None
        self.text_surf = None
        self.text_rect = None

    def create_rect(self, position, dimensions, text_colour, rect_colour , text, font, border = 0, offset_x = 0, offset_y = 0, image= None):
        #make the text rect
        self.rect = pygame.Rect((0,0), dimensions) #create rect but leave the coordinate to default to 0,0
        self.rect.center = position
        self.text_surf = font.render(text, False, text_colour)  # true/false is for anti-aliasing on the font
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        #apply offsets if needed
        if offset_x != 0:
            self.text_rect.x += offset_x
        if offset_y != 0:
            self.text_rect.y += offset_y

        self.btn = {
            "text": text,
            "text_surf" : self.text_surf,
            "text_rect": self.text_rect,
            "rect_colour" : rect_colour,
            "rect" : self.rect,
            "border" : border,
            "position": self.rect.center,
            "offset_x" : offset_x,
            "offset_y" : offset_y,
            "font" : font
        }

        return self.btn

    def update_text(self, btn, text, text_colour, font, offset_x = None, offset_y = None):
        self.btn = btn
        self.rect = self.btn["rect"]
        self.text_surf = font.render(text, False, text_colour)
        self.text_rect = self.text_surf.get_rect(center=btn["position"])

        if offset_x is None:
            self.text_rect.x += btn["offset_x"]
        else:
            self.text_rect.x += offset_x
            self.btn["offset_x"] = offset_x
        if offset_y is None:
            self.text_rect.y += btn["offset_y"]
        else:
            self.text_rect.y += offset_y
            self.btn["offset_y"] = offset_y

        self.btn["text"] = text
        self.btn["text_surf"] = self.text_surf
        self.btn["text_rect"] = self.text_rect
        self.btn["font"] = font

        return self.btn