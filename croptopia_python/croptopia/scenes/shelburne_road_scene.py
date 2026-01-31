"""
Shelburne Road Scene - Checkpoint cutscene and shelburne load trigger
Derived from testing.tscn + scenes/shelburne_road.gd
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

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


class ShelburneRoadScene(Scene):
    """Implements cutscene checkpoint and transition to Shelburne."""

    def __init__(self, engine):
        super().__init__("shelburne_road", engine)

        # From testing.tscn:
        # scenetrans Area2D position: (4826, 1552)
        # CollisionShape2D position: (-562.4, -114.228)
        # RectangleShape2D_f8bob size: (42.8667, 925.848)
        self.checkpoint_trigger = RectTrigger(
            center=(4826 + -562.4, 1552 + -114.228),
            size=(42.8667, 925.848),
        )

        # shelburne_load Area2D with CollisionShape2D position: (-86, 1039)
        # RectangleShape2D_trnqr size: (169.737, 10.5731)
        self.shelburne_trigger = RectTrigger(
            center=(-86, 1039),
            size=(169.737, 10.5731),
        )

        self.in_cutscene = False
        self.cutscene_time = 0.0
        self.dialogue_index = 0

        self.dialogue_lines: List[Tuple[str, str]] = [
            ("Cop", "Papers, please."),
            ("Cop", "Sorry sir, only government agents may leave the town."),
            ("Cop", "The town is encircled and the outskirts are a battlefield now."),
        ]

    def enter(self) -> None:
        super().enter()
        self.in_cutscene = False
        self.cutscene_time = 0.0
        self.dialogue_index = 0

    def update(self, delta: float) -> None:
        player_pos = (self.engine.player.position.x, self.engine.player.position.y)

        # Check for Shelburne transition
        if self.shelburne_trigger.contains(player_pos):
            self.emit_signal("shelburne_generate")

        # Cutscene trigger
        if not self.in_cutscene and self.checkpoint_trigger.contains(player_pos):
            self._start_cutscene()

        if self.in_cutscene:
            self.cutscene_time += delta
            if self.cutscene_time >= 2.0:
                self.cutscene_time = 0.0
                self.dialogue_index += 1
                if self.dialogue_index < len(self.dialogue_lines):
                    char, text = self.dialogue_lines[self.dialogue_index]
                    self.engine.ui.show_dialog(char, text)
                else:
                    self._end_cutscene()

    def _start_cutscene(self) -> None:
        self.in_cutscene = True
        self.dialogue_index = 0
        self.cutscene_time = 0.0
        self.engine.player.can_move = False
        char, text = self.dialogue_lines[0]
        self.engine.ui.show_dialog(char, text)

    def _end_cutscene(self) -> None:
        self.in_cutscene = False
        self.engine.player.can_move = True
        self.engine.ui.hide_dialog()
