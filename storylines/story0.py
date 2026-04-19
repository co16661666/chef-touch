from gameObjects.ingredientPlate import Ingredient
from gameObjects.mixPlate import MixPlate
from tools.zone import Zone

class Story0:
    def __init__(self, initTagPosDict):
        self.story_id = 0
        self.story_name = "Basic Cutting"

        # Zones TODO: Adjust for setup
        self.cuttingZone = Zone("Cutting Zone", 415, 615, 300, 415)
        self.mixingZone = Zone("Mixing Zone", -15, 415, 200, 415)
        self.servingZone = Zone("Serving Zone", 415, 615, -15, 250)

        self.lettuce = Ingredient(6, "Lettuce", initTagPosDict[5], 0, 3)
        self.tomato = Ingredient(7, "Tomato", initTagPosDict[6], 0, 3)
        self.mixPlate = MixPlate(5, "Mix Plate", initTagPosDict[4], 0, 500, self.lettuce, self.tomato)

        self.chapter = 0 # c0: spash screen, c1: instructions, c2: gameplay, c3: completion
        self.complete = False

    def update(self, tagPosDict, cut_active=False, mixing=0):
        try:
            self.mixPlate.position = tagPosDict[4]
        except KeyError:
            pass
        try:
            self.lettuce.position = tagPosDict[5]
        except KeyError:
            pass
        try:
            self.tomato.position = tagPosDict[6]
        except KeyError:
            pass

        if self.chapter == 0:
            if mixing == 1:
                self.chapter = 1
        if self.chapter == 1:
            if mixing == 1 and cut_active:
                self.chapter = 2
        if self.chapter == 2:
            if cut_active:
                self.processCutting()
            if mixing == 1:
                self.processMixing()

    # TODO: Reference correct images
    def get_render_list(self):
        # {"image_path": "assets/chop.png", "x": 500, "y": 300, "scale": (64, 64), "frame": 2, "frame_width": 64}
        if self.chapter == 0:
            return [{"image_path": "assets/splash_screen.png", "x": 0, "y": 0, "scale": (1280, 720)}]
        elif self.chapter == 1:
            return [{"image_path": "assets/instructions.png", "x": 0, "y": 0, "scale": (1280, 720)}]
        elif self.chapter == 2:
            render_list = [
                {"image_path": "assets/gameplay_background.png", "x": 0, "y": 0, "scale": (1280, 720)},
                {"image_path": self.lettuce.image_path, "x": self.lettuce.position['top_left'][0], "y": self.lettuce.position['top_left'][1], "scale": (400, 400), "frame": min(self.lettuce.cutNum, self.lettuce.cutThreshold), "frame_width": 400},
                {"image_path": self.tomato.image_path, "x": self.tomato.position['top_left'][0], "y": self.tomato.position['top_left'][1], "scale": (400, 400), "frame": min(self.tomato.cutNum, self.tomato.cutThreshold), "frame_width": 400}
                # {"image_path": self.mixPlate.image_path, "x": self.mixPlate.position[0], "y": self.mixPlate.position[1], "scale": (100, 100)},
            ]
            return render_list
        elif self.chapter == 3:
            if self.complete:
                return [{"image_path": "assets/complete_success.png", "x": 0, "y": 0, "scale": (1280, 720)}]
            else:
                return [{"image_path": "assets/complete_failure.png", "x": 0, "y": 0, "scale": (1280, 720)}]
        
        return []
    
    def checkComplete(self):
        if self.servingZone.inZone(self.mixPlate.position) and self.mixPlate.processed and self.chapter == 2:
            self.complete = True
            self.chapter = 3
            return True
        return False
    
    def processCutting(self):
        if self.cuttingZone.inZone(self.lettuce.position):
            self.lettuce.processCut()
        elif self.cuttingZone.inZone(self.tomato.position):
            self.tomato.processCut()

    def processMixing(self):
        if self.mixingZone.inZone(self.mixPlate.position):
            success = self.mixPlate.processMix(self.lettuce, self.tomato)
            if not success and self.chapter == 2:
                self.chapter = 3
