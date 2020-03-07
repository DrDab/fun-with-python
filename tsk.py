from __future__ import print_function, division; """
TechSmart Kit (TSK) support library.

In particular it:
* Provides additional functionality to Python and PyGame.
* Implements the Skylark runtime.

Copyright (c) 2016-2018 TechSmart Inc.
"""
#
# This library's API is highly visible.
# Please do not make API changes without discussing with the rest of the team.
#

# NOTE: Be careful when extending the list of top-level imports since it can
#       noticeably delay the DPython interpreter startup time if the new
#       imports are not burned into interpreter filesystem or are not
#       statically linked to the interpreter.
#       
#       For rarely used imports consider the use of local imports instead.
import codecs
import json
import math
import os
import os.path
import pygame
import sys
import time as std_time
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Dict, List, Type, Union


# Support Python 2.7 or 3.x
try:
    unicode
except NameError:
    unicode = str


# ------------------------------------------------------------------------------
# Common Types and Constants

if TYPE_CHECKING:
    ImageFilePath = str
    ImageDescriptor = Union[ImageFilePath, 'ImageSheet']

_VERBOSE_EXPIRE_CALLS_TO_EVERY_X_SECONDS = False

_DEFAULT_FONT_FAMILY = 'Helvetica'
_DEFAULT_FONT_SIZE = 12


# ------------------------------------------------------------------------------
# Python: Extensions

def input_number(prompt):
    # type: (str) -> Union[int, float]
    """
    Prompts the user to input a number.
    
    Returns the number as an integer if it can be interpreted as one.
    Returns the number as a float if it can be interpreted as one.
    Otherwise raises a ValueError.
    """
    value = input(prompt)
    try:
        return int(value)
    except ValueError:
        return float(value)


# ------------------------------------------------------------------------------
# PyGame: Patches

def enable_pause_pygame_clock_during_input():
    """
    Patches input() to stop the PyGame clock while it is running.
    """
    old_input = __builtins__['input']

    def new_input(prompt=""):
        import pygame  # needs to be inside function for subsequent runs.

        old_ticking = pygame.time._get_ticking()
        pygame.time._set_ticking(False)
        try:
            response = old_input(prompt=prompt)
        finally:
            pygame.time._set_ticking(old_ticking)

        return response

    # NOTE: Patches input() after DPython patch.
    __builtins__['input'] = new_input


# ------------------------------------------------------------------------------
# PyGame: Sprites

