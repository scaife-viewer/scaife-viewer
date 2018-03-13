
class CollectionDoesNotExist(Exception):
    pass


class PassageDoesNotExist(Exception):

    def __init__(self, text, *args, **kwargs):
        self.text = text
        super().__init__(*args, **kwargs)


class InvalidPassageReference(Exception):
    pass
