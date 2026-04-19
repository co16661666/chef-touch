from .tagObject import TagObject

class Ingredient(TagObject):
    def __init__(self, tag_id, name, position, cutNum, cutThreshold, processed=False):
        super().__init__(tag_id, name, position, processed)
        self.cutNum = cutNum
        self.cutThreshold = cutThreshold

    def processCut(self):
        self.cutNum += 1

        if self.cutNum >= self.cutThreshold:
            self.processed = True
        
        print(self.cutNum, self.cutThreshold, self.processed)
        return True
