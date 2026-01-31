"""
UI Canvas System - Layer-based UI rendering with hotbar, HUD, and overlays
Replaces ui.gd, canvas_layer.gd, and hotbar.gd (400+ lines combined)
"""

import pygame
import os
import re
from croptopia.signals import SignalEmitter
from enum import Enum
from typing import Dict, List, Tuple, Optional


class UILayer(Enum):
    """UI layer hierarchy for Z-ordering"""
    BACKGROUND = 0
    GAME = 1
    HUD = 2
    DIALOG = 3
    INVENTORY = 4
    MENU = 5
    DEBUG = 6


class UIElement:
    """Base UI element with position, size, and rendering"""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize UI element.
        
        Args:
            x: Position X
            y: Position Y
            width: Element width
            height: Element height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.layer = UILayer.HUD
        self.children: List['UIElement'] = []
    
    def update(self, delta: float) -> None:
        """Update element state"""
        for child in self.children:
            child.update(delta)
    
    def render(self, display: pygame.Surface) -> None:
        """Render element"""
        if not self.visible:
            return
        
        for child in self.children:
            child.render(display)
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle mouse click.
        Returns True if click was handled by this element.
        """
        if self.rect.collidepoint(mouse_pos):
            return True
        return False


class HotBar(UIElement):
    """8-slot inventory hotbar (matches hotbar.tscn)"""
    
    # Position from worldtest.gd: position = Vector2(239, 544)
    HOTBAR_X = 239
    HOTBAR_Y = 544
    BASE_SLOT_SIZE = 16
    BASE_SLOT_SCALE = 0.5
    GRID_SCALE = 1.3
    RENDER_SCALE = 3
    SLOT_MARGIN = 2
    INVENTORY_SIZE = 8  # 8-slot row
    
    def __init__(self):
        """Initialize hotbar"""
        super().__init__(self.HOTBAR_X, self.HOTBAR_Y, 
                        0, 0)
        
        self.layer = UILayer.HUD
        
        # Hotbar inventory: {slot_index: item_name}
        self.inventory: Dict[int, str] = {}
        self.selected_slot = 0

        # UI assets
        self.hotbar_surface: Optional[pygame.Surface] = None
        self.slot_surface: Optional[pygame.Surface] = None
        self.select_surface: Optional[pygame.Surface] = None
        self.slot_size = int(self.BASE_SLOT_SIZE * self.BASE_SLOT_SCALE * self.GRID_SCALE * self.RENDER_SCALE)
        self.padding_left = int(6 * self.RENDER_SCALE)
        self.padding_top = int(4 * self.RENDER_SCALE)
        
        # Slot rendering data
        self.slot_rects = self._calculate_slot_rects()
        
        print(f"[HotBar] Initialized at ({self.HOTBAR_X}, {self.HOTBAR_Y})")
    
    def add_item(self, slot: int, item_name: str) -> bool:
        """
        Add item to hotbar slot.
        
        Args:
            slot: Slot index (0-8)
            item_name: Name of item
        
        Returns:
            True if successful
        """
        
        if 0 <= slot < self.INVENTORY_SIZE:
            self.inventory[slot] = item_name
            print(f"[HotBar] Added {item_name} to slot {slot}")
            return True
        
        return False
    
    def remove_item(self, slot: int) -> Optional[str]:
        """
        Remove item from slot.
        
        Args:
            slot: Slot index
        
        Returns:
            Item name or None
        """
        
        if slot in self.inventory:
            item = self.inventory.pop(slot)
            print(f"[HotBar] Removed {item} from slot {slot}")
            return item
        
        return None
    
    def select_slot(self, slot: int) -> bool:
        """
        Select hotbar slot.
        
        Args:
            slot: Slot index (0-8)
        
        Returns:
            True if valid slot
        """
        
        if 0 <= slot < self.INVENTORY_SIZE:
            self.selected_slot = slot
            return True
        
        return False
    
    def get_selected_item(self) -> Optional[str]:
        """Get item in selected slot"""
        return self.inventory.get(self.selected_slot)
    
    def render(self, display: pygame.Surface) -> None:
        """Draw hotbar and inventory slots"""
        
        if not self.visible:
            return
        
        # Draw hotbar background
        if self.hotbar_surface:
            display.blit(self.hotbar_surface, (self.HOTBAR_X, self.HOTBAR_Y))

        # Draw each slot
        for slot in range(self.INVENTORY_SIZE):
            slot_rect = self.slot_rects[slot]

            # Draw slot background
            if self.slot_surface:
                display.blit(self.slot_surface, slot_rect.topleft)
            else:
                bg_color = (100, 100, 100) if slot != self.selected_slot else (200, 150, 100)
                pygame.draw.rect(display, bg_color, slot_rect)

            # Selection indicator
            if slot == self.selected_slot:
                if self.select_surface:
                    display.blit(self.select_surface, slot_rect.topleft)
                else:
                    pygame.draw.rect(display, (255, 200, 100), slot_rect, 2)
            
            # Draw item in slot
            if slot in self.inventory:
                self._render_item_preview(display, slot_rect, self.inventory[slot])
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle slot click"""
        
        for slot, slot_rect in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                self.select_slot(slot)
                return True
        
        return False
    
    def _calculate_slot_rects(self) -> List[pygame.Rect]:
        """Calculate rects for all 8 slots"""
        
        rects = []
        for col in range(self.INVENTORY_SIZE):
            x = self.HOTBAR_X + self.padding_left + col * (self.slot_size + self.SLOT_MARGIN)
            y = self.HOTBAR_Y + self.padding_top
            rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))
        
        return rects
    
    def _render_item_preview(self, display: pygame.Surface, 
                            slot_rect: pygame.Rect, item_name: str) -> None:
        """
        Draw item preview in slot.
        
        Args:
            display: Pygame surface
            slot_rect: Slot rectangle
            item_name: Name of item
        """
        
        # Draw simple text preview (TODO: use actual sprite)
        font = pygame.font.Font(None, 16)
        text = font.render(item_name[:3].upper(), True, (200, 200, 200))
        text_rect = text.get_rect(center=slot_rect.center)
        display.blit(text, text_rect)

    def set_assets(self, hotbar_surface: Optional[pygame.Surface],
                   slot_surface: Optional[pygame.Surface],
                   select_surface: Optional[pygame.Surface]) -> None:
        """Assign hotbar assets and recalc layout."""
        self.hotbar_surface = hotbar_surface
        self.slot_surface = slot_surface
        self.select_surface = select_surface

        if self.hotbar_surface:
            width, height = self.hotbar_surface.get_size()
            self.rect = pygame.Rect(self.HOTBAR_X, self.HOTBAR_Y, width, height)

        self.slot_rects = self._calculate_slot_rects()


