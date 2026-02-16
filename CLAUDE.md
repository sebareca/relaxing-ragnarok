# Relaxing Ragnarok - Project Rules

## Sprite Work
- **ALWAYS read SPRITES.md before doing any sprite-related work** (adding sprites, changing animations, modifying rendering, compositing layers)
- SPRITES.md contains frame coordinates, sheet layouts, compositing order, positioning rules, and extraction lessons learned
- After downloading new sprites or learning new frame data, **update SPRITES.md** with the new information
- The sprites/manifest.json file contains metadata about all downloaded assets - consult it to find the right sprite file
- **Verify frame data with automated extraction** (Python + PIL/numpy) - never trust manually measured coordinates without checking. See SPRITES.md "Frame Extraction Lessons" section
- **Head compositing**: Always use Row 0 direction frames for the head across all body states to avoid hair appearance changes

## Project Structure
- `index.html` - The entire game (single file, HTML + CSS + JS)
- `sprites/` - All sprite sheet PNGs downloaded from spriters-resource.com
- `sprites/manifest.json` - Asset manifest with metadata (category, type, dimensions)
- `ro_classes.json` - Complete class/job system metadata (class trees, stats, HP/SP formulas, ASPD, builds)
- `monster_stats.json` - Complete monster/enemy stats for all 699 enemies with sprites (see Monster Stats section)
- `example_maps/` - Reference screenshots of actual Ragnarok Online gameplay
- `SPRITES.md` - Sprite technical reference (frame data, compositing rules, positioning)
- `scripts/parse_rathena_db.py` - Script to regenerate monster_stats.json from rAthena mob database
- `scripts/fetch_monster_stats.py` - Legacy sprite→mob ID mapping (700 entries, used as reference)

## Game Architecture
- Single HTML file with inline CSS and JS
- HTML5 Canvas 2D rendering at 960x640
- Sprites loaded from `sprites/` directory (requires HTTP server to run)
- Web Audio API for sound effects
- Pre-rendered terrain on offscreen canvas

## Class System & Character Progression
- **`ro_classes.json`** - Complete RO class/job metadata for automatic character progression
- Contains: class tree (Novice → 1st → 2nd → Transcendent → 3rd → 4th), stat builds, HP/SP formulas, ASPD data, job change requirements
- **Class tree lookup**: Use `class_trees` for the 6 primary branches (swordsman, mage, archer, thief, merchant, acolyte), each with 2-1 and 2-2 paths. Use `expanded_classes` for Super Novice, Taekwon, Ninja, Gunslinger, Doram
- **Individual class data**: `classes.<class_key>` has combat_type, role, weapons, primary/secondary stats, recommended_builds, key_skills, description
- **Automatic stat allocation**: Use `recommended_builds` per class for auto-distributing stat points. Cost formula in `stat_points.stat_cost_table`. Points per level: `floor(BaseLv / 5) + 3`
- **HP/SP calculation**: Use `hp_sp_formulas.hp_coefficients` and `sp_coefficients` with the formulas to compute MAX HP/SP per class at any level. Transcendent classes get 1.25x multiplier
- **ASPD**: Use `aspd_weapon_delays` for base attack speed per class+weapon combo. Formula in `derived_stat_formulas.aspd`
- **Job change triggers**: `job_change_requirements` defines when class transitions happen (job level + base level thresholds)
- **When adding new class features**, always reference ro_classes.json for accurate data rather than hardcoding values

## Monster Stats & Enemy Data
- **`monster_stats.json`** - Complete stat data for 699 enemies (keyed by sprite filename with underscores)
- Data sourced from **rAthena renewal mob database** (680 entries) + manual estimates for 19 event/collab exclusives
- **Key per entry**: Sprite filename with spaces→underscores (e.g. `Baphomet`, `Goblin_(Axe)`, `Desert_Wolf_(Baby)`)
- **Fields per monster**: `monster_id`, `name`, `aegis_name`, `level`, `hp`, `sp`, `base_exp`, `job_exp`, `attack_min`, `attack_max`, `defense`, `magic_defense`, `str/agi/vit/int/dex/luk`, `attack_range`, `size`, `race`, `element`, `element_level`, `walk_speed`, `walk_speed_label`, `attack_delay`, `attack_motion`, `damage_motion`, `is_aggressive`, `is_boss`, `is_mvp`
- **Drops**: `drops[]` array with `{item, rate_percent}`, plus `mvp_drops[]` for MVPs
- **Estimated entries**: 19 monsters from event/collab content have `"estimated_stats": true` flag (PAD collab lits, Brazilian exclusives, etc.)
- **Regenerating**: Download rAthena mob_db.yml to /tmp/ then run `python3 scripts/parse_rathena_db.py`
- **Sprite→name mapping**: The key in monster_stats.json matches the sprite filename in `sprites/enemies/` (strip frame number suffix `_NNNNN.png`)
- **When adding new enemy features**, always reference monster_stats.json for accurate stats rather than hardcoding values

## Visual Style
- Must look like actual Ragnarok Online (reference screenshots in example_maps/)
- Use actual RO sprite sheets, NOT canvas-drawn approximations
- Damage numbers: HUGE, bold Impact font, gradient fill, thick black outline
- Terrain: Natural painted grass with organic dirt patches
- UI: White/light gray windows, RO-style HP/SP/EXP bars
