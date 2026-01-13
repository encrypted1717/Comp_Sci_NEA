class ResolutionScaler:
    def __init__(self, display_size, design_size = (1920, 1080)):
        width, height = display_size
        design_width, design_height = design_size
        self.scaled_x = width / design_width
        self.scaled_y = height / design_height
        self.scale = min(self.scaled_x, self.scaled_y)  # uniform scale for general non x/y type of code

    def x(self, value):
        return int(value * self.scaled_x)

    def y(self, value):
        return int(value * self.scaled_y)

    def u(self, value):
        return int(value * self.scale)