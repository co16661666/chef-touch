class GameController:
    def __init__(self):
        self.cut_count = 0
        self.cut_active = False
        self.mixing = 0  # 0 -> idle, 1 -> mixing

    def update(self, raw_update):
        items = [item.strip() for item in raw_update.split(",")]
        if len(items) >= 2:
            if int(items[0]) >= self.cut_count:
                self.cut_count = int(items[0])
                self.cut_active = True
            else:
                self.cut_active = False

            self.mixing = int(items[1])