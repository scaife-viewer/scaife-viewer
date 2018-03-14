from typing import List, Tuple

from .passage import Passage
from .toc import RefNode
from .utils import natural_keys


def heal(passage: Passage) -> Tuple[Passage, bool]:
    if not passage.exists():
        toc = passage.text.toc()
        healed_node = heal_recursive(toc.root, passage.reference.list)
        return Passage(passage.text, healed_node.reference), True
    return passage, False


def heal_recursive(node: RefNode, reference_list: List[str]) -> RefNode:
    first, *rest = reference_list
    healthy_node = heal_node(node, first)
    if rest:
        return heal_recursive(healthy_node, rest)
    else:
        return healthy_node


def heal_node(node: RefNode, r: str) -> RefNode:
    if not node.children:
        return node
    prev_child = node.children[0]
    r = natural_keys(r)
    for child in node.children:
        lsb = natural_keys(child.num.split(".")[-1])
        if lsb > r:
            break
        prev_child = child
    return prev_child
