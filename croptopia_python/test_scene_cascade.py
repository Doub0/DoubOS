#!/usr/bin/env python3
"""
Test Scene Cascade - Validates complete worldtest.gd orchestration
Tests: spawn_node → shelburne_road → shelburne → michael_plot → zea_walk → scenetwo → shelburne loop
"""

import sys
sys.path.insert(0, '/Users/Jonas/Documents/doubOS/DoubOS/croptopia_python')

from croptopia.scene_manager import SceneManager
from croptopia.signals import SignalEmitter


class MockEngine:
    """Minimal engine mock for testing scene cascade."""
    
    def __init__(self):
        self.scene_manager = None
        self.player = None
        self.display = None
        self.running = True
        self.events_fired = []
        
        
class MockPlayer:
    """Minimal player mock for trigger testing."""
    
    def __init__(self):
        import pygame
        self.position = pygame.math.Vector2(454.75, -1183.5)  # Spawn trigger center
        self.can_move = True
        self.camera = MockCamera()
        

class MockCamera:
    """Minimal camera mock."""
    
    def __init__(self):
        self.enabled = True


def test_scene_cascade():
    """Test complete scene orchestration."""
    print("\n" + "=" * 70)
    print("SCENE CASCADE TEST")
    print("=" * 70)
    
    # Create mock engine
    engine = MockEngine()
    engine.player = MockPlayer()
    
    # Initialize SceneManager
    print("\n[Test] Initializing SceneManager...")
    manager = SceneManager(engine)
    engine.scene_manager = manager
    
    # Verify all scenes are preloaded
    print(f"\n[Test] Verifying {len(manager.scenes)} preloaded scenes:")
    for name in manager.scenes.keys():
        print(f"  ✓ {name}")
    
    # Test 1: Verify spawn_node is active
    print(f"\n[Test 1] Current active scene: {manager.active_scene.name}")
    assert manager.active_scene.name == "spawn_node", "spawn_node should be active"
    print("  ✓ spawn_node is active")
    
    # Test 2: Simulate spawn_node trigger detection
    print(f"\n[Test 2] Simulating spawn_node.scene_triggered signal...")
    manager.scenes['spawn_node'].emit_signal('scene_triggered')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "shelburne_road", "Should transition to shelburne_road"
    print("  ✓ Transition successful: spawn_node → shelburne_road")
    
    # Test 3: Simulate shelburne_road trigger completion
    print(f"\n[Test 3] Simulating shelburne_road.shelburne_generate signal...")
    manager.scenes['shelburne_road'].emit_signal('shelburne_generate')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "shelburne", "Should transition to shelburne"
    print("  ✓ Transition successful: shelburne_road → shelburne")
    
    # Test 4: Simulate Mount Crag trigger (from Shelburne)
    print(f"\n[Test 4] Simulating shelburne.mt_crag_over signal...")
    manager.scenes['shelburne'].emit_signal('mt_crag_over')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "michael_plot", "Should transition to michael_plot"
    print("  ✓ Transition successful: shelburne → michael_plot")
    
    # Test 5: Simulate Michael Plot completion
    print(f"\n[Test 5] Simulating michael_plot.michael_plot_over signal...")
    manager.scenes['michael_plot'].emit_signal('michael_plot_over')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "zea_walk_cutscene", "Should transition to zea_walk_cutscene"
    print("  ✓ Transition successful: michael_plot → zea_walk_cutscene")
    
    # Test 6: Simulate Zea walk cutscene completion
    print(f"\n[Test 6] Simulating zea_walk_cutscene.cutscene_over signal...")
    manager.scenes['zea_walk_cutscene'].emit_signal('cutscene_over')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "scenetwo", "Should transition to scenetwo"
    print("  ✓ Transition successful: zea_walk_cutscene → scenetwo")
    
    # Test 7: Simulate SceneTwo completion
    print(f"\n[Test 7] Simulating scenetwo.cutscene_finished signal...")
    manager.scenes['scenetwo'].emit_signal('cutscene_finished')
    print(f"  → Scene transitioned to: {manager.active_scene.name}")
    assert manager.active_scene.name == "shelburne", "Should transition back to shelburne"
    print("  ✓ Transition successful: scenetwo → shelburne (loop complete!)")
    
    # All tests passed!
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - Scene cascade working correctly!")
    print("=" * 70)
    print("\nScene Flow Summary:")
    print("  spawn_node (trigger)")
    print("    ↓")
    print("  shelburne_road (checkpoint cutscene)")
    print("    ↓")
    print("  shelburne (main town + NPC)")
    print("    ↓")
    print("  michael_plot (building area)")
    print("    ↓")
    print("  zea_walk_cutscene (animated walk)")
    print("    ↓")
    print("  scenetwo (dialogue scene)")
    print("    ↓")
    print("  shelburne (return to town - LOOP)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        test_scene_cascade()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
