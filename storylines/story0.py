from gameObjects.ingredientPlate import Ingredient
from gameObjects.mixPlate import MixPlate
from tools.zone import Zone

class Story0:
    def __init__(self, initTagPosDict):
        self.story_id = 0
        self.story_name = "Basic Cutting"

        # Zones TODO: Adjust for setup
        self.cuttingZone = Zone("Cutting Zone", 0, 200, 0, 200)
        self.mixingZone = Zone("Mixing Zone", 200, 400, 0, 200)
        self.servingZone = Zone("Serving Zone", 400, 600, 0, 200)

        self.lettuce = Ingredient(6, "Lettuce", initTagPosDict[5], 0, 3)
        self.tomato = Ingredient(7, "Tomato", initTagPosDict[6], 0, 3)
        self.mixPlate = MixPlate(5, "Mix Plate", initTagPosDict[4], 0, 1, self.lettuce, self.tomato)

        self.complete = False

    def update(self, tagPosDict):
        self.lettuce.position = tagPosDict[5]
        self.tomato.position = tagPosDict[6]
        self.mixPlate.position = tagPosDict[4]

    def checkComplete(self):
        if self.servingZone.inZone(self.mixPlate.position) and self.mixPlate.processed:
            self.complete = True
            return True
        return False
    
    def processCutting(self):
        if self.cuttingZone.inZone(self.lettuce.position):
            self.lettuce.processCut()
        
        if self.cuttingZone.inZone(self.tomato.position):
            self.tomato.processCut()

    def processMixing(self):
        if self.mixingZone.inZone(self.mixPlate.position):
                self.mixPlate.processMix(self.lettuce, self.tomato)