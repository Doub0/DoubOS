"""
Base Scene class - foundation for all game scenes
Handles signal emission, state management, and lifecycle
"""

from dataclasses import dataclass
from typing import Tuple
from croptopia.signals import SignalEmitter


@dataclass
class RectTrigger:
    """Simple rectangular trigger/collision box for area detection."""
    center: Tuple[float, float]
    size: Tuple[float, float]

    def contains(self, pos: Tuple[float, float]) -> bool:
        """Check if point is inside trigger bounds."""
        cx, cy = self.center
        w, h = self.size
        x, y = pos
        return (cx - w / 2) <= x <= (cx + w / 2) and (cy - h / 2) <= y <= (cy + h / 2)


class Scene(SignalEmitter):
    """
    Base class for all game scenes.
    
    Replaces Godot Node2D pattern in Python:
    - Signal emission (emit_signal, on_signal)
    - Lifecycle (enter, exit, update, render)
    - State management
    """
    
    def __init__(self, name: str, engine=None):
        super().__init__()
        self.name = name
        self.engine = engine
        self.is_active = False
        
    def enter(self) -> None:
        """Called when scene becomes active."""
        self.is_active = True
        print(f"[Scene] {self.name} entered")
        
    def exit(self) -> None:
        """Called when scene is deactivated."""
        self.is_active = False
        print(f"[Scene] {self.name} exited")
        
    def update(self, delta: float) -> None:
        """Update scene logic every frame."""
        pass
        
    def render(self, display) -> None:
        """Render scene to display surface."""
        pass
        
    def cleanup(self) -> None:
        """Clean up resources on deactivation."""
        self.clear_signals()
