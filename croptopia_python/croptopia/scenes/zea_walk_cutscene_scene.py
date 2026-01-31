"""
ZeaWalkCutsceneScene: Animated cutscene where Zea walks across screen.
Two-phase path animation with camera following Zea's movement.
Transitions to scenetwo (second dialogue scene) on completion.
"""

from .base_scene import Scene


class ZeaWalkCutsceneScene(Scene):
    """Zea Walk Cutscene - animated character movement with camera tracking."""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "zea_walk_cutscene"
        
        # Cutscene state machine (from zea_walk_cutscene.gd)
        self.is_pathfollowing = False      # First path: Zea walks to meeting point
        self.is_pathfollowing2 = False     # Second path: Both walk away together
        self.cutscene_is_over = False
        
        # Animation progress (0.0 to 1.0 for each path)
        self.path_progress = 0.0
        self.path_progress2 = 0.0
        
        # Path movement speeds (from GDScript: 0.007 and 0.001)
        self.path_speed_1 = 0.007
        self.path_speed_2 = 0.001
        
        # Fade transition state
        self.quest_fade_active = False
        
    def update(self, delta):
        """Update cutscene animation and transitions."""
        if not self.cutscene_is_over:
            # Phase 1: First path movement
            if self.is_pathfollowing:
                self.path_progress += self.path_speed_1
                if self.path_progress >= 1.0:
                    # Start fade transition
                    self.quest_fade_active = True
                    self.is_pathfollowing = False
                    self.is_pathfollowing2 = True  # Switch to second path
                    
            # Phase 2: Second path movement
            if self.is_pathfollowing2:
                self.path_progress2 += self.path_speed_2
                if self.path_progress2 >= 1.0:
                    # Cutscene complete
                    self.cutscene_is_over = True
                    self.emit_signal("cutscene_over")
                    
    def start_cutscene(self):
        """Begin Zea walk cutscene animation."""
        self.is_pathfollowing = True
        self.path_progress = 0.0
        self.path_progress2 = 0.0
