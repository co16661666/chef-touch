class TagObject:
    def __init__(self, tag_id, name, position, processed=False):
        self.tag_id = tag_id
        self.name = name
        self.position = position
        self.processed = processed