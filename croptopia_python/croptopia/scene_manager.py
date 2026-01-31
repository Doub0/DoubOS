"""
Scene Manager - Orchestrates all scene loading and signal routing
Replaces worldtest.gd behavior in Python
"""

from typing import Dict, Any, Callable
from croptopia.signals import SignalEmitter, event_bus
from croptopia.scenes.base_scene import Scene
import pygame


class SceneManager(SignalEmitter):
    """
    Orchestrates all scene loading, transitions, and signal routing.
    Replaces worldtest.gd's preload and signal connection behavior.
    
    Key Responsibilities:
    1. Preload all 11 subscenes
    2. Wire up signal connections between scenes
    3. Manage scene transitions
    4. Handle signal routing
    """
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Scene = None
        self.scene_queue: list = []
        
        print("[SceneManager] Initializing...")
        self._preload_scenes()
        self._setup_signal_connections()
        self.switch_scene('main_menu')  # Start with main menu
    
    def _preload_scenes(self) -> None:
        """
        Preload all 11 scenes from worldtest.gd's preload list.
        In Godot: var spawn = preload("res://scenes/spawn_node.tscn").instantiate()
        In Python: self.scenes['spawn_node'] = SpawnNodeScene()
        
        WorldTest.gd Preload Chain:
        1. spawn_node (first playable zone)
        2. shelburne_road (checkpoint cutscene)
        3. shelburne (main town)
        4. michael_plot (building area)
        5. zea_walk_cutscene (Zea walks to meeting point)
        6. scenetwo (dialogue after walk)
        7. npc (Zea NPC with quests)
        8. redbaneberry/chives (collectibles)
        9. ui (canvas UI layer)
        10-11. Other utility scenes
        """
        
        # Import all real scene classes
        from croptopia.scenes.main_menu_scene import MainMenuScene
        from croptopia.scenes.spawn_node_scene import SpawnNodeScene
        from croptopia.scenes.shelburne_road_scene import ShelburneRoadScene
        from croptopia.scenes.shelburne_scene import ShelburneScene
        from croptopia.scenes.michael_plot_scene import MichaelPlotScene
        from croptopia.scenes.zea_walk_cutscene_scene import ZeaWalkCutsceneScene
        from croptopia.scenes.scenetwo_scene import ScenetwoScene
        
        scenes_to_load = {
            'main_menu': MainMenuScene,
            'spawn_node': SpawnNodeScene,
            'shelburne_road': ShelburneRoadScene,
            'shelburne': ShelburneScene,
            'michael_plot': MichaelPlotScene,
            'zea_walk_cutscene': ZeaWalkCutsceneScene,
            'scenetwo': ScenetwoScene,
            # Placeholder scenes (utility - not core game flow)
            'npc': None,
            'redbaneberry': None,
            'chive': None,
            'ui': None,
            'phillip_merchant': None
        }
        
        for key, scene_class in scenes_to_load.items():
            if scene_class:
                self.scenes[key] = scene_class(self.engine)
            else:
                self.scenes[key] = Scene(key, self.engine)
            print(f"  [Preload] {key}")
    
    def _setup_signal_connections(self) -> None:
        """
        Wire up all signal connections between scenes.
        Matches the orchestration from worldtest.gd
        
        Signal Flow:
        spawn_node.scene_triggered
          → _on_spawn_scene_triggered()
          → switch_scene('shelburne_road')
        
        shelburne_road.shelburne_generate
          → _on_shelburne_generate()
          → switch_scene('shelburne')
        
        shelburne.mt_crag_over
          → switch_scene('michael_plot')
        
        michael_plot.cutscene_end (custom)
          → switch_scene('zea_walk_cutscene')
        
        zea_walk_cutscene.cutscene_over
          → switch_scene('scenetwo')
        
        scenetwo.cutscene_finished
          → switch_scene('shelburne')
        
        npc.quest_is_finished
          → _on_zea_quest_finished()
        """
        
        print("[SceneManager] Setting up signal connections...")
        
        # SPAWN_NODE SIGNALS
        if 'spawn_node' in self.scenes:
            self.scenes['spawn_node'].on_signal('scene_triggered', 
                                                 self._on_spawn_scene_triggered)
        
        # SHELBURNE_ROAD SIGNALS
        if 'shelburne_road' in self.scenes:
            self.scenes['shelburne_road'].on_signal('shelburne_generate',
                                                    self._on_shelburne_generate)
        
        # SHELBURNE SIGNALS
        if 'shelburne' in self.scenes:
            self.scenes['shelburne'].on_signal('mt_crag_over',
                                               self._on_mt_crag_over)
            self.scenes['shelburne'].on_signal('quest_finished',
                                               self._on_quest_finished)
        
        # MICHAEL_PLOT SIGNALS  
        if 'michael_plot' in self.scenes:
            self.scenes['michael_plot'].on_signal('michael_plot_over',
                                                   self._on_michael_plot_over)
        
        # ZEA_WALK_CUTSCENE SIGNALS
        if 'zea_walk_cutscene' in self.scenes:
            self.scenes['zea_walk_cutscene'].on_signal('cutscene_over',
                                                       self._on_zea_cutscene_over)
        
        # SCENETWO SIGNALS
        if 'scenetwo' in self.scenes:
            self.scenes['scenetwo'].on_signal('cutscene_finished',
                                             self._on_scenetwo_finished)
        
        # NPC (ZEA) SIGNALS
        if 'npc' in self.scenes:
            self.scenes['npc'].on_signal('quest_is_finished',
                                         self._on_zea_quest_finished)
        
        # MAIN_MENU SIGNALS
        if 'main_menu' in self.scenes:
            self.scenes['main_menu'].on_signal('start_game',
                                               self._on_start_game)
            self.scenes['main_menu'].on_signal('quit_game',
                                               self._on_quit_game)
            self.scenes['main_menu'].on_signal('open_settings',
                                               self._on_open_settings)
            self.scenes['main_menu'].on_signal('show_credits',
                                               self._on_show_credits)
    
    # Signal handlers matching worldtest.gd orchestration
    
    def _on_spawn_scene_triggered(self) -> None:
        """
        Called when spawn_node emits 'scene_triggered'
        Player entered the spawn detection zone and checkpoint is ready.
        """
        print("[SceneManager] → spawn_node.scene_triggered")
        self._generate_shelburne_road()
    
    def _on_shelburne_generate(self) -> None:
        """
        Called when shelburne_road emits 'shelburne_generate'
        Checkpoint cutscene complete, load main town.
        """
        print("[SceneManager] → shelburne_road.shelburne_generate")
        self.switch_scene('shelburne')
    
    def _on_mt_crag_over(self) -> None:
        """
        Called when shelburne emits 'mt_crag_over'
        Mount Crag cutscene complete, transition to Michael Plot.
        """
        print("[SceneManager] → shelburne.mt_crag_over")
        self.switch_scene('michael_plot')
    
    def _on_michael_plot_over(self) -> None:
        """
        Called when michael_plot completes cutscene
        Building area finished, start Zea walk animation.
        """
        print("[SceneManager] → michael_plot.michael_plot_over")
        self.switch_scene('zea_walk_cutscene')
        # Trigger cutscene start
        if self.scenes['zea_walk_cutscene']:
            self.scenes['zea_walk_cutscene'].start_cutscene()
    
    def _on_zea_cutscene_over(self) -> None:
        """
        Called when zea_walk_cutscene emits 'cutscene_over'
        Walking animation complete, load second dialogue scene.
        """
        print("[SceneManager] → zea_walk_cutscene.cutscene_over")
        self.switch_scene('scenetwo')
    
    def _on_scenetwo_finished(self) -> None:
        """
        Called when scenetwo emits 'cutscene_finished'
        Second cutscene/dialogue complete, return to Shelburne.
        """
        print("[SceneManager] → scenetwo.cutscene_finished")
        self.switch_scene('shelburne')
    
    def _on_quest_finished(self) -> None:
        """
        Called when shelburne emits 'quest_finished'
        Player completed NPC quest, triggers walking cutscene.
        """
        print("[SceneManager] → shelburne.quest_finished")
        # Start Zea walk cutscene from Shelburne
        # Player position will be locked during this
    
    def _on_zea_quest_finished(self) -> None:
        """Called when NPC quest completes"""
        print("[SceneManager] → npc.quest_is_finished")
        # Update game state, emit completion signal, etc.
        event_bus.emit_signal("quest_completed", quest_name="zea_first_quest")
    
    def _on_start_game(self) -> None:
        """Called when main_menu emits 'start_game'"""
        print("[SceneManager] → main_menu.start_game")
        self.switch_scene('spawn_node')
    
    def _on_quit_game(self) -> None:
        """Called when main_menu emits 'quit_game'"""
        print("[SceneManager] → main_menu.quit_game - EXITING")
        # Signal engine to quit
        if hasattr(self.engine, 'running'):
            self.engine.running = False
    
    def _on_open_settings(self) -> None:
        """Called when main_menu emits 'open_settings'"""
        print("[SceneManager] → main_menu.open_settings")
        # TODO: Implement settings scene
        print("  [TODO] Settings scene not yet implemented")
    
    def _on_show_credits(self) -> None:
        """Called when main_menu emits 'show_credits'"""
        print("[SceneManager] → main_menu.show_credits")
        # TODO: Implement credits scene
        print("  [TODO] Credits scene not yet implemented")
    
    # Scene management methods
    
    def _generate_shelburne_road(self) -> None:
        """
        Generate the Shelburne road scene.
        Called on spawn_node's 'scene_triggered' signal.
        Matches: func generate_shelburne_road() in worldtest.gd
        """
        print("[SceneManager] Generating Shelburne Road scene...")
        self.switch_scene('shelburne_road')
    
    def switch_scene(self, scene_name: str) -> None:
        """
        Unload current scene and activate a new one.
        
        Args:
            scene_name: Name of scene to activate
        """
        # Exit current scene
        if self.active_scene:
            print(f"[SceneManager] Exiting scene: {self.active_scene.name}")
            self.active_scene.exit()
            self.active_scene.cleanup()
        
        # Enter new scene
        if scene_name in self.scenes:
            self.active_scene = self.scenes[scene_name]
            print(f"[SceneManager] Entering scene: {self.active_scene.name}")
            self.active_scene.enter()
        else:
            print(f"[SceneManager] ERROR: Scene '{scene_name}' not found!")
            self.active_scene = None
    
    def get_scene(self, scene_name: str) -> Scene:
        """Get a scene by name"""
        return self.scenes.get(scene_name)
    
    def update(self, delta: float) -> None:
        """Update active scene"""
        if self.active_scene and self.active_scene.is_active:
            self.active_scene.update(delta)
    
    def render(self, display) -> None:
        """Render active scene"""
        if self.active_scene and self.active_scene.is_active:
            self.active_scene.render(display)
    
    def get_active_scene(self) -> Scene:
        """Get currently active scene"""
        return self.active_scene


# Example usage / testing
if __name__ == "__main__":
    print("Scene Manager Test")
    print("=" * 50)
    
    class FakeEngine:
        def __init__(self):
            self.display = None
    
    engine = FakeEngine()
    manager = SceneManager(engine)
    
    print("\nTesting signal emissions:")
    print("-" * 50)
    
    # Simulate spawn_node emitting scene_triggered
    print("\nSimulating: spawn_node.emit_signal('scene_triggered')")
    manager.scenes['spawn_node'].emit_signal('scene_triggered')
