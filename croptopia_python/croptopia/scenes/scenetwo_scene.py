"""
ScenetwoScene: Second Zea dialogue/cutscene after the walk animation.
Short dialogue scene that transitions back to Shelburne zone.
"""

from .base_scene import Scene


class ScenetwoScene(Scene):
    """Second Zea Cutscene - dialogue scene after walk animation."""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "scenetwo"
        
        # Cutscene state
        self.cutscene_finished = False
        self.dialogue_active = False
        
        # From scenetwo.gd: player position Vector2(-5091.517, -3156.3)
        self.cutscene_position = (-5091.517, -3156.3)
        
        # Camera state (disable/enable based on cutscene progression)
        self.player_camera_enabled = False
        self.cutscene_camera_enabled = True
        
    def update(self, delta):
        """Update second cutscene state."""
        if not self.cutscene_finished:
            # Dialogue progression handled by UI system
            # This scene just waits for dialogue to complete
            pass
            
    def complete_cutscene(self):
        """Mark cutscene as finished and emit signal."""
        self.cutscene_finished = True
        self.emit_signal("cutscene_finished")
        # Re-enable player camera
        if self.engine and self.engine.player:
            self.engine.player.camera.enabled = True