class HUD:
    """
    Heads-Up Display - Day/night cycle, money, health, etc.
    Rendered at top of screen (WorldUICanvas in worldtest.gd)
    """
    
    HUD_HEIGHT = 40
    
    def __init__(self):
        """Initialize HUD"""
        
        self.day = 1
        self.time = 0.0  # 0.0 = 6:00 AM, 1.0 = 6:00 AM next day
        self.money = 0
        self.health = 100
        self.max_health = 100
        
        self.visible = True

        # UI assets
        self.ui_bar_surface: Optional[pygame.Surface] = None
        self.money_icon_surface: Optional[pygame.Surface] = None
        self.font_path: Optional[str] = None
        
        print("[HUD] Initialized")
    
    def update(self, delta: float) -> None:
        """Update HUD state"""
        # TODO: Update time/day cycle
        pass
    
    def render(self, display: pygame.Surface) -> None:
        """Draw HUD elements"""
        
        if not self.visible:
            return
        
        # Draw HUD background
        hud_rect = pygame.Rect(0, 0, display.get_width(), self.HUD_HEIGHT)
        if self.ui_bar_surface:
            bar = pygame.transform.scale(self.ui_bar_surface, (display.get_width(), self.HUD_HEIGHT))
            display.blit(bar, (0, 0))
        else:
            pygame.draw.rect(display, (30, 30, 30), hud_rect)
            pygame.draw.line(display, (100, 100, 100), 
                            (0, self.HUD_HEIGHT), 
                            (display.get_width(), self.HUD_HEIGHT), 2)

        # Draw text info
        font = pygame.font.Font(self.font_path, 18) if self.font_path else pygame.font.Font(None, 24)
        
        day_text = font.render(f"Day {self.day}", True, (200, 200, 200))
        display.blit(day_text, (10, 10))

        money_x = 120
        if self.money_icon_surface:
            icon = pygame.transform.scale(self.money_icon_surface, (20, 20))
            display.blit(icon, (90, 10))
            money_x = 115

        money_text = font.render(f"${self.money}", True, (200, 200, 100))
        display.blit(money_text, (money_x, 10))

        health_text = font.render(f"HP: {self.health}/{self.max_health}", True, 
                                 (200, 100, 100))
        display.blit(health_text, (display.get_width() - 170, 10))
    
    def set_day(self, day: int) -> None:
        """Set current day"""
        self.day = day
    
    def set_time(self, time_fraction: float) -> None:
        """Set time (0.0 = 6 AM, 0.5 = 6 PM, etc.)"""
        self.time = max(0.0, min(1.0, time_fraction))
    
    def set_money(self, amount: int) -> None:
        """Set money amount"""
        self.money = amount
    
    def set_health(self, health: int) -> None:
        """Set current health"""
        self.health = max(0, min(self.max_health, health))

    def set_assets(self, ui_bar_surface: Optional[pygame.Surface],
                   money_icon_surface: Optional[pygame.Surface],
                   font_path: Optional[str]) -> None:
        """Assign HUD assets."""
        self.ui_bar_surface = ui_bar_surface
        self.money_icon_surface = money_icon_surface
        self.font_path = font_path