class Sprite(object):
    """
    Represents a sprite, a persistent image on the screen with a particular location.
    """
    def __init__(self, image_descriptor, x, y):
        # type: (ImageDescriptor, float, float) -> None
        
        self.name = None  # Optional. Name of sprite as specified in the scene.
        
        self._set_image(image_descriptor, init=True)
        self.image_animation_rate = None
        self.x = x
        self.y = y
        self._scale = 1.0
        self._angle = 0
        self._flip_x = False
        self._flip_y = False
        
        self.visible = True
        self._destroyed = False

        self._creation_time = pygame.time.get_ticks()
        self._creation_frame_count = sky._frame_count

    # === Image ===
    
    def _get_image(self):
        return self._image_descriptor
    def _set_image(self, image_descriptor, init=False):
        if not init and image_descriptor == self._image_descriptor:
            return
        
        if not init:
            old_center = self.center
        
        if isinstance(image_descriptor, (str, unicode)):
            image_file_path = image_descriptor
            cells = [pygame.image.load(image_file_path)]
        elif isinstance(image_descriptor, ImageSheet):
            image_sheet = image_descriptor
            cells = image_sheet.cells
        else:
            raise ValueError(
                'Expected image descriptor to be an image file path or ImageSheet but found: %r' % 
                image_descriptor)
        
        self._image_descriptor = image_descriptor
        
        # Change cells
        self._current_cell_index = 0
        self._cells = cells
        self._transformed_cells = [None] * len(cells)
        
        # Reset cell animation timing
        self._time_current_cell_visible = 0
        
        if not init:
            self.center = old_center
    image = property(_get_image, _set_image, doc=
        """The static or animated image that this sprite displays.""")
    
    # The current image cell, before scale, flip, and rotate transformations.
    @property
    def _current_cell(self):
        return self._cells[self._current_cell_index]
    
    # The current image cell, after scale, flip, and rotate transformations.
    @property
    def _current_transformed_cell(self):
        transformed_cell = self._transformed_cells[self._current_cell_index]
        if transformed_cell is None:  # not yet cached
            cell = self._cells[self._current_cell_index]
            transformed_cell = self._transform_cell(cell)
            self._transformed_cells[self._current_cell_index] = transformed_cell
        return transformed_cell
    
    # Invalidates all cached transformed image cells.
    # Should be called whenever any fields that affect _transform_cell() are changed.
    def _invalidate_transformed_cells(self):
        for i in range(len(self._transformed_cells)):
            self._transformed_cells[i] = None
    
    def _get_image_animation_rate(self):
        return self._image_animation_rate
    def _set_image_animation_rate(self, image_animation_rate):
        if image_animation_rate is None:
            time_per_cell = None
        elif isinstance(image_animation_rate, (int, float)):
            if image_animation_rate > 0:
                time_per_cell = 1000/image_animation_rate
            elif image_animation_rate == 0:
                time_per_cell = -1
            else:
                raise ValueError('Expected animation rate to be >=0 but got %r.' % image_animation_rate)
        else:
            raise ValueError('Not a valid animation rate: %r' % image_animation_rate)
        
        # Update image animation rate
        self._image_animation_rate = image_animation_rate
        self._time_per_cell = time_per_cell
    image_animation_rate = property(_get_image_animation_rate, _set_image_animation_rate, doc=
        """
        The rate at which the animated sprite image advances.
        Does not apply to static sprite images.
        
        If None then 1 cell per frame (regardless of frame length),
        if a double then X cells per second.
        """)
    
    def _transform_cell(self, cell):
        transformed_cell = cell
        
        # Scale
        if self._scale != 1.0:
            transformed_cell = \
                pygame.transform.scale(transformed_cell, (
                    int(transformed_cell.get_width() * self._scale),
                    int(transformed_cell.get_height() * self._scale)
                ))
        
        # Flip
        if self._flip_x or self._flip_y:
            transformed_cell = pygame.transform.flip(transformed_cell, self._flip_x, self._flip_y)

        # Rotate
        if self._angle != 0:
            transformed_cell = pygame.transform.rotate(transformed_cell, self._angle)
        
        return transformed_cell

    # === Bounds ===
    
    # x = property(...)
    
    # y = property(...)
    
    @property
    def width(self):
        return self._current_transformed_cell.get_width()
    
    @property
    def height(self):
        return self._current_transformed_cell.get_height()
    
    @property
    def rect(self):
        # NOTE: pygame.Rect does not support non-integer values.
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def get_edge(self, edge_type):
        """
        Returns the specified edge of this sprite,
        which can be used with pygame.sprite.collide_rect().
        """
        return _Edge.of_rect(self.rect, edge_type)
    
    # === Center ===
    
    def _get_center_x(self):
        return self.x + (self.width / 2)
    def _set_center_x(self, center_x):
        self.x = center_x - (self.width / 2)
    center_x = property(_get_center_x, _set_center_x)
    
    def _get_center_y(self):
        return self.y + (self.height / 2)
    def _set_center_y(self, center_y):
        self.y = center_y - (self.height / 2)
    center_y = property(_get_center_y, _set_center_y)
    
    def _get_center(self):
        return (self.center_x, self.center_y)
    def _set_center(self, center):
        (self.center_x, self.center_y) = center
    center = property(_get_center, _set_center)
    
    # === Scale ===
    
    def _get_scale(self):
        return self._scale
    def _set_scale(self, scale):
        old_center = self.center
        
        self._scale = scale
        self._invalidate_transformed_cells()
        
        self.center = old_center
    scale = property(_get_scale, _set_scale)

    # === Flip ===

    def _get_flip_x(self):
        return self._flip_x
    def _set_flip_x(self, flipped):
        if self._flip_x == flipped:
            return
        
        self._flip_x = flipped
        self._invalidate_transformed_cells()
    flip_x = property(_get_flip_x, _set_flip_x)

    def _get_flip_y(self):
        return self._flip_y
    def _set_flip_y(self, flipped):
        if self._flip_y == flipped:
            return
        
        self._flip_y = flipped
        self._invalidate_transformed_cells()
    flip_y = property(_get_flip_y, _set_flip_y)
    
    # === Angle ===
    
    def _get_angle(self):
        return self._angle
    def _set_angle(self, angle):
        old_center = self.center
        
        self._angle = angle
        self._invalidate_transformed_cells()
        
        self.center = old_center
    angle = property(_get_angle, _set_angle)
    
    # === Behavior ===
    
    def update(self, delta_time):
        """
        Updates this sprite's animated image.
        
        Parameters:
        * delta_time -- The amount of time since the last call to update,
                        in milliseconds.
        """
        self._time_current_cell_visible += delta_time
        
        # Advance cell if appropriate
        if self._time_per_cell == -1:
            # Cell animation is disabled
            pass
        elif self._time_per_cell is None:
            # Time per cell is 1 frame/cell, regardless of frame duration
            if len(self._cells) > 1:
                self._current_cell_index += 1
                if self._current_cell_index == len(self._cells):
                    self._current_cell_index = 0
        else:
            # Time per cell is X seconds/cell
            time_per_cell = self._time_per_cell
            
            # Change current cell if enough time has passed
            if self._time_current_cell_visible >= time_per_cell:
                (num_cells_to_advance, self._time_current_cell_visible) = \
                    divmod(self._time_current_cell_visible, time_per_cell)
                self._current_cell_index = \
                    (self._current_cell_index + int(num_cells_to_advance)) % len(self._cells)
    
    def draw(self):
        """Draws this sprite if it is visible."""
        if self.visible:
            _get_window().blit(self._current_transformed_cell, [self.x, self.y])
    
    # === Lifecycle ===
    
    def destroy(self):
        """Marks this sprite for destruction."""
        self._destroyed = True
    
    @property
    def destroyed(self):
        """Whether this sprite has been marked for destruction."""
        return self._destroyed
    
    # === Distance ===
    
    def distance_to(self, x, y):
        """Returns the distance from this sprite's center to the specified point."""
        (center_x, center_y) = self.center
        return math.sqrt((center_x - x)**2 + (center_y - y)**2)


class _Edge(object):
    def __init__(self, rect):
        self.rect = rect
    
    @staticmethod
    def of_rect(rect, edge_type):
        if edge_type == 'top':
            return _Edge(pygame.Rect(rect.x, rect.y, rect.width, 1))
        elif edge_type == 'bottom':
            return _Edge(pygame.Rect(rect.x, rect.y + rect.height - 1, rect.width, 1))
        elif edge_type == 'left':
            return _Edge(pygame.Rect(rect.x, rect.y, 1, rect.height))
        elif edge_type == 'right':
            return _Edge(pygame.Rect(rect.x + rect.width - 1, rect.y, 1, rect.height))
        else:
            raise ValueError('Unrecognized edge type %r.' % edge_type)


# ------------------------------------------------------------------------------
# PyGame: Image Sheet

class ImageSheet(object):
    """
    Represents an image file that is divided into an (m x n) grid of cells.
    
    The cells are intended for use in an animation.
    """
    def __init__(self, file_path, row_count, column_count):
        # type: (ImageFilePath, int, int) -> None
        if not (row_count >= 1 and column_count >= 1):
            raise ValueError('Expected row and column count to be >= 1.')
        
        sheet_image = pygame.image.load(file_path)
        sheet_width, sheet_height = sheet_image.get_size()

        # Slice the sheet into cells
        cells = []
        (cell_width, cell_height) = (
            sheet_width // column_count,
            sheet_height // row_count
        )
        for gy in range(row_count):
            for gx in range(column_count):
                cell = sheet_image.subsurface(pygame.Rect(
                    gx * cell_width, gy * cell_height,
                    cell_width, cell_height))
                cells.append(cell)
        
        self.cells = cells
        self.row_count = row_count
        self.column_count = column_count


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


# ------------------------------------------------------------------------------
# PyGame: Internal Utility

# Returns the current display surface.
def _get_window():
    return pygame.display.get_surface()


