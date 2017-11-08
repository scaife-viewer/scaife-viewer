
class PassageDoesNotExist(Exception):

    def __init__(self, text, *args, **kwargs):
        self.text = text
        super().__init__(*args, **kwargs)
