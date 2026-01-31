"""
Asset Loader - builds sprite assets from Godot resources.
Focused on player sprites from player_anim.tres.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Tuple

import pygame


class AssetLoader:
    """Loads assets from Croptopia Godot resources into pygame surfaces."""

    @staticmethod
    def load_player_assets(croptopia_root: str) -> Dict[str, pygame.Surface]:
        """
        Load player sprites from player_anim.tres and build asset keys
        used by `Player._get_sprite_key()`.

        Returns:
            Dict[str, pygame.Surface] asset map
        """

        player_anim_path = os.path.join(
            croptopia_root, "scenes", "formats", "player_anim.tres"
        )
        assets_dir = os.path.join(croptopia_root, "assets")

        if not os.path.exists(player_anim_path):
            print(f"[AssetLoader] player_anim.tres not found: {player_anim_path}")
            return {}

        with open(player_anim_path, "r", encoding="utf-8") as f:
            content = f.read()

        ext_resources = AssetLoader._parse_ext_resources(content)
        atlas_textures = AssetLoader._parse_atlas_textures(content)
        animations = AssetLoader._parse_animations(content)

        # Only load the core movement animations
        anim_names = [
            "walk_down",
            "walk_up",
            "walk_left",
            "walk_right",
            "walk_down_idle",
            "walk_up_idle",
            "walk_left_idle",
            "walk_right_idle",
        ]

        frames_by_anim: Dict[str, List[pygame.Surface]] = {}
        for name in anim_names:
            refs = animations.get(name, [])
            if not refs:
                continue
            frames: List[pygame.Surface] = []
            for ref in refs:
                frame = AssetLoader._resolve_texture_ref(
                    ref,
                    ext_resources,
                    atlas_textures,
                    assets_dir,
                    croptopia_root,
                )
                if frame is not None:
                    frames.append(frame)
            if frames:
                frames_by_anim[name] = frames

        assets: Dict[str, pygame.Surface] = {}

        dir_map = {
            "walk_down": "down",
            "walk_up": "up",
            "walk_left": "left",
            "walk_right": "right",
        }

        # Movement frames
        for anim_name, frames in frames_by_anim.items():
            if anim_name in dir_map:
                dir_key = dir_map[anim_name]
                for i, frame in enumerate(frames):
                    assets[f"player_{dir_key}_walk_{i}"] = frame
                    assets[f"player_{dir_key}_sprint_{i}"] = frame

        # Idle frames
        idle_map = {
            "walk_down_idle": "down",
            "walk_up_idle": "up",
            "walk_left_idle": "left",
            "walk_right_idle": "right",
        }
        for anim_name, dir_key in idle_map.items():
            frames = frames_by_anim.get(anim_name)
            if frames:
                assets[f"player_{dir_key}_idle"] = frames[0]

        print(f"[AssetLoader] Loaded player assets: {len(assets)}")
        return assets

    @staticmethod
    def _parse_ext_resources(content: str) -> Dict[str, str]:
        resources: Dict[str, str] = {}
        for match in re.finditer(
            r"\[ext_resource[^\]]*path=\"res://(.*?)\"[^\]]*id=\"(\S+?)\"\]",
            content,
        ):
            path = match.group(1)
            res_id = match.group(2)
            resources[res_id] = path
        return resources

    @staticmethod
    def _parse_atlas_textures(content: str) -> Dict[str, Tuple[str, Tuple[int, int, int, int]]]:
        atlas: Dict[str, Tuple[str, Tuple[int, int, int, int]]] = {}
        pattern = (
            r"\[sub_resource type=\"AtlasTexture\" id=\"(AtlasTexture_\w+)\"\]"
            r"\s*atlas = ExtResource\(\"(\S+?)\"\)"
            r"\s*region = Rect2\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)"
        )
        for match in re.finditer(pattern, content):
            atlas_id = match.group(1)
            ext_id = match.group(2)
            rect = (
                int(float(match.group(3))),
                int(float(match.group(4))),
                int(float(match.group(5))),
                int(float(match.group(6))),
            )
            atlas[atlas_id] = (ext_id, rect)
        return atlas

    @staticmethod
    def _parse_animations(content: str) -> Dict[str, List[str]]:
        animations: Dict[str, List[str]] = {}
        current_frames: List[str] = []
        in_frames = False

        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("\"frames\": ["):
                in_frames = True
                current_frames = []
                continue

            if in_frames and stripped.startswith("\"texture\":"):
                # texture can be SubResource("AtlasTexture_x") or ExtResource("id")
                texture_ref = stripped.split(":", 1)[1].strip().strip(",")
                current_frames.append(texture_ref)
                continue

            if in_frames and stripped.startswith("\"name\":"):
                # Finalize animation when name appears
                name = stripped.split("&\"")[1].split("\"")[0]
                animations[name] = list(current_frames)
                in_frames = False
                continue

        return animations

    @staticmethod
    def _resolve_texture_ref(
        texture_ref: str,
        ext_resources: Dict[str, str],
        atlas_textures: Dict[str, Tuple[str, Tuple[int, int, int, int]]],
        assets_dir: str,
        croptopia_root: str,
    ) -> pygame.Surface | None:
        # SubResource("AtlasTexture_x")
        if texture_ref.startswith("SubResource"):
            atlas_id = texture_ref.split("\"")[1]
            if atlas_id not in atlas_textures:
                return None
            ext_id, rect = atlas_textures[atlas_id]
            tex_path = ext_resources.get(ext_id)
            if not tex_path:
                return None
            full_path = AssetLoader._resolve_asset_path(tex_path, assets_dir, croptopia_root)
            if not full_path:
                return None
            image = pygame.image.load(full_path).convert_alpha()
            x, y, w, h = rect
            return image.subsurface(pygame.Rect(x, y, w, h)).copy()

        # ExtResource("id")
        if texture_ref.startswith("ExtResource"):
            ext_id = texture_ref.split("\"")[1]
            tex_path = ext_resources.get(ext_id)
            if not tex_path:
                return None
            full_path = AssetLoader._resolve_asset_path(tex_path, assets_dir, croptopia_root)
            if not full_path:
                return None
            return pygame.image.load(full_path).convert_alpha()

        return None

    @staticmethod
    def _resolve_asset_path(path: str, assets_dir: str, croptopia_root: str) -> str | None:
        # Normalize: remove leading assets/ to avoid duplication
        clean_path = path.replace("assets/", "")

        candidates = [
            os.path.join(assets_dir, clean_path),
            os.path.join(croptopia_root, clean_path),
        ]
        for candidate in candidates:
            candidate = os.path.normpath(candidate)
            if os.path.exists(candidate):
                return candidate
        return None
