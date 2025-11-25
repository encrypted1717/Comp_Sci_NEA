import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, window): #consider adding a log as image
        super().__init__()
        self.txt_colour = None
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
        self.text = ""
        self.text_surf = None
        self.text_rect = None

    def create_rect(self, position, dimensions, txt_colour, rect_colour , text, font, border = 0, offset_x = 0, offset_y = 0, image= None):
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.border = border
        self.rect_colour = rect_colour
        self.dimensions = dimensions #tuple of width and height

        #make the text rect
        self.rect = pygame.Rect((0,0), dimensions) #create rect but leave the coordinate to default to 0,0
        self.rect.center = position
        self.txt_colour = txt_colour
        self.text_surf = font.render(self.text, False, self.txt_colour)  # true/false is for anti-aliasing on the font
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        #apply offsets if needed
        if self.offset_x != 0:
            self.text_rect.x += self.offset_x
        if self.offset_y != 0:
            self.text_rect.y += self.offset_y

        #dictionary holds all data of the button
        self.btn = {"text": self.text, "text surf" : self.text_surf, "text rect": self.text_rect, "colour" : self.rect_colour, "rect" : self.rect, "border" : self.border}
        return self.btn