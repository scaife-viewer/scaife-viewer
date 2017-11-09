from typing import Union

from MyCapytain.resources.prototypes.cts import inventory as cts

CtsCollectionMetadata = Union[
    cts.CtsTextgroupMetadata,
    cts.CtsWorkMetadata,
    cts.CtsTextMetadata,
]
