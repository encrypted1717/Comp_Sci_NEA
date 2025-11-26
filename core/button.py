import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, window): #consider adding a log as image
        super().__init__()
        self.window = window
        self.btn = None

        #features of rect
        self.rect = None
        self.position = None
        self.dimensions = None
        self.rect_colour = None
        self.offset_x = 0
        self.offset_y = 0
        self.border = False

        #text surface
        self.text_colour = None
        self.font = None
        self.text = ""
        self.text_surf = None
        self.text_rect = None

    def create_rect(self, position, dimensions, text_colour, rect_colour , text, font, border = 0, offset_x = 0, offset_y = 0, image= None):
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.border = border
        self.rect_colour = rect_colour
        self.dimensions = dimensions #tuple of width and height
        self.font = font

        #make the text rect
        self.rect = pygame.Rect((0,0), dimensions) #create rect but leave the coordinate to default to 0,0
        self.rect.center = position
        self.text_colour = text_colour
        self.text_surf = self.font.render(self.text, False, self.text_colour)  # true/false is for anti-aliasing on the font
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        #apply offsets if needed
        if self.offset_x != 0:
            self.text_rect.x += self.offset_x
        if self.offset_y != 0:
            self.text_rect.y += self.offset_y

        #dictionary holds all data of the button
        self.btn = {"text": self.text, "text surf" : self.text_surf, "text rect": self.text_rect, "colour" : self.rect_colour, "rect" : self.rect, "border" : self.border, "position": self.rect.center}
        return self.btn

    def update_txt(self, btn, text, colour, font):
        self.btn = btn
        self.rect.center = self.btn["position"]
        self.text_colour = colour
        self.text = text
        self.rect = self.btn["rect"]
        self.font = font
        self.text_surf = self.font.render(self.text, False, self.text_colour)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.btn["text_surf"] = self.text_surf
        self.btn["text_rect"] = self.text_rect
        return self.btn