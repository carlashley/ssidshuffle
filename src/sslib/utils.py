"""Basic utilities."""
from os import geteuid


def is_root() -> bool:
    """Truth test for determing the effective user id value is the root uid."""
    return geteuid() == 0
