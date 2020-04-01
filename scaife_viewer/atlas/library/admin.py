from django.contrib import admin

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Node


class NodeAdmin(TreeAdmin):
    form = movenodeform_factory(Node)


admin.site.register(Node, NodeAdmin)
