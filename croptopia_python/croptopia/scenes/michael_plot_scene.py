"""
MichaelPlotScene: Building placement and customization area.
Player constructs buildings and items. Transitions to zea_walk_cutscene on completion.
"""

from .base_scene import Scene


class MichaelPlotScene(Scene):
    """Michael Plot - building placement and construction mechanics."""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "michael_plot"
        
        # Building state
        self.can_build = False
        self.cutscene_happened = False
        self.selected_item = None
        
        # From michael_plot.gd signals
        self.redbaneberry_placed = False
        self.chive_placed = False
        
    def update(self, delta):
        """Update Michael Plot state - handle building placement."""
        if not self.engine or not self.engine.player:
            return
        
        # Building mechanics handled by player.selected_item
        if self.engine.player.selected_item:
            self.selected_item = self.engine.player.selected_item
            
        # Check if cutscene should complete
        # From michael_plot.gd: cutscene triggers when conditions met
        if self.cutscene_happened:
            self.emit_signal("michael_plot_over")
    
    def enable_building_mode(self):
        """Enable building/placement mode."""
        self.can_build = True
        
    def disable_building_mode(self):
        """Disable building/placement mode."""
        self.can_build = False
        
    def on_redbaneberry_placed(self):
        """Callback when redbaneberry item is placed."""
        self.redbaneberry_placed = True
        
    def on_chive_placed(self):
        """Callback when chive item is placed."""
        self.chive_placed = True
        
    def start_cutscene(self):
        """Begin Michael Plot cutscene."""
        self.cutscene_happened = True
