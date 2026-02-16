# Enemy Sprite Standardization

## Overview

Monsters transition from **auto-extracted** sprites (single idle row, no direction) to **standardized** sprites with full animation states and directional facing. This document covers the standardized format and workflow.

## Sprite Sheet Layout (`sprites/enemies_x/`)

Standardized sheets use a uniform grid of cells. Each row is one animation state + direction combination:

| Row | Label        | Description                          |
|-----|-------------|--------------------------------------|
| 0   | Standing S  | Idle facing south (toward camera)     |
| 1   | Standing N  | Idle facing north (away from camera)  |
| 2   | Walk S      | Walking south                         |
| 3   | Walk N      | Walking north                         |
| 4   | Attack S    | Attack animation south                |
| 5   | Attack N    | Attack animation north                |
| 6   | Hurt S      | Hit reaction south                    |
| 7   | Hurt N      | Hit reaction north                    |
| 8   | Dying S     | Death animation south                 |
| 9   | Dying N     | Death animation north                 |

- Cell size and frame count per row are defined in `sprite_overrides.json`
- Columns are left-to-right animation frames within each row
- Rows with fewer frames than `cols` leave trailing cells empty

## Override System (`sprite_overrides.json`)

Each monster entry has:
- **`source`**: Path to standardized sheet in `sprites/enemies_x/`
- **`cell`**: `[width, height]` of each grid cell in pixels
- **`cols`**: Max columns in the grid
- **`rows`**: Object mapping row index to `{label, frames}`
- **`status`**: `done` (ready), `wip` (in progress), `skip` (use auto-extraction)

The game loads overrides at startup. Monsters with `status: "done"` use the enhanced rendering path with direction-aware animations. All others use the legacy auto-extraction path.

## How It Works in the Game

1. `sprite_overrides.json` is fetched at startup alongside other JSON data
2. `loadEnhancedSprites()` processes each `done` entry:
   - Loads the standardized sheet image
   - Builds an `animations` object mapping keys like `walk_s`, `hurt_n` to frame rectangles
   - Marks the `MONSTER_TYPES` entry as `enhanced`
3. Monsters track a `facing` direction (`'s'` or `'n'`) based on their wander angle
4. `drawMonster()` checks for `enhanced` flag and renders using the appropriate directional animation

## Workflow: Adding a New Monster

1. **Identify the monster** - Find its original sprite sheet in `sprites/enemies/`
2. **Extract and arrange frames** - Create a standardized grid sheet with all states/directions
3. **Save to `sprites/enemies_x/`** - Use the monster's name (e.g., `Poporing.png`)
4. **Add entry to `sprite_overrides.json`** - Define cell size, column count, and row labels
5. **Set status to `done`** - The game will automatically use it on next load
6. **Test** - Verify all animation states play correctly in both directions

## Row Label Convention

Labels follow the pattern `"<State> <Direction>"`:
- States: `Standing`, `Walk`, `Attack`, `Hurt`, `Dying`
- Directions: `S` (south/toward camera), `N` (north/away from camera)

Labels are converted to animation keys by lowercasing and replacing spaces with underscores: `"Walk S"` becomes `walk_s`.

## Current Progress

See `sprite_overrides.json` for per-monster status. Currently standardized:
- Poring (10 rows, 4 cols, 92x74 cells)
