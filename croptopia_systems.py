"""
CROPTOPIA SYSTEMS - Extended Game Mechanics
=============================================

Additional systems for the complete Croptopia recreation:
- World layout and entity spawning
- Dialogue system with JSON integration
- Quest tracking system
- Economy and merchant system
- Save/load functionality
- Complete animation frame extraction from TSCN files
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

ASSET_PATH = Path(__file__).parent / "croptopia_assets"
SAVE_PATH = Path(__file__).parent / "saves"
SAVE_PATH.mkdir(exist_ok=True)


# ============================================================================
# DIALOGUE AND QUESTS
# ============================================================================

@dataclass
class Quest:
    """Quest tracking (from npc_quest.gd)."""
    quest_id: str
    title: str
    description: str
    npc_name: str
    objectives: List[str]
    rewards: Dict[str, int]  # item: quantity
    completed: bool = False
    active: bool = False
    progress: int = 0


class DialogueSystem:
    """Manages NPC dialogue chains (from dialogueplayer.gd)."""

    def __init__(self):
        self.dialogues: Dict[str, List[str]] = {}
        self.current_dialogue_index = 0
        self.current_npc = None
        self.load_dialogues()

    def load_dialogues(self):
        """Load dialogue files from assets directory (would be JSON files)."""
        # In actual implementation, would load from .json files in croptopia_assets/dialogues/
        # For now, hardcode some example dialogues
        self.dialogues = {
            "zea": [
                "Hello, Michael! Have you seen anything strange lately?",
                "My mother is very ill... I'm worried about her.",
                "Could you help me gather some ingredients to make medicine?",
                "I'll pay you well if you can find them!"
            ],
            "philip": [
                "Welcome to my shop!",
                "I have potions and rare items for sale.",
                "What can I help you with today?"
            ],
            "mark": [
                "The trees around here are perfect for wood.",
                "Be careful in the forest - strange things have been happening.",
                "I've seen dark figures moving at night."
            ]
        }

    def get_dialogue(self, npc_name: str, line_index: int) -> Optional[str]:
        """Get a specific dialogue line."""
        if npc_name not in self.dialogues:
            return None
        lines = self.dialogues[npc_name]
        if 0 <= line_index < len(lines):
            return lines[line_index]
        return None

    def get_all_dialogue(self, npc_name: str) -> Optional[List[str]]:
        """Get all dialogue for an NPC."""
        return self.dialogues.get(npc_name)


class QuestSystem:
    """Quest tracking and management (from npc_quest.gd)."""

    def __init__(self):
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: List[str] = []
        self.quest_log: Dict[str, Quest] = {}
        self._init_default_quests()

    def _init_default_quests(self):
        """Initialize default quests."""
        # Main quest: Help Zea save her mother
        self.quest_log["main_quest_1"] = Quest(
            quest_id="main_quest_1",
            title="Save Zea's Mother",
            description="Zea's mother is ill. Gather ingredients to make medicine.",
            npc_name="zea",
            objectives=[
                "Find 5 Elderberries",
                "Find 3 Sorrels",
                "Find 2 Chives",
                "Return ingredients to Zea"
            ],
            rewards={"gold": 500, "experience": 1000}
        )

    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest."""
        if quest_id not in self.quest_log:
            return False
        quest = self.quest_log[quest_id]
        quest.active = True
        self.active_quests[quest_id] = quest
        return True

    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest."""
        if quest_id not in self.active_quests:
            return False
        quest = self.active_quests[quest_id]
        quest.completed = True
        self.completed_quests.append(quest_id)
        del self.active_quests[quest_id]
        return True

    def update_quest_progress(self, quest_id: str, objective_index: int):
        """Update quest progress."""
        if quest_id in self.active_quests:
            quest = self.active_quests[quest_id]
            quest.progress = objective_index


# ============================================================================
# ECONOMY SYSTEM (from economy_manager.gd)
# ============================================================================

class EconomyManager:
    """Economy and merchant system (from economy_manager.gd)."""

    def __init__(self):
        self.player_gold = 0
        self.base_prices = {
            "Wheat": 1,
            "Chive": 2,
            "Potato": 3,
            "Elderberry": 5,
            "Sorrel": 4,
            "Redbaneberry": 6,
            "Birch": 2,
            "Oak": 3,
            "Maple": 4
        }
        self.inflation = 1.0
        self.economic_state = "normal"  # normal, high_demand, low_demand
        self.update_economy()

    def update_economy(self):
        """Update economy state (from economy_manager.gd _process)."""
        # Simulate price fluctuation
        import random
        self.inflation = random.uniform(0.75, 1.25)
        
        if self.inflation > 1.1:
            self.economic_state = "high_demand"
        elif self.inflation < 0.9:
            self.economic_state = "low_demand"
        else:
            self.economic_state = "normal"

    def get_price(self, item_name: str) -> float:
        """Get current price of an item (from economy_manager.gd)."""
        base_price = self.base_prices.get(item_name, 1.0)
        return base_price * self.inflation

    def sell_item(self, item_name: str, quantity: int = 1) -> int:
        """Sell an item and get gold (from merchant interactions)."""
        price = self.get_price(item_name)
        total = int(price * quantity)
        self.player_gold += total
        return total

    def buy_item(self, item_name: str, quantity: int = 1) -> bool:
        """Buy an item (from merchant interactions)."""
        price = self.get_price(item_name)
        total = int(price * quantity)
        if self.player_gold >= total:
            self.player_gold -= total
            return True
        return False


# ============================================================================
# WORLD SPAWNING AND LAYOUT
# ============================================================================

@dataclass
class EntitySpawn:
    """Entity spawn point."""
    entity_type: str  # crop, tree, npc, collectable
    entity_class: str  # e.g., "Wheat", "BirchTree", "NPC"
    position: Tuple[int, int]
    properties: Dict = None


class WorldLayout:
    """Manages world entity spawning (from shelburne.tscn structure)."""

    def __init__(self):
        self.spawns: List[EntitySpawn] = []
        self._generate_shelburne()

    def _generate_shelburne(self):
        """Generate Shelburne world layout (from shelburne.tscn)."""
        # Crop field layout
        for row in range(5):
            for col in range(8):
                x = 1000 + col * 100
                y = 500 + row * 100
                
                # Alternate crops
                if (row + col) % 3 == 0:
                    self.spawns.append(EntitySpawn("crop", "Wheat", (x, y)))
                elif (row + col) % 3 == 1:
                    self.spawns.append(EntitySpawn("crop", "Chive", (x, y)))
                else:
                    self.spawns.append(EntitySpawn("crop", "Potato", (x, y)))

        # Tree spawn points
        tree_types = ["BirchTree", "OakTree", "MapleTree", "WhitepineTree"]
        for i, tree_type in enumerate(tree_types):
            x = 2000 + i * 200
            y = 2000
            self.spawns.append(EntitySpawn("tree", tree_type, (x, y)))

        # NPC spawn points
        self.spawns.append(EntitySpawn("npc", "Zea", (1500, 3000), {"dialogue": "zea"}))
        self.spawns.append(EntitySpawn("npc", "Philip", (2500, 3500), {"dialogue": "philip"}))
        self.spawns.append(EntitySpawn("npc", "Mark", (3000, 2500), {"dialogue": "mark"}))

    def get_spawns(self, entity_type: str = None) -> List[EntitySpawn]:
        """Get spawns of a specific type."""
        if entity_type:
            return [s for s in self.spawns if s.entity_type == entity_type]
        return self.spawns


# ============================================================================
# SAVE/LOAD SYSTEM
# ============================================================================

@dataclass
class GameSave:
    """Game save state."""
    player_position: Tuple[int, int]
    player_inventory: List[Dict]
    day_count: int
    time: Tuple[int, int]  # hour, minute
    completed_quests: List[str]
    active_quests: List[str]
    player_gold: int
    world_state: Dict  # For crops/tree harvest states
    timestamp: str = ""


class SaveManager:
    """Save and load game state."""

    def __init__(self, save_dir: Path = SAVE_PATH):
        self.save_dir = save_dir
        self.save_dir.mkdir(exist_ok=True)

    def save_game(self, filename: str, game_save: GameSave):
        """Save game state."""
        game_save.timestamp = datetime.now().isoformat()
        save_file = self.save_dir / f"{filename}.sav"
        
        try:
            with open(save_file, "wb") as f:
                pickle.dump(game_save, f)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self, filename: str) -> Optional[GameSave]:
        """Load game state."""
        save_file = self.save_dir / f"{filename}.sav"
        
        if not save_file.exists():
            return None
        
        try:
            with open(save_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Load failed: {e}")
            return None

    def get_save_list(self) -> List[str]:
        """Get list of saves."""
        return [f.stem for f in self.save_dir.glob("*.sav")]


# ============================================================================
# ANIMATION FRAME EXTRACTION FROM TSCN
# ============================================================================

class TSCNAnimationExtractor:
    """Extract animation frames from TSCN files."""

    @staticmethod
    def extract_atlas_frames(tscn_path: Path) -> Dict[str, List[Tuple[int, int, int, int]]]:
        """Extract AtlasTexture regions from a TSCN file."""
        frames_by_animation = {}
        
        try:
            with open(tscn_path, 'r') as f:
                content = f.read()
            
            # Simple parsing of AtlasTexture regions
            # In format: region = Rect2(x, y, w, h)
            import re
            pattern = r'region = Rect2\((\d+), (\d+), (\d+), (\d+)\)'
            matches = re.findall(pattern, content)
            
            # Group by animation name (simple approach)
            # A real implementation would parse the full TSCN structure
            animation_name = tscn_path.stem
            frames_by_animation[animation_name] = [
                (int(m[0]), int(m[1]), int(m[2]), int(m[3])) 
                for m in matches
            ]
            
            return frames_by_animation
        except Exception as e:
            print(f"Error extracting frames from {tscn_path}: {e}")
            return {}


# ============================================================================
# CROPTOPIA GAME DATA (Consolidated Configuration)
# ============================================================================

class GameData:
    """Centralized game configuration (from GameData.gd equivalent)."""

    CROP_DATA = {
        "wheat": {
            "growth_time": 3.0,
            "animation": "wheat",
            "sprite": "pixil-frame-0 - 2024-05-17T194744.217.png"
        },
        "chive": {
            "growth_time": 2.5,
            "animation": "chive",
            "sprite": "chive.png"
        },
        "potato": {
            "growth_time": 4.0,
            "animation": "potato",
            "sprite": "potato.png"
        },
        "redbaneberry": {
            "growth_time": 6.0,
            "animation": "redbaneberry",
            "sprite": "redbaneberry.png"
        },
        "cranberry": {
            "growth_time": 5.0,
            "animation": "cranberry",
            "sprite": "cranberry.png"
        },
        "sorrel": {
            "growth_time": 2.0,
            "animation": "sorrel",
            "sprite": "sorrel.png"
        }
    }

    TREE_DATA = {
        "birch": {
            "regrow_time": 8.0,
            "sprite_sheet": "birch_tree.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "oak": {
            "regrow_time": 10.0,
            "sprite_sheet": "oak_tree.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "maple": {
            "regrow_time": 12.0,
            "sprite_sheet": "maple.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "whitepine": {
            "regrow_time": 11.0,
            "sprite_sheet": "whitepine.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "sweetgum": {
            "regrow_time": 9.0,
            "sprite_sheet": "sweetgum.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "mediumspruce": {
            "regrow_time": 10.5,
            "sprite_sheet": "mediumspruce.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        },
        "pine": {
            "regrow_time": 10.0,
            "sprite_sheet": "pine.png",
            "frames": {"full": (0, 0, 50, 50), "empty": (50, 0, 50, 50)}
        }
    }

    NPC_DATA = {
        "zea": {
            "sprite": "zea_sprite.png",
            "position": (1500, 3000),
            "dialogue_file": "zea_dialogue.json"
        },
        "philip": {
            "sprite": "philip_sprite.png",
            "position": (2500, 3500),
            "dialogue_file": "philip_dialogue.json",
            "type": "merchant"
        },
        "mark": {
            "sprite": "mark_sprite.png",
            "position": (3000, 2500),
            "dialogue_file": "mark_dialogue.json"
        }
    }
