"""
Player System - 8-direction movement, animations, inventory, camera control
Replaces player.gd behavior (729 lines)
"""

import pygame
from croptopia.signals import SignalEmitter
from enum import Enum
from typing import Dict, Tuple


class Direction(Enum):
    """8-direction movement enum"""
    IDLE = "idle"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up-left"
    UP_RIGHT = "up-right"
    DOWN_LEFT = "down-left"
    DOWN_RIGHT = "down-right"


class Player(SignalEmitter):
    """
    Player character with 8-direction movement, animations, item system, camera.
    Replaces player.gd (729 lines) and player.tscn node definitions.
    
    Key Features:
    - 8-direction walk and sprint movement
    - Animation frame sequencing based on direction
    - Item wielding system (axe, redbaneberry, chives, etc.)
    - Inventory signal integration
    - Camera control with following behavior
    - Save/load game state
    """
    
    # Movement constants matching player.gd
    SPEED_WALK = 100.0
    SPEED_SPRINT = 200.0
    ANIMATION_FRAME_DURATION = 0.1  # Seconds per frame
    
    def __init__(self, position: Tuple[float, float], assets: Dict = None):
        """
        Initialize player character.
        
        Args:
            position: Starting (x, y) position - defaults to (12, -11) from worldtest
            assets: Dictionary of loaded sprite assets
        """
        super().__init__()
        
        # Position and movement
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = Direction.IDLE
        self.is_moving = False
        self.is_sprinting = False
        self.can_move = True
        
        # Animation system
        self.assets = assets or {}
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = self.ANIMATION_FRAME_DURATION
        
        # Item/inventory system
        self.selected_item = None  # "redbaneberry", "chive", "axe", etc.
        self.item_type = None      # Category of item
        self.item_position = pygame.math.Vector2(0, 0)
        
        # Camera system
        self.camera_enabled = True
        self.screen_center = pygame.math.Vector2(400, 300)  # Half of 800x600
        self.camera_offset = pygame.math.Vector2(position) - self.screen_center
        
        # Signals emitted from player (from player.gd)
        self.signals_emitted = [
            'stick_collected',
            'redbane_selected',
            'chive_selected',
            'sorrel_collected',
            'chive_collected',
            'elderberry_collected',
            'pinecone_collected',
            'item_holding'
        ]
        
        print(f"[Player] Initialized at position {position}")
    
    def handle_input(self, keys, mouse_buttons: Tuple[bool, bool, bool]) -> None:
        """
        Process keyboard and mouse input for movement.
        Implements 8-direction movement from player.gd
        
        Args:
            keys: pygame.key.get_pressed() result
            mouse_buttons: pygame.mouse.get_pressed() result
        """
        
        if not self.can_move:
            self.velocity = pygame.math.Vector2(0, 0)
            self.is_moving = False
            return

        # Get input axis (-1, 0, 1)
        input_x = 0
        input_y = 0
        
        # Horizontal input
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_x = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_x = 1
        
        # Vertical input
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            input_y = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            input_y = 1
        
        # Determine direction
        if input_x == 0 and input_y == 0:
            self.direction = Direction.IDLE
            self.velocity = pygame.math.Vector2(0, 0)
            self.is_moving = False
        else:
            # Determine 8-direction
            self.direction = self._get_direction_from_input(input_x, input_y)
            
            # Set velocity based on direction
            speed = self.SPEED_SPRINT if keys[pygame.K_LSHIFT] else self.SPEED_WALK
            self.is_sprinting = keys[pygame.K_LSHIFT]
            
            # Normalize diagonal movement (so diagonal speed equals cardinal speed)
            if input_x != 0 and input_y != 0:
                self.velocity.x = input_x * speed * 0.7071  # 1/sqrt(2)
                self.velocity.y = input_y * speed * 0.7071
            else:
                self.velocity.x = input_x * speed
                self.velocity.y = input_y * speed
            
            self.is_moving = True
    
    def update(self, delta: float) -> None:
        """
        Update player position, animation, and camera.
        Called every frame from game loop.
        
        Args:
            delta: Time since last frame in seconds
        """
        
        # Update position based on velocity
        self.position += self.velocity * delta
        
        # Update animation frame
        if self.is_moving:
            self.animation_timer += delta
            if self.animation_timer >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % 4  # 4-frame loop
                self.animation_timer = 0.0
        else:
            self.animation_frame = 0  # Idle pose
        
        # Update camera to follow player
        if self.camera_enabled:
            self.camera_offset = self.position - self.screen_center
    
    def on_item_collected(self, item_name: str) -> None:
        """
        Handle item collection - emit appropriate signal.
        Called when player collides with collectible.
        
        Args:
            item_name: Name of collected item
        """
        
        # Emit collection signal (from player.gd signals)
        signal_name = f"{item_name}_collected"
        self.emit_signal(signal_name)
        
        self.selected_item = item_name
        print(f"[Player] Collected: {item_name}")
    
    def on_item_selected(self, item_type: str) -> None:
        """
        Handle player selecting item from inventory.
        Implements item_holding signal from player.gd
        
        Args:
            item_type: Type of item selected (e.g., "Redbaneberry", "Chive", "Iron Axe")
        """
        
        self.item_type = item_type
        self.selected_item = item_type
        self.emit_signal('item_holding', item_type)
        
        print(f"[Player] Selected item: {item_type}")
    
    def render(self, display: pygame.Surface, camera_pos: pygame.math.Vector2) -> None:
        """
        Draw player sprite, item, effects.
        
        Args:
            display: Pygame surface to draw to
            camera_pos: Camera position for viewport conversion
        """
        
        # Calculate screen position relative to camera
        screen_x = self.position.x - camera_pos.x
        screen_y = self.position.y - camera_pos.y
        
        # Only draw if on screen
        if -64 < screen_x < display.get_width() + 64 and \
           -64 < screen_y < display.get_height() + 64:
            
            # Draw player sprite
            sprite_key = self._get_sprite_key()
            if sprite_key in self.assets:
                sprite = self.assets[sprite_key]
                display.blit(sprite, (screen_x, screen_y))
            else:
                # Draw placeholder circle if sprite not loaded
                pygame.draw.circle(display, (100, 200, 100), 
                                 (int(screen_x) + 8, int(screen_y) + 8), 8)
            
            # Draw item if holding
            if self.item_type:
                self._render_item(display, screen_x, screen_y)
    
    def _get_direction_from_input(self, input_x: int, input_y: int) -> Direction:
        """
        Convert input axis to 8-direction enum.
        
        Args:
            input_x: -1, 0, or 1
            input_y: -1, 0, or 1
        
        Returns:
            Direction enum value
        """
        
        if input_y < 0:  # Up
            if input_x < 0:
                return Direction.UP_LEFT
            elif input_x > 0:
                return Direction.UP_RIGHT
            else:
                return Direction.UP
        elif input_y > 0:  # Down
            if input_x < 0:
                return Direction.DOWN_LEFT
            elif input_x > 0:
                return Direction.DOWN_RIGHT
            else:
                return Direction.DOWN
        else:  # Horizontal only
            if input_x < 0:
                return Direction.LEFT
            else:
                return Direction.RIGHT
    
    def _get_sprite_key(self) -> str:
        """Get asset key for current animation frame"""

        direction_key = self._get_base_direction_key()

        if self.is_moving:
            anim_type = "walk" if not self.is_sprinting else "sprint"
            return f"player_{direction_key}_{anim_type}_{self.animation_frame}"
        return f"player_{direction_key}_idle"

    def _get_base_direction_key(self) -> str:
        """Map 8-direction movement to 4-direction sprite keys."""

        if self.direction in (Direction.UP, Direction.UP_LEFT, Direction.UP_RIGHT):
            return "up"
        if self.direction in (Direction.DOWN, Direction.DOWN_LEFT, Direction.DOWN_RIGHT):
            return "down"
        if self.direction == Direction.LEFT:
            return "left"
        if self.direction == Direction.RIGHT:
            return "right"
        return "down"
    
    def _render_item(self, display: pygame.Surface, screen_x: float, screen_y: float) -> None:
        """
        Draw item sprite on top of player.
        
        Args:
            display: Pygame surface to draw to
            screen_x: Player's screen X position
            screen_y: Player's screen Y position
        """
        
        item_sprite_key = f"item_{self.item_type}_{self.direction.value}"
        if item_sprite_key in self.assets:
            item_sprite = self.assets[item_sprite_key]
            
            # Get offset for item based on direction
            offset = self._get_item_offset(self.direction)
            display.blit(item_sprite, (screen_x + offset[0], screen_y + offset[1]))
    
    def _get_item_offset(self, direction: Direction) -> Tuple[int, int]:
        """
        Get pixel offset for item sprite based on player direction.
        Matches item_north_pos, item_south_pos, etc. from player.tscn
        
        Args:
            direction: Current player direction
        
        Returns:
            (x_offset, y_offset) tuple
        """
        
        offsets = {
            Direction.UP: (8, -16),
            Direction.DOWN: (8, 16),
            Direction.LEFT: (-16, 0),
            Direction.RIGHT: (16, 0),
            Direction.UP_LEFT: (-12, -12),
            Direction.UP_RIGHT: (12, -12),
            Direction.DOWN_LEFT: (-12, 12),
            Direction.DOWN_RIGHT: (12, 12),
            Direction.IDLE: (0, 0)
        }
        
        return offsets.get(direction, (0, 0))
    
    def save_game(self, save_path: str) -> None:
        """Save player state to file"""
        # TODO: Implement save system
        print(f"[Player] Saving game to {save_path}")
    
    def load_game(self, save_path: str) -> None:
        """Load player state from file"""
        # TODO: Implement load system
        print(f"[Player] Loading game from {save_path}")


# Testing
if __name__ == "__main__":
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Player Test")
    
    player = Player((400, 300))
    
    print("\nPlayer System Test")
    print("=" * 50)
    print(f"Initial position: {player.position}")
    print(f"Initial direction: {player.direction}")
    
    # Simulate movement input
    print("\nSimulating input...")
    test_keys = [0] * 512
    test_keys[pygame.K_w] = True
    test_keys[pygame.K_d] = True
    
    player.handle_input(test_keys, (False, False, False))
    print(f"After W+D input: direction={player.direction}, velocity={player.velocity}")
    
    # Simulate item collection
    print("\nSimulating item collection...")
    player.on_item_collected("stick")
    
    # Simulate item selection
    print("\nSimulating item selection...")
    player.on_item_selected("Iron Axe")
    
    pygame.quit()
