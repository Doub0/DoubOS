"""
Spawn Node Scene - Minimal trigger logic for spawn_node.tscn
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from croptopia.scene_manager import Scene


@dataclass
class RectTrigger:
    center: Tuple[float, float]
    size: Tuple[float, float]

    def contains(self, pos: Tuple[float, float]) -> bool:
        cx, cy = self.center
        w, h = self.size
        x, y = pos
        return (cx - w / 2) <= x <= (cx + w / 2) and (cy - h / 2) <= y <= (cy + h / 2)


class SpawnNodeScene(Scene):
    """Implements the spawn_node player_detection trigger."""

    def __init__(self, engine):
        super().__init__("spawn_node", engine)
        # Derived from spawn_node.tscn
        # spawn_node position: (32, -192)
        # player_detection CollisionShape2D position: (422.75, -991.5)
        # RectangleShape2D size: (266.5, 15)
        self.trigger = RectTrigger(center=(32 + 422.75, -192 + -991.5), size=(266.5, 15))
        self.has_triggered = False

    def update(self, delta: float) -> None:
        if self.has_triggered:
            return
        player_pos = (self.engine.player.position.x, self.engine.player.position.y)
        if self.trigger.contains(player_pos):
            self.has_triggered = True
            self.emit_signal("scene_triggered")
