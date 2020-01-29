import pygame

# ------------------------------------------------------------------------------
# PyGame: Keyboard Utility

def is_key_down(key):
    """
    Returns whether the specified key constant (usually pygame.K_<key>) is
    currently down.
    """
    return pygame.key.get_pressed()[key]


def is_key_pressed(key):
    """Deprecated. Use is_key_down() instead."""
    return pygame.key.get_pressed()[key]


def get_key_pressed(key):
    """Deprecated. Use is_key_pressed() instead."""
    return is_key_pressed(key)