# ------------------------------------------------------------------------------
# Skylark Runtime

# NOTE: Duplicate from calendar_file.py but unable to import since
#       calendar_file.py and tsk.py have to be standalone.
_IMAGE_FILE_EXTENSIONS = ['jpg', 'png']


class sky(object):
    """
    The Skylark runtime.
    
    Contains infrastructure for running Skylark programs. Also exports an API
    for interacting with Skylark programs.
    """
    
    # === Load Program ===
    
    _program_loaded = False
    _scenes = {}  # type: Dict[str, Dict]
    _modules = []  # type: List[ModuleType]
    _sprite_types = {}  # type: Dict[str, Type[Sprite]]
    _sprites = []  # type: List[Sprite]
    _desired_fps = None
    _frame_count = 0
    
    @staticmethod
    def load_program(_caller_distance=1):
        """
        Loads the Skylark program in the same directory as the caller.
        """
        
        caller_filepath = sys._getframe(_caller_distance).f_code.co_filename
        caller_parent_dirpath = os.path.dirname(os.path.abspath(caller_filepath))
        
        sky._load_program_in_directory(caller_parent_dirpath)
    
    @staticmethod
    def _load_program_in_directory(program_dirpath):
        all_filenames = os.listdir(program_dirpath)
        
        sky_filenames = [f for f in all_filenames if f.endswith('.sky')]
        skybg_filenames = [f for f in all_filenames if f.endswith('.skybg')]
        skys_filenames = [f for f in all_filenames if f.endswith('.skys')]
        json_filenames = [f for f in all_filenames if f.endswith('.json')]
        
        # Load sprite type meta data
        sky._sprite_type_metadata = {}
        for fn in json_filenames:
            with codecs.open(fn, 'r', encoding='utf8') as f:
                type_name = fn[:-len('.json')]
                sky._sprite_type_metadata[type_name] = json.load(f)
        
        # Locate sprite types and standalone modules
        sprite_type_infos = []
        module_names = []
        for sky_sibling in sky_filenames:
            module_name = sky_sibling[:-len('.sky')]
            for ext in _IMAGE_FILE_EXTENSIONS:
                image_filename = '%s.%s' % (module_name, ext)
                if image_filename in all_filenames:
                    sprite_type_infos.append((module_name, image_filename))
                    break
            else:
                module_names.append(module_name)
        
        # Locate scenes
        scene_names = [f[:-len('.skys')] for f in skys_filenames]
        
        # Load scenes
        sky._scenes = {
            scene_name: sky._load_scene(scene_name)
            for scene_name in scene_names
        }
        
        # Load modules
        sky._modules = [
            __import__(module_name)
            for module_name in module_names
        ]

        # Load sprite types
        sky._sprite_types = {
            type_name: sky._create_sprite_type_from_module(__import__(type_name), image_filename)
            for (type_name, image_filename) in sprite_type_infos
        }
        
        # Load background type names
        sky._background_types = [f[:-len('.skybg')] for f in skybg_filenames]
        
        # Initialize sprites
        sky._sprites = []
        
        sky._program_loaded = True
    
    @staticmethod
    def _load_scene(scene_name):
        with codecs.open('%s.skys' % scene_name, 'r', encoding='utf8') as f:
            return json.load(f)
    
    @staticmethod
    def _create_sprite_type_from_module(sprite_type_module, image_filename):
        # type: (...) -> Type[Sprite]
        methods = {
            fn: staticmethod(f) \
                if hasattr(f, '__name__') and f.__name__.startswith('before_program_starts') \
                else f
            for (fn, f) in sprite_type_module.__dict__.items()
        }
        sprite_type = type(sprite_type_module.__name__, (Sprite,), methods)  # type: Type[Sprite]
        sprite_type._image_filename = image_filename  # type: ignore  # annotate type object
        return sprite_type

    # === Run Program ===
    
    _clock = None

    @staticmethod
    def run_program():
        """
        Runs the currently loaded Skylark program.
        
        If no Skylark program is currently loaded, automatically
        loads the Skylark program in the same directory as the caller.
        """
        if not sky._program_loaded:
            sky.load_program(_caller_distance=2)
        
        # Locate default scene, if one exists
        # TODO: Consider supporting the recognition of a default scene
        #       in the presence of multiple scenes. Suggest a key like
        #       'is_default' in the scene file to distinguish.
        if len(sky._scenes) == 1:
            (default_scene,) = sky._scenes.values()
        else:
            default_scene = None

        # Setup PyGame and default scene, if this is a graphical program
        if default_scene is not None:
            # Initialize PyGame early (if we would have later) so that
            # before_program_starts*() can interact with PyGame if desired
            pygame.init()

            # Stops PyGame clock while waiting for input from the user
            enable_pause_pygame_clock_during_input()

            # Setup clock before before_program_starts*() events are run so that
            # they can interact with the clock.
            sky._clock = pygame.time.Clock()

            # Setup font
            # NOTE: Use the internal version of pygame.freetype because we don't
            #       want to import the public version because that import has
            #       a side effect. In particular user programs that otherwise
            #       would need to import pygame.freetype explicitly would no
            #       longer need to make such an import.
            sky.font = pygame._freetype.SysFont(_DEFAULT_FONT_FAMILY, _DEFAULT_FONT_SIZE)
            sky.font.origin = True  # baseline

            # Setup the default scene (if applicable) before
            # before_program_starts*() events are run so that they can interact
            # with the scene.
            sky._set_scene(default_scene)

        # Call before_program_starts*() methods on all modules
        sky._call_static_event_handlers('before_program_starts')
        
        # Run main loop, if this is a graphical program
        if default_scene is not None:
            sky._run_main_loop()

    @staticmethod
    def _set_scene(scene):
        sky.window = pygame.display.set_mode(scene['size'])

        sky._desired_fps = scene.get('desired_fps')
        if sky._desired_fps is None:
            # Use deprecated default FPS
            sky._desired_fps = 30  # arbitrary

        for sprite_info in scene['sprites']:
            sprite = sky.create_sprite(sprite_info['type'], 0, 0)
            if 'name' in sprite_info:
                sprite.name = sprite_info['name']
            if 'visible' in sprite_info:
                sprite.visible = sprite_info['visible']
            
            # Set transformation properties,
            # which hold (center_x, center_y) fixed but could alter (x, y)
            if 'angle' in sprite_info:
                sprite.angle = sprite_info['angle']
            if 'flip_x' in sprite_info:
                sprite.flip_x = sprite_info['flip_x']
            if 'flip_y' in sprite_info:
                sprite.flip_y = sprite_info['flip_y']
            if 'scale' in sprite_info:
                sprite.scale = sprite_info['scale']
            
            # Set location after all transformation properties
            sprite.x = sprite_info['x']
            sprite.y = sprite_info['y']

        sky.draw(custom=False)
        
    @staticmethod
    def _run_main_loop():
        sky.draw(custom=False)
        while True:
            sky._update()
            sky.draw()
            sky.tick()

    # === Update ===

    @staticmethod
    def _update():
        """
        Updates the state of all sprites in the program.
        
        Processes all outstanding events from the event queue.
        Calls all pending event handlers as appropriate.
        """
        for event in pygame.event.get():
            # Quit if the close box was clicked
            if event.type == pygame.QUIT:
                sys.exit(0)
            
            # Run deferred function call
            if event.type == pygame.USEREVENT and \
                    hasattr(event, 'kind') and \
                    event.kind == 'ts.run':
                event.func()

            # Trigger when_x_key_pressed events
            if event.type == pygame.KEYDOWN:
                sky._call_all_key_pressed_events(event.key)

            # Trigger when_x_key_released events
            if event.type == pygame.KEYUP:
                sky._call_all_key_released_events(event.key)

            # Trigger mouse button pressed events
            if event.type == pygame.MOUSEBUTTONDOWN:
                sky._call_all_mouse_button_is_pressed_events()
                sky._call_all_mouse_button_is_pressed_on_sprite_events()

            # Trigger mouse button released events
            if event.type == pygame.MOUSEBUTTONUP:
                sky._call_all_mouse_button_is_released_events()
                sky._call_all_mouse_button_is_released_on_sprite_events()

        # Call every_frame*() methods
        sky._call_hybrid_event_handlers('every_frame')
        
        sky._call_all_key_state_events()
        sky._call_all_mouse_button_state_events()
        sky._call_all_sprite_mouse_button_state_events()

        sky._call_all_collide_events_for_sprite_types()
        sky._call_all_collide_events_for_edge_of_window()

        sky._call_after_x_seconds_events()
        sky._call_after_x_frames_events()

        sky._call_x_seconds_after_created_events()
        sky._call_x_frames_after_created_events()

        sky._call_every_x_seconds_events()
        sky._call_every_x_frames_events()

        # Update all sprites
        for sprite in sky._sprites:
            sprite.update(sky.delta_time())
        
        # Remove any destroyed sprites from the sprite list
        for (i, sprite) in reversed(list(enumerate(sky._sprites))):
            if sprite.destroyed:
                del sky._sprites[i]
    
    @staticmethod
    def _call_all_key_state_events():
        for key_event_handler in sky._hybrid_event_handlers('while_x_key_is_down'):
            (key,) = key_event_handler.args
            if pygame.key.get_pressed()[key]:
                key_event_handler.call()

        for key_event_handler in sky._hybrid_event_handlers('while_x_key_is_up'):
            (key,) = key_event_handler.args
            if not pygame.key.get_pressed()[key]:
                key_event_handler.call()

    @staticmethod
    def _call_all_key_pressed_events(key_pressed):
        for key_event_handler in sky._hybrid_event_handlers('when_x_key_is_pressed'):
            (key,) = key_event_handler.args
            if key == key_pressed:
                key_event_handler.call()

    @staticmethod
    def _call_all_key_released_events(key_released):
        for key_event_handler in sky._hybrid_event_handlers('when_x_key_is_released'):
            (key,) = key_event_handler.args
            if key == key_released:
                key_event_handler.call()

    @staticmethod
    def _call_all_mouse_button_state_events():
        is_mouse_pressed = any(pygame.mouse.get_pressed())
        if is_mouse_pressed:
            for mouse_event_handler in sky._hybrid_event_handlers('while_mouse_button_is_down_on_window'):
                mouse_event_handler.call()
        else:
            for mouse_event_handler in sky._hybrid_event_handlers('while_mouse_button_is_up_on_window'):
                mouse_event_handler.call()

    @staticmethod
    def _call_all_mouse_button_is_pressed_events():
        for mouse_event_handler in sky._hybrid_event_handlers('when_mouse_button_is_pressed_on_window'):
            mouse_event_handler.call()

    @staticmethod
    def _call_all_mouse_button_is_released_events():
        for mouse_event_handler in sky._hybrid_event_handlers('when_mouse_button_is_released_on_window'):
            mouse_event_handler.call()

    @staticmethod
    def _call_all_mouse_button_is_pressed_on_sprite_events():
        sky._call_all_mouse_button_is_x_on_sprite_events('when_mouse_button_is_pressed_on_x')

    @staticmethod
    def _call_all_mouse_button_is_released_on_sprite_events():
        sky._call_all_mouse_button_is_x_on_sprite_events('when_mouse_button_is_released_on_x')
    
    @staticmethod
    def _call_all_mouse_button_is_x_on_sprite_events(event_handler_name):
        (mouse_x, mouse_y) = pygame.mouse.get_pos()

        top_most_sprite = sky._sprite_at(mouse_x, mouse_y)
        if top_most_sprite is not None:
            for (event_handler, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(event_handler_name):
                (sprite_ref,) = event_handler.args
                sprite = sky._resolve_sprite_instance_reference(sprite_ref, event_handler, self_sprite)
                
                if sprite == top_most_sprite:
                    event_handler.call(sprite)

    @staticmethod
    def _call_all_sprite_mouse_button_state_events():
        # Locate pressed_sprite
        is_mouse_pressed = any(pygame.mouse.get_pressed())
        if is_mouse_pressed:
            (mouse_x, mouse_y) = pygame.mouse.get_pos()
            pressed_sprite = sky._sprite_at(mouse_x, mouse_y)
        else:
            pressed_sprite = None
        
        # Locate unpressed_sprites
        unpressed_sprites = list(sky._sprites)  # capture
        if pressed_sprite is not None:
            unpressed_sprites.remove(pressed_sprite)
        
        if pressed_sprite is not None:
            for (event_handler, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(
                    'while_mouse_button_is_down_on_x'):
                (sprite_ref,) = event_handler.args
                sprite = sky._resolve_sprite_instance_reference(sprite_ref, event_handler, self_sprite)
                
                if sprite == pressed_sprite:
                    event_handler.call(sprite)
        
        for (event_handler, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(
                'while_mouse_button_is_up_on_x'):
            (sprite_ref,) = event_handler.args
            sprite = sky._resolve_sprite_instance_reference(sprite_ref, event_handler, self_sprite)
            
            if sprite in unpressed_sprites:
                event_handler.call(sprite)

    @staticmethod
    def _call_all_collide_events_for_sprite_types():
        collide_calls = []
        
        def prepare_call_collide_events(event_name, collide_handler):
            for (collide_method, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(event_name):
                (sprite_1_ref, sprite_2_type_name) = collide_method.args
                sprite_1 = sky._resolve_sprite_instance_reference(sprite_1_ref, collide_method, self_sprite)
                
                if not sprite_1.visible:
                    continue
                
                sprite_2_type = sky._sprite_types[sprite_2_type_name]
                for sprite_2 in sky._sprites:
                    if type(sprite_2) != sprite_2_type:
                        continue
                    if sprite_2 == sprite_1:  # don't collide with self
                        continue
                    if not sprite_2.visible:
                        continue

                    collide_method_with_args = _functools_partial(collide_method.call, sprite_1, sprite_2)
                    was_collided = collide_method.data['_was_collided'].get(sprite_2, False)
                    is_collided = pygame.sprite.collide_rect(sprite_1, sprite_2)

                    collide_handler(collide_method_with_args, is_collided, was_collided)

                    collide_method.data['_was_collided'][sprite_2] = is_collided

        def handle_when_x_starts_colliding_with_any(collide_method_with_args, is_collided, was_collided):
            if is_collided and not was_collided:
                collide_calls.append(collide_method_with_args)
        
        def handle_while_x_is_colliding_with_any(collide_method_with_args, is_collided, was_collided):
            if is_collided:
                collide_calls.append(collide_method_with_args)
        
        def handle_when_x_stops_colliding_with_any(collide_method_with_args, is_collided, was_collided):
            if not is_collided and was_collided:
                collide_calls.append(collide_method_with_args)
        
        def handle_while_x_is_not_colliding_with_any(collide_method_with_args, is_collided, was_collided):
            if not is_collided:
                collide_calls.append(collide_method_with_args)
        
        def call_collide_events():
            for cc in collide_calls:
                cc()
        
        # Call collision-related event handlers
        # 
        # NOTE: Collision handlers are not called immediately because
        #       handlers that change the position of sprites might change
        #       whether other handlers are triggered or not.
        prepare_call_collide_events('when_x_starts_colliding_with_any_x', handle_when_x_starts_colliding_with_any)
        prepare_call_collide_events('while_x_is_colliding_with_any_x', handle_while_x_is_colliding_with_any)
        prepare_call_collide_events('when_x_stops_colliding_with_any_x', handle_when_x_stops_colliding_with_any)
        prepare_call_collide_events('while_x_is_not_colliding_with_any_x', handle_while_x_is_not_colliding_with_any)
        call_collide_events()
    
    @staticmethod
    def _call_all_collide_events_for_edge_of_window():
        collide_calls = []
        
        def prepare_call_collide_events(event_name, collide_handler):
            for (collide_method, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(event_name):
                (sprite_1_ref, edge_descriptor) = collide_method.args
                sprite_1 = sky._resolve_sprite_instance_reference(sprite_1_ref, collide_method, self_sprite)
                
                if not sprite_1.visible:
                    continue
                
                collide_method_with_args = _functools_partial(collide_method.call, sprite_1)
                was_collided = collide_method.data['_was_collided'].get(edge_descriptor, False)
                is_collided = sky.is_colliding_with_edge_of_window(sprite_1, edge_descriptor)

                collide_handler(collide_method_with_args, is_collided, was_collided)

                collide_method.data['_was_collided'][edge_descriptor] = is_collided
        
        def handle_when_x_starts_colliding_with_x_edge_of_window(collide_method, is_collided, was_collided):
            if is_collided and not was_collided:
                collide_calls.append(collide_method)
        
        def handle_while_x_is_colliding_with_x_edge_of_window(collide_method, is_collided, was_collided):
            if is_collided:
                collide_calls.append(collide_method)
        
        def handle_when_x_stops_colliding_with_x_edge_of_window(collide_method, is_collided, was_collided):
            if not is_collided and was_collided:
                collide_calls.append(collide_method)
        
        def handle_while_x_is_not_colliding_with_x_edge_of_window(collide_method, is_collided, was_collided):
            if not is_collided:
                collide_calls.append(collide_method)
        
        def call_collide_events():
            for cc in collide_calls:
                cc()
        
        # Call collision-related event handlers
        #
        # NOTE: Collision handlers are not called immediately because
        #       handlers that change the position of sprites might change
        #       whether other handlers are triggered or not.
        prepare_call_collide_events('when_x_starts_colliding_with_x_edge_of_window', handle_when_x_starts_colliding_with_x_edge_of_window)
        prepare_call_collide_events('while_x_is_colliding_with_x_edge_of_window', handle_while_x_is_colliding_with_x_edge_of_window)
        prepare_call_collide_events('when_x_stops_colliding_with_x_edge_of_window', handle_when_x_stops_colliding_with_x_edge_of_window)
        prepare_call_collide_events('while_x_is_not_colliding_with_x_edge_of_window', handle_while_x_is_not_colliding_with_x_edge_of_window)
        call_collide_events()

    @staticmethod
    def _call_after_x_seconds_events():
        sorted_after_x_seconds_event_handlers = sorted(
            [event_handler for event_handler in sky._hybrid_event_handlers('after_x_seconds')],
            key=lambda event_handler: event_handler.args[0]
        )
        for periodic_event_handler in sorted_after_x_seconds_event_handlers:
            now = pygame.time.get_ticks()  # capture
            (trigger_time,) = periodic_event_handler.args
            trigger_time *= 1000  # convert to milliseconds

            was_triggered = periodic_event_handler.data['_was_triggered'][0]
            if was_triggered:
                continue

            if now >= trigger_time:
                periodic_event_handler.call()
                was_triggered = True

            periodic_event_handler.data['_was_triggered'][0] = was_triggered

    @staticmethod
    def _call_after_x_frames_events():
        sorted_after_x_frames_event_handlers = sorted(
            [event_handler for event_handler in sky._hybrid_event_handlers('after_x_frames')],
            key=lambda event_handler: event_handler.args[0]
        )
        for periodic_event_handler in sorted_after_x_frames_event_handlers:
            current_frame_count = sky._frame_count  # capture
            (trigger_frame_count,) = periodic_event_handler.args

            was_triggered = periodic_event_handler.data['_was_triggered'][0]
            if was_triggered:
                continue

            if current_frame_count >= trigger_frame_count:
                periodic_event_handler.call()
                was_triggered = True

            periodic_event_handler.data['_was_triggered'][0] = was_triggered

    @staticmethod
    def _call_x_seconds_after_created_events():
        x_seconds_after_created_event_handlers = []
        for sprite in sky._sprites:
            x_seconds_after_created_event_handlers.extend(
                sky._instance_event_handlers(sprite, 'x_seconds_after_created')
            )
        sorted_x_seconds_after_created_event_handlers = sorted(
            x_seconds_after_created_event_handlers,
            key=lambda event_handler: event_handler.args[0]
        )
        for periodic_event_handler in sorted_x_seconds_after_created_event_handlers:
            this_sprite = periodic_event_handler._obj
            creation_time = this_sprite._creation_time

            now = pygame.time.get_ticks()  # capture
            (trigger_time,) = periodic_event_handler.args
            trigger_time *= 1000  # convert to milliseconds

            was_triggered = periodic_event_handler.data['_was_triggered'][0]
            if was_triggered:
                continue

            if now - creation_time >= trigger_time:
                periodic_event_handler.call()
                was_triggered = True

            periodic_event_handler.data['_was_triggered'][0] = was_triggered

    @staticmethod
    def _call_x_frames_after_created_events():
        x_frames_after_created_event_handlers = []
        for sprite in sky._sprites:
            x_frames_after_created_event_handlers.extend(
                sky._instance_event_handlers(sprite, 'x_frames_after_created')
            )
        sorted_x_frames_after_created_event_handlers = sorted(
            x_frames_after_created_event_handlers,
            key=lambda event_handler: event_handler.args[0]
        )
        for periodic_event_handler in sorted_x_frames_after_created_event_handlers:
            this_sprite = periodic_event_handler._obj
            creation_frame_count = this_sprite._creation_frame_count

            current_frame_count = sky._frame_count  # capture
            (trigger_frame_count,) = periodic_event_handler.args

            was_triggered = periodic_event_handler.data['_was_triggered'][0]
            if was_triggered:
                continue

            if current_frame_count - creation_frame_count >= trigger_frame_count:
                periodic_event_handler.call()
                was_triggered = True

            periodic_event_handler.data['_was_triggered'][0] = was_triggered

    @staticmethod
    def _call_every_x_seconds_events():
        for periodic_event_handler in sky._hybrid_event_handlers('every_x_seconds'):
            now = pygame.time.get_ticks()  # capture
            (period,) = periodic_event_handler.args
            period *= 1000  # convert to milliseconds

            next_trigger_time = periodic_event_handler.data['_next_trigger_time'][0]
            if next_trigger_time is None:
                next_trigger_time = period
                num_advances = 0
                while next_trigger_time < now:
                    next_trigger_time += period
                    num_advances += 1
                if num_advances >= 2 and _VERBOSE_EXPIRE_CALLS_TO_EVERY_X_SECONDS:
                    print('*** Expired %d calls to every_x_seconds on program start' % (num_advances - 1))

            if now >= next_trigger_time:
                periodic_event_handler.call()

                now = pygame.time.get_ticks()  # recapture
                num_advances = 0
                while next_trigger_time < now:
                    next_trigger_time += period
                    num_advances += 1
                if num_advances >= 2 and _VERBOSE_EXPIRE_CALLS_TO_EVERY_X_SECONDS:
                    print('*** Expired %d calls to every_x_seconds while running program' % (num_advances - 1))
            
            periodic_event_handler.data['_next_trigger_time'][0] = next_trigger_time

    @staticmethod
    def _call_every_x_frames_events():
        for periodic_event_handler in sky._hybrid_event_handlers('every_x_frames'):
            current_frame_count = sky._frame_count  # capture
            (frame_period,) = periodic_event_handler.args

            next_trigger_frame = periodic_event_handler.data['_next_trigger_frame'][0]
            if next_trigger_frame is None:
                next_trigger_frame = frame_period

            if current_frame_count >= next_trigger_frame:
                periodic_event_handler.call()
                next_trigger_frame += frame_period

            periodic_event_handler.data['_next_trigger_frame'][0] = next_trigger_frame

    # === Draw ===

    @staticmethod
    def draw(custom=True):
        """
        Draws everything to the window immediately.
        """
        _get_window().fill((255, 255, 255))
        sky._draw_sprites()
        if custom:
            sky._call_hybrid_event_handlers('always_draw')
        pygame.display.flip()

    @staticmethod
    def _draw_sprites():
        """
        Draws all sprites.
        
        Note that the display must still be flipped in order for the sprites
        to actually show up on the screen.
        """
        # Draw all sprites
        for sprite in sky._sprites:
            sprite.draw()

    # === Time ===

    @staticmethod
    def delta_time():
        """
        Returns the time elapsed during the last frame (in milliseconds).
        """
        return sky._clock.get_time()

    @staticmethod
    def tick():
        """
        Waits until the end of the current frame.
        """
        sky._clock.tick(sky._desired_fps)
        sky._frame_count += 1

    @staticmethod
    def wait(milliseconds):
        """
        Mimics PyGame's time.wait function but pauses PyGame clock while waiting.
        """
        old_ticking = pygame.time._get_ticking()
        pygame.time._set_ticking(False)
        try:
            return pygame.time._wait_generic(milliseconds, std_time.time)
        finally:
            pygame.time._set_ticking(old_ticking)

    # === Program Variables ===
    
    class _ProgramVariables(object):
        def __getattr__(self, name):
            # Provide better error message than the default AttributeError
            raise AttributeError('program variable %r is not defined' % name)

    program = _ProgramVariables()
    program.__doc__ = 'Contains user-defined program variables.'
    
    # === Sprites ===
    
    class _Sprites(object):
        def __getattr__(self, name):
            for sprite in sky._sprites:
                if sprite.name == name:
                    return sprite
            raise NameError('sprite instance %r is not defined in the current scene' % name)
        
        def __setattr__(self, name, value):
            if name in ['__doc__']:  # whitelist
                return object.__setattr__(self, name, value)
            raise TypeError('cannot assign to members of tsk.sky.sprites')
        
        def __delattr__(self, name):
            raise TypeError('cannot delete members of tsk.sky.sprites')
    
    sprites = _Sprites()
    sprites.__doc__ = 'Contains sprite instances defined in the current scene.'
    
    # --- Sprites: Create ---

    @staticmethod
    def create_sprite(sprite_type_name, center_x, center_y):
        """
        Creates a sprite of the specified type at the specified center position,
        returning the created sprite.
        """
        return sky._create_sprite(sprite_type_name, center_x, center_y)
        
    @staticmethod
    def _create_sprite(sprite_type_name, center_x, center_y, _z_index=-1):
        sprite_type = sky._sprite_types.get(sprite_type_name)
        if sprite_type is None:
            raise ValueError('No such sprite type: ' + sprite_type_name)

        # Determine if metadata has spritesheet information for the sprite type
        sprite_type_metadata = sky._sprite_type_metadata.get(sprite_type_name, {})
        rows = sprite_type_metadata.get('rows', None)
        cols = sprite_type_metadata.get('cols', None)

        # Determine if the sprite's image should be a spritesheet or a static image
        if rows is not None and cols is not None:
            image = ImageSheet(sprite_type._image_filename, rows, cols)
        else:
            image = sprite_type._image_filename
            
        sprite = sprite_type(image, 0, 0)
        sprite.center_x = center_x
        sprite.center_y = center_y

        # Default to scene fps
        sprite.image_animation_rate = sky._desired_fps
        
        if _z_index == -1:
            sky._sprites.append(sprite)
        else:
            sky._sprites.insert(_z_index, sprite)
        
        # NOTE: By calling event handlers immediately, it implies that a
        #       sprite creation block can implicitly call other
        #       user-defined functions.
        sky._call_instance_event_handlers(sprite, 'when_created')
        
        return sprite
    
    # Deprecated. Deferrals will be too difficult to emulate in the likely event
    # that the Skylark run loop is altered to use code generation.
    @staticmethod
    def _call_soon(func):
        pygame.event.post(pygame.event.Event(
            pygame.USEREVENT,
            kind='ts.run',
            func=func))
    
    # --- Sprites: Get ---
    
    @staticmethod
    def get_sprites_of_type(sprite_type_name):
        """
        Returns a list of sprites that are of the specified sprite type name.
        """
        return [s for s in sky._sprites if type(s).__name__ == sprite_type_name]
        
    @staticmethod
    def _get_type_name_of_sprite(sprite):
        return type(sprite).__name__

    @staticmethod
    def _sprite_at(x, y):
        """
        Returns the top-most visible sprite that collides with the given x, y
        parameters or None.
        """
        sprites_colliding_with_mouse = list(reversed([
            sprite
            for sprite in sky._sprites
            if sprite.rect.collidepoint(x, y) and sprite.visible
        ]))

        return sprites_colliding_with_mouse[0] \
            if len(sprites_colliding_with_mouse) >= 1 \
            else None
    
    # --- Sprites: Collisions ---

    @staticmethod
    def is_colliding_with_sprite_of_type(sprite_instance, sprite_type_name):
        """
        Returns True if the sprite instance is colliding with any sprite of the
        specified type name, otherwise False.
        """
        if sprite_instance not in sky._sprites:
            return False
        if not sprite_instance.visible:
            return False

        return any([
            pygame.sprite.collide_rect(sprite_instance, sprite)
            for sprite in sky.get_sprites_of_type(sprite_type_name)
        ])
    
    @staticmethod
    def is_colliding_with_sprite(sprite_instance_1, sprite_instance_2):
        """
        Returns True if the specified sprite instances are colliding with
        each other, otherwise False.
        """
        if sprite_instance_1 not in sky._sprites or sprite_instance_2 not in sky._sprites:
            return False
        if not sprite_instance_1.visible or not sprite_instance_2.visible:
            return False

        return pygame.sprite.collide_rect(sprite_instance_1, sprite_instance_2)

    @staticmethod
    def is_colliding_with_edge_of_window(sprite_instance, edge_descriptor):
        """
        Returns True if the sprite instance is colliding with the specified edge
        of the PyGame window, otherwise False.

        The edge may be "any", "top", "bottom", "left", or "right".
        """
        if sprite_instance not in sky._sprites:
            return False
        if not sprite_instance.visible:
            return False

        if edge_descriptor == 'any':
            edge_types = ['top', 'bottom', 'left', 'right']
        elif edge_descriptor in ['top', 'bottom', 'left', 'right']:
            edge_types = [edge_descriptor]
        else:
            raise ValueError('Invalid edge descriptor: %s.' % edge_descriptor)

        return any([
            pygame.sprite.collide_rect(
                sprite_instance,
                _Edge.of_rect(_get_window().get_rect(), edge_type))
            for edge_type in edge_types
        ])
        
    # === Backgrounds ===
    
    @staticmethod
    def set_background(background_type):
        """
        Sets the background of the current scene by destroying the old background, if one exists, 
        and creating a new background of the specified background type.
        """
        # Destroy old background, if one exists. NOTE: Assumes at most one background, 
        # which if present, is at the beginning of the list of sprites.
        if len(sky._sprites) > 0:
            if sky._is_sprite_a_background(sky._sprites[0]):
                sky._sprites[0].destroy()
        
        # Create new background and reposition at top-left
        background = sky._create_sprite(background_type, center_x=0, center_y=0, _z_index=0)
        (background.x, background.y) = (0, 0)
        
    @staticmethod
    def _is_sprite_a_background(sprite):
        return sky._get_type_name_of_sprite(sprite) in sky._background_types

    # === Fonts ===

    @staticmethod
    def set_font(filename):
        import pygame.freetype

        old_font = sky.font
        if old_font is None:
            raise ValueError('sky.font not initialized')

        old_size = old_font.size
        old_fgcolor = old_font.fgcolor
        old_origin = old_font.origin

        sky.font = pygame.freetype.Font(filename, old_size)
        sky.font.origin = old_origin
        sky.font.fgcolor = old_fgcolor

    # === Events ===
    
    @staticmethod
    def arguments(*args):
        """
        Decorates an event function to fill in arguments for it.
        
        Required for any event function whose name contains one or
        more "_x_" parameters.
        """
        def decorate(func):
            func.args = args
            return func
        return decorate
    
    # === Event Invocation & Introspection ===
    
    """
    An Event (like 'before_program_starts') describes some kind of happening that
    can occur.
    
    An Event Handler (like 'def before_program_starts_1(...)') is a particular
    function or method that is called when an Event occurs.
    
    There are a few kinds of events:
    
    * Static Events - Always occur independently of any particular sprite instance.
    * Hybrid Events - May or may not occur in the context of a sprite instance.
    * Instance Events - Always occur in the context of a particular sprite instance.
    
    Static and Hybrid Events can be declared anywhere. Instance Events may only
    be declared within a Sprite Type.
    """
    
    @staticmethod
    def _call_static_event_handlers(prefix, *args, **kwargs):
        for event_handler in sky._static_event_handlers(prefix):
            event_handler.call(*args, **kwargs)
    
    @staticmethod
    def _static_event_handlers(prefix):
        for module in sky._modules:
            for x in sky._functions_that_start_with(module, prefix):
                yield x
        for sprite_type in sky._sprite_types.values():
            for x in sky._functions_that_start_with(sprite_type, prefix):
                yield x
    
    @staticmethod
    def _call_hybrid_event_handlers(prefix, *args, **kwargs):
        for event_handler in sky._hybrid_event_handlers(prefix):
            event_handler.call(*args, **kwargs)
    
    @staticmethod
    def _hybrid_event_handlers(prefix):
        for (event_handler, self_sprite) in sky._hybrid_event_handlers_with_self_sprite(prefix):
            yield event_handler
    
    @staticmethod
    def _hybrid_event_handlers_with_self_sprite(prefix):
        for module in sky._modules:
            for x in sky._functions_that_start_with(module, prefix):
                yield (x, None)
        for sprite in sky._sprites:
            for x in sky._methods_that_start_with(sprite, prefix):
                yield (x, sprite)
    
    @staticmethod
    def _call_instance_event_handlers(sprite, prefix, *args, **kwargs):
        for event_handler in sky._instance_event_handlers(sprite, prefix):
            event_handler.call(*args, **kwargs)
    
    @staticmethod
    def _instance_event_handlers(sprite, prefix):
        return sky._methods_that_start_with(sprite, prefix)
    
    # === Event Parameters ===
    
    @staticmethod
    def _resolve_sprite_instance_reference(sprite_ref, event_handler, self_sprite):
        if sprite_ref == 'self':
            if self_sprite is None:
                raise NameError(
                    'Function %r references self which is not available.' % 
                    event_handler.__name__)
            return self_sprite
        elif sprite_ref.startswith('sprites.'):
            sprite_instance_name = sprite_ref[len('sprites.'):]
            try:
                return getattr(sky.sprites, sprite_instance_name)
            except NameError:
                raise NameError(
                    ('Method %r references sprite instance %r '
                     'not defined in the current scene.') % 
                    (event_handler.__name__, sprite_instance_name))
        else:
            raise NameError(
                'Method %r references invalid sprite: %r' % 
                (event_handler, sprite_ref))
    
    # === Utility ===

    @staticmethod
    def _functions_that_start_with(module, prefix):
        return sorted([
            _Handler(module, f)
            for f in module.__dict__
            if f.startswith(prefix)
        ], key=lambda f: f.__name__)

    @staticmethod
    def _methods_that_start_with(sprite, prefix):
        return sorted([
            _Handler(sprite, m)
            for m in type(sprite).__dict__
            if m.startswith(prefix)
        ], key=lambda m: m.__name__)


class _Handler:
    """
    Wraps the function or method underlying an event handler on a particular object.
    
    Provides a data dictionary that can be used to store stateful information
    related to handlers.
    """
    def __init__(self, obj, attr_name):
        self._obj = obj
        self._attr_name = attr_name
    
    # === Proxy ===
    
    # HACK: Implementing call() here instead of __call__ because invoking
    #       __call__ on this object causes the C stack trace in CPython to
    #       intersect a function not already in the DPython Emterpreter
    #       whitelist, and I'm too lazy to extend the whitelist right now. -DF
    def call(self, *args, **kwargs):
        return getattr(self._obj, self._attr_name)(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError('Use call() instead')
    
    # NOTE: This attribute proxy exists mainly to handle requests to the "args"
    #       attribute, which is on the function/method object.
    def __getattr__(self, attr_name):
        return getattr(getattr(self._obj, self._attr_name), attr_name)
    
    # === Data ===
    
    @property
    def data(self):
        data_attr_name = '_%s_data' % self._attr_name
        try:
            return getattr(self._obj, data_attr_name)
        except AttributeError:
            data = self._create_initial_data()
            setattr(self._obj, data_attr_name, data)
            return data
    
    @staticmethod
    def _create_initial_data():
        return dict(
            # Collision events
            _was_collided={},
            # after_x_{seconds,frames} event, x_{seconds,frames}_after_created event
            _was_triggered=[False],     # TODO: Demote cell to scalar.
            # every_x_seconds event
            _next_trigger_time=[None],  # TODO: Demote cell to scalar.
            # every_x_frames event
            _next_trigger_frame=[None], # TODO: Demote cell to scalar.
        )


# ------------------------------------------------------------------------------
# Internal Utility

# Same as functools.partial(), but avoids importing the functools module.
def _functools_partial(func, *args, **kwargs):
    return lambda: func(*args, **kwargs)


# ------------------------------------------------------------------------------