class DialogBox(UIElement):
    """Dialogue box for NPC conversations"""
    
    def __init__(self, width: int = 600, height: int = 150):
        """Initialize dialog box"""
        
        # Center horizontally, bottom of screen
        x = (800 - width) // 2  # Assuming 800px width
        y = 600 - height - 20    # Assuming 600px height
        
        super().__init__(x, y, width, height)
        
        self.layer = UILayer.DIALOG
        self.visible = False
        
        self.text = ""
        self.character_name = ""
        self.current_frame = 0
        self.total_frames = 0
        
        print("[DialogBox] Initialized")
    
    def show_dialog(self, character: str, text: str, portrait_frame: int = 0) -> None:
        """
        Show dialog from character.
        
        Args:
            character: Character name
            text: Dialogue text
            portrait_frame: Portrait animation frame (0-7 from dialogue.gd)
        """
        
        self.visible = True
        self.character_name = character
        self.text = text
        self.current_frame = portrait_frame
        
        print(f"[DialogBox] Showing dialog: {character}: {text[:30]}...")
    
    def hide_dialog(self) -> None:
        """Hide dialogue box"""
        self.visible = False
    
    def render(self, display: pygame.Surface) -> None:
        """Draw dialog box"""
        
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(display, (40, 40, 40), self.rect)
        pygame.draw.rect(display, (150, 150, 150), self.rect, 2)
        
        # Draw character name
        font = pygame.font.Font(None, 20)
        name_text = font.render(self.character_name, True, (200, 200, 200))
        display.blit(name_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw dialogue text with word wrapping
        text_font = pygame.font.Font(None, 18)
        words = self.text.split()
        current_line = ""
        line_y = self.rect.y + 35
        
        for word in words:
            test_line = current_line + word + " "
            if text_font.size(test_line)[0] > self.rect.width - 20:
                if current_line:
                    text_surf = text_font.render(current_line, True, (200, 200, 200))
                    display.blit(text_surf, (self.rect.x + 10, line_y))
                    line_y += 20
                current_line = word + " "
            else:
                current_line = test_line
        
        if current_line:
            text_surf = text_font.render(current_line, True, (200, 200, 200))
            display.blit(text_surf, (self.rect.x + 10, line_y))


class UICanvas(SignalEmitter):
    """
    Main UI canvas coordinating all UI elements.
    Replaces canvas_layer.gd (100 lines)
    """
    
    def __init__(self, display_size: Tuple[int, int] = (800, 600), 
                 croptopia_root: Optional[str] = None):
        """
        Initialize UI canvas.
        
        Args:
            display_size: (width, height) of display
            croptopia_root: Path to Croptopia - 02.11.25 (for UI asset loading)
        """
        super().__init__()
        
        self.display_size = display_size
        self.croptopia_root = self._resolve_croptopia_root(croptopia_root)
        self.ui_asset_paths: List[str] = []
        self.ui_assets: Dict[str, object] = {}
        self.ui_missing_assets: List[str] = []
        
        # UI layers
        self.layers: Dict[UILayer, List[UIElement]] = {
            UILayer.BACKGROUND: [],
            UILayer.GAME: [],
            UILayer.HUD: [],
            UILayer.DIALOG: [],
            UILayer.INVENTORY: [],
            UILayer.MENU: [],
            UILayer.DEBUG: []
        }
        
        # UI assets (ui.tscn + child scenes)
        self._load_ui_assets()

        # UI components
        self.hotbar = HotBar()
        self.hud = HUD()
        self._apply_ui_assets()
        self.dialog = DialogBox()
        
        # Add to layers
        self.layers[UILayer.HUD].append(self.hotbar)
        self.layers[UILayer.DIALOG].append(self.dialog)
        
        print(f"[UICanvas] Initialized ({display_size[0]}x{display_size[1]})")

    def _apply_ui_assets(self) -> None:
        """Apply loaded UI assets to UI components."""
        hotbar_tex = self.ui_assets.get("res://assets/hotbar_asset.png")
        slot_tex = self.ui_assets.get("res://inventory/pixil-frame-0 - 2024-01-08T110435.971.png")
        select_tex = self.ui_assets.get("res://inventory/pixil-frame-0 - 2024-02-05T105702.567.png")
        ui_bar_tex = self.ui_assets.get("res://assets/ui_bar.png")
        money_icon_tex = self.ui_assets.get("res://assets/pixil-frame-0 (5).png")
        font_path = self.ui_assets.get("res://fonts/pixelated.ttf")

        # Scale hotbar textures to match Godot scale (3x)
        if isinstance(hotbar_tex, pygame.Surface):
            hotbar_tex = pygame.transform.scale(
                hotbar_tex,
                (hotbar_tex.get_width() * HotBar.RENDER_SCALE,
                 hotbar_tex.get_height() * HotBar.RENDER_SCALE)
            )

        if isinstance(slot_tex, pygame.Surface):
            size = int(HotBar.BASE_SLOT_SIZE * HotBar.BASE_SLOT_SCALE * HotBar.GRID_SCALE * HotBar.RENDER_SCALE)
            slot_tex = pygame.transform.scale(slot_tex, (size, size))

        if isinstance(select_tex, pygame.Surface):
            size = int(HotBar.BASE_SLOT_SIZE * HotBar.BASE_SLOT_SCALE * HotBar.GRID_SCALE * HotBar.RENDER_SCALE)
            select_tex = pygame.transform.scale(select_tex, (size, size))

        self.hotbar.set_assets(hotbar_tex, slot_tex, select_tex)
        self.hud.set_assets(ui_bar_tex, money_icon_tex, font_path)

    def _resolve_croptopia_root(self, croptopia_root: Optional[str]) -> Optional[str]:
        """Resolve Croptopia project root path."""
        if croptopia_root and os.path.isdir(croptopia_root):
            return croptopia_root

        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        candidate = os.path.join(repo_root, "Croptopia - 02.11.25")
        if os.path.isdir(candidate):
            return candidate

        return None

    def _load_ui_assets(self) -> None:
        """Load all assets referenced by ui.tscn and its child scenes."""
        if not self.croptopia_root:
            print("[UICanvas] Croptopia root not found; skipping UI asset load")
            return

        ui_tscn = os.path.join(self.croptopia_root, "scenes", "ui.tscn")
        if not os.path.exists(ui_tscn):
            print(f"[UICanvas] ui.tscn not found: {ui_tscn}")
            return

        asset_paths = self._collect_tscn_assets(ui_tscn)
        self.ui_asset_paths = sorted(asset_paths)

        for res_path in self.ui_asset_paths:
            full_path = self._resolve_res_path(res_path)
            if not full_path or not os.path.exists(full_path):
                self.ui_missing_assets.append(res_path)
                continue

            ext = os.path.splitext(full_path)[1].lower()
            try:
                if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    self.ui_assets[res_path] = pygame.image.load(full_path).convert_alpha()
                elif ext in [".ttf", ".otf"]:
                    self.ui_assets[res_path] = full_path
                elif ext in [".wav", ".mp3", ".ogg"]:
                    self.ui_assets[res_path] = full_path
                else:
                    self.ui_assets[res_path] = full_path
            except Exception:
                self.ui_missing_assets.append(res_path)

        print(f"[UICanvas] UI assets loaded: {len(self.ui_assets)}")
        if self.ui_missing_assets:
            print(f"[UICanvas] UI assets missing: {len(self.ui_missing_assets)}")

    def _collect_tscn_assets(self, tscn_path: str, seen: Optional[set] = None) -> set:
        """Collect asset paths from a .tscn file and its PackedScene children."""
        if seen is None:
            seen = set()
        if tscn_path in seen or not os.path.exists(tscn_path):
            return set()

        seen.add(tscn_path)
        assets = set()
        packed_scenes = set()

        ext_pattern = re.compile(r'^\[ext_resource\s+type="([^"]+)"[^\]]*\spath="([^"]+)"')

        try:
            with open(tscn_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    match = ext_pattern.match(line.strip())
                    if not match:
                        continue
                    res_type, res_path = match.groups()

                    if res_type == "PackedScene":
                        packed_scenes.add(res_path)
                    elif res_type in {"Texture2D", "FontFile", "AudioStream", "Shader", "Animation"}:
                        assets.add(res_path)
        except Exception:
            return assets

        for child in sorted(packed_scenes):
            child_path = self._resolve_res_path(child)
            if child_path:
                assets.update(self._collect_tscn_assets(child_path, seen))

        return assets

    def _resolve_res_path(self, res_path: str) -> Optional[str]:
        """Resolve a res:// path to an absolute filesystem path."""
        if not self.croptopia_root:
            return None
        if res_path.startswith("res://"):
            rel = res_path.replace("res://", "", 1)
        else:
            rel = res_path
        return os.path.join(self.croptopia_root, rel.replace("/", os.sep))
    
    def update(self, delta: float) -> None:
        """Update all UI elements"""
        
        for layer in self.layers.values():
            for element in layer:
                element.update(delta)
        
        self.hud.update(delta)
    
    def render(self, display: pygame.Surface) -> None:
        """Render all UI layers in order"""
        
        # Render HUD (always on top of game)
        self.hud.render(display)
        
        # Render UI layers in order
        for layer_type in [UILayer.BACKGROUND, UILayer.GAME, UILayer.HUD, 
                          UILayer.DIALOG, UILayer.INVENTORY, UILayer.MENU, 
                          UILayer.DEBUG]:
            for element in self.layers[layer_type]:
                element.render(display)
    
    def handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle mouse click on UI elements.
        
        Args:
            mouse_pos: (x, y) mouse position
        
        Returns:
            True if click was handled by UI
        """
        
        # Check from top layer to bottom (reverse order)
        for layer_type in reversed([UILayer.MENU, UILayer.INVENTORY, UILayer.DIALOG, 
                                   UILayer.HUD, UILayer.GAME, UILayer.BACKGROUND]):
            for element in self.layers[layer_type]:
                if element.handle_click(mouse_pos):
                    return True
        
        return False
    
    def add_element(self, element: UIElement, layer: UILayer) -> None:
        """Add UI element to layer"""
        element.layer = layer
        self.layers[layer].append(element)
    
    def show_dialog(self, character: str, text: str) -> None:
        """Show dialogue box"""
        self.dialog.show_dialog(character, text)
        self.emit_signal('dialog_shown', character, text)
    
    def hide_dialog(self) -> None:
        """Hide dialogue box"""
        self.dialog.hide_dialog()
        self.emit_signal('dialog_hidden')


# Testing
if __name__ == "__main__":
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("UI Canvas Test")
    
    canvas = UICanvas((800, 600))
    
    print("\nUI Canvas Test")
    print("=" * 50)
    
    # Test hotbar
    print("\nHotbar test:")
    canvas.hotbar.add_item(0, "Iron Axe")
    canvas.hotbar.add_item(1, "Redbaneberry")
    print(f"Selected item: {canvas.hotbar.get_selected_item()}")
    canvas.hotbar.select_slot(1)
    print(f"Selected item after switch: {canvas.hotbar.get_selected_item()}")
    
    # Test HUD
    print("\nHUD test:")
    canvas.hud.set_day(5)
    canvas.hud.set_money(150)
    canvas.hud.set_health(80)
    print(f"Day: {canvas.hud.day}, Money: {canvas.hud.money}, Health: {canvas.hud.health}")
    
    # Test dialog
    print("\nDialog test:")
    canvas.show_dialog("Zea", "Welcome to the farm! Would you like to help me plant some crops?")
    print(f"Dialog visible: {canvas.dialog.visible}")
    
    # Render test
    print("\nRendering UI...")
    canvas.update(0.016)
    canvas.render(display)
    pygame.display.flip()
    
    pygame.time.wait(1000)
    pygame.quit()
