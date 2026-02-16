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
- `settings.json` - **All gameplay constants** (spawning, combat, progression, visuals, etc.) — edit this to tune the game
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
- At startup, loads 4 data files: core sprites, `monster_stats.json`, `sprites/manifest.json`, `settings.json` — game waits for all via `tryStart()`
- All ~700 enemy sprites are loaded progressively in background after game starts (5 parallel loaders, sorted weakest-first by composite stat score)
- Auto frame extraction: `extractFrames(img)` scans sprite sheet pixel data to detect Row 0 idle frames (no manual coordinates needed)

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

## Settings & Constants (`settings.json`)
- **ALL gameplay constants are externalized** in `settings.json` — **NEVER hardcode magic numbers** in index.html
- Settings are loaded at startup and accessed via the global `S` object (e.g. `S.combat.crit_chance`, `S.boss.scale_multiplier`)
- If `settings.json` fails to load, hardcoded `DEFAULTS` object in index.html is used as fallback
- `mergeDefaults(target, defaults)` deep-merges user settings over defaults, so partial settings.json files work fine
- **When adding new gameplay features**, add the constant to both `DEFAULTS` in index.html AND `settings.json`, then reference via `S.category.key`

### Settings Categories
- **`spawning`**: `max_monsters`, `spawn_timer_min`, `spawn_timer_random`, `initial_monster_count`
- **`player`**: `initial_str`, `initial_agi`, `move_speed`, `initial_atk_cooldown`, `base_exp_max`, `job_exp_max`, `attack_range`
- **`combat`**: `damage_base`, `damage_per_level`, `damage_variance`, `crit_chance`, `crit_multiplier`, `cleave_chance`, `cleave_damage_ratio`, `cleave_range`, `double_attack_chance`, `double_attack_delay_ms`
- **`progression`**: `exp_multiplier_per_level`, `job_exp_multiplier_per_level`, `job_exp_ratio`, `str_per_level`, `atk_cooldown_reduction_per_level`, `min_atk_cooldown`, `zeny_ratio`, `zeny_bonus_max`
- **`boss`**: `kill_interval`, `scale_multiplier`, `speed_min`, `speed_random`, `aura_size`, `aura_pulse_speed`, `hp_bar_width`, `hp_bar_height`, `escort_count_min`, `escort_count_random`, `escort_distance_min`, `escort_distance_random`, `candidate_max_level`, `candidate_max_hp`, `level_match_tolerance`, `selection_level_diff`, `death_shake_duration`, `zeny_multiplier`, `champion_hp_multiplier`, `champion_exp_multiplier`
- **`monsters`**: `speed_min`, `speed_random`, `wander_timer_min`, `wander_timer_random`, `bounds_padding_x`, `bounds_padding_top`, `bounds_padding_bottom`, `frame_duration`, `death_duration`, `hurt_duration`
- **`visuals`**: `sprite_scale`, `shake_magnitude`, `crit_shake_duration`, `dmg_num_rise_speed`, `dmg_num_lifetime`, `dmg_num_crit_font_size`, `dmg_num_normal_font_size`, `dmg_num_stroke_width`, `dmg_num_x_offset_range`, `dmg_num_crit_scale`, `levelup_display_duration`
- **`particles`**: `lifetime_min`, `lifetime_random`, `speed_min`, `speed_random`, `size_min`, `size_random`, `gravity`, `crit_count`, `boss_death_gold`, `boss_death_type`, `boss_death_white`, `normal_death_type`, `normal_death_white`, `levelup_gold`, `levelup_white`
- **`items`**: `drop_chance`, `drop_types`, `spawn_offset_x`, `spawn_offset_y`, `despawn_time`, `bob_speed`, `bob_amplitude`
- **`loading`**: `parallel_sprite_loaders`, `sprite_load_delay_ms`, `auto_extract_target_height`, `frame_extract_min_gap`, `frame_extract_min_size`, `frame_extract_max_frames`, `frame_extract_alpha_threshold`

## Monster Spawning & Boss System
- Monsters spawn sorted by composite stat score: `level*2 + hp/50 + (atk_min+atk_max)/5 + defense/10 + (str+agi+vit+int+dex+luk)/20`
- Dynamic spawn weighting: `weight / (1 + levelDiff/10)` — monsters far below player level spawn less often
- Boss types (`is_boss`/`is_mvp` in monster_stats.json) are excluded from regular spawning (`weight: 0`)
- Every `S.boss.kill_interval` kills, a boss group spawns: one boss with golden aura + escort ring of smaller monsters
- Boss candidates filtered from monster_stats.json by `candidate_max_level` and `candidate_max_hp`
- If the boss has a loaded sprite (`isBossType: true`), that sprite is used; otherwise falls back to `bossCandidates` list
- Poring is NOT in monster_stats.json (rAthena DB) — its stats are hardcoded in `processMonsterStats()`

## Visual Style
- Must look like actual Ragnarok Online (reference screenshots in example_maps/)
- Use actual RO sprite sheets, NOT canvas-drawn approximations
- Damage numbers: HUGE, bold Impact font, gradient fill, thick black outline
- Terrain: Natural painted grass with organic dirt patches
- UI: White/light gray windows, RO-style HP/SP/EXP bars
