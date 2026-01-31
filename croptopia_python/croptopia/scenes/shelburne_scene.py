"""
ShelburneScene: Main town zone with NPCs, houses, shops, and collectibles.
Orchestrates NPC interactions and quest progression.
Signals to michael_plot when conditions are met.
"""

from .base_scene import Scene, RectTrigger


class ShelburneScene(Scene):
    """Main Shelburne town area - NPCs, houses, economy."""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "shelburne"
        
        # Mount Crag trigger area (leads to michael_plot)
        # From shelburne.gd: signals mt_crag_over when cutscene complete
        self.mt_crag_trigger = RectTrigger(
            center=(-10388 - 5870, -1849 - 18615),  # mt_crag_pos marker offset
            size=(200, 200)  # Trigger zone
        )
        
        # NPC Zea position (from worldtest.gd: Vector2(-297, -1287))
        self.zea_position = (-297, -1287)
        
        # Quest state tracking
        self.quest_is_finished = False
        self.newspaper_active = False  # When true, player can interact with newspaper
        
    def update(self, delta):
        """Update Shelburne state - check triggers, NPC interactions."""
        if not self.engine or not self.engine.player:
            return
            
        player_pos = self.engine.player.position
        
        # Check if player reaches Mount Crag trigger
        if self.mt_crag_trigger.contains(player_pos) and not self.quest_is_finished:
            # Should emit mt_crag_over signal to transition to michael_plot
            self.emit_signal("mt_crag_over")
            
    def on_npc_quest_finished(self):
        """Called when NPC quest is completed (from Zea interaction)."""
        self.quest_is_finished = True
        # This triggers the zea_walk_cutscene sequence
        self.emit_signal("quest_finished")
        
    def activate_newspaper(self):
        """Allow player to interact with newspaper (item pickup mechanism)."""
        self.newspaper_active = True
