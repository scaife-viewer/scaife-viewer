from django import forms

from . import models


class ResourceListForm(forms.ModelForm):
    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owner"].initial = owner
        self.fields["owner"].widget = forms.HiddenInput()
        self.fields["owner"].widget.attrs["readonly"] = True


class ReadingListForm(ResourceListForm):
    class Meta:
        model = models.ReadingList
        fields = ["owner", "title", "description"]
