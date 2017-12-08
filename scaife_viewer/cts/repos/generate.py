import glob
import os

from django.conf import settings

from MyCapytain.resources.collections.cts import (
    XmlCtsTextgroupMetadata,
    XmlCtsWorkMetadata,
    XmlCtsTextInventoryMetadata,
)
from MyCapytain.resources.prototypes.cts.inventory import CtsTextInventoryCollection
from MyCapytain.resolvers.utils import CollectionDispatcher


def load_repo_dirs():
    data_path = settings.CTS_LOCAL_DATA_PATH
    for entry in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, entry)):
            yield os.path.join(data_path, entry)


def main():
    assert settings.CTS_RESOLVER["type"] == "local"

    inventory_collection = CtsTextInventoryCollection(identifier="defaultTic")
    ti = XmlCtsTextInventoryMetadata("default")
    ti.parent = inventory_collection
    ti.set_label("Default collection", "eng")
    dispatcher = CollectionDispatcher(inventory_collection)

    for repo in load_repo_dirs():
        for text_group_path in glob.glob(f"{repo}/data/*/__cts__.xml"):
            with open(text_group_path) as f:
                text_group_metadata = XmlCtsTextgroupMetadata.parse(resource=f)
            dispatcher.dispatch(text_group_metadata, path=text_group_path)
            for work_path in glob.glob(f"{os.path.dirname(text_group_path)}/*/__cts__.xml"):
                with open(work_path) as f:
                    work_metadata = XmlCtsWorkMetadata.parse(resource=f, parent=text_group_metadata)
                for text_urn in work_metadata.texts:
                    text_metadata = dispatcher.collection[text_urn]
                    print(text_metadata)
                    text_path = os.path.join(os.path.dirname(work_path), "{text_group}.{work}.{version}.xml".format(
                        text_group=text_metadata.urn.textgroup,
                        work=text_metadata.urn.work,
                        version=text_metadata.urn.version,
                    ))
