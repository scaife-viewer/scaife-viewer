import os
from collections import namedtuple


Form = namedtuple("Form", ["form", "code", "lemma"])
TextKey = namedtuple("TextKey", ["short_key", "ref", "n"])


class Morphology:

    @classmethod
    def load(cls, root_dir):
        short_keys = {}
        with open(os.path.join(root_dir, "works.txt")) as f:
            for line in f:
                cts_urn, short_key = line.strip().split("\t")
                short_keys[cts_urn] = short_key
        forms = []
        with open(os.path.join(root_dir, "forms-normalised.txt")) as f:
            for line in f:
                form, _, code, lemma = line.strip().split("\t")
                forms.append(Form(form, code, lemma))
        text = {}
        with open(os.path.join(root_dir, "text.txt")) as f:
            for line in f:
                short_key, ref, n, form_key = line.strip().split("\t")
                text[TextKey(short_key, ref, n)] = form_key
        return cls(short_keys, forms, text)

    def __init__(self, short_keys, forms, text):
        self.short_keys = short_keys
        self.forms = forms
        self.text = text
