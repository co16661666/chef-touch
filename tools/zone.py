class Zone:
    def __init__(self, name, x_min, x_max, y_min, y_max):
        self.name = name
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def inZone(self, x, y):
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max