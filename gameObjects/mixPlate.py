from tagObject import TagObject

class MixPlate(TagObject):
    def __init__(self, tag_id, name, position, mixNum, mixThreshold, ing1, ing2):
        super().__init__(tag_id, name, position)
        self.ing1 = ing1
        self.ing2 = ing2

        self.mixNum = mixNum
        self.mixThreshold = mixThreshold

    def processMix(self, ing1, ing2):
        # Check if ingredients processed before mixing
        if ing1.processed == False or ing2.processed == False:
            print("Ingredients not processed for mixing")
            return False
        
        # Check if ingredients are correct
        if (ing1 == self.ing1 and ing2 == self.ing2) or (ing1 == self.ing2 and ing2 == self.ing1):
            self.mixNum += 1
        else:
            print("Incorrect ingredients for mixing")
            return False

        if self.mixNum >= self.mixThreshold:
            self.processed = True

        return True
