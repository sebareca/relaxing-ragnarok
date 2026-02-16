# Attacks & Skills Reference

## Common Attack System (Auto-Attack)

### Targeting
- Player auto-targets the nearest alive monster (`updatePlayer()`)
- Click a monster to manually override target; click terrain to walk
- Target clears when the monster dies or enters `dying` state

### Movement → Attack Flow
1. If target exists and distance > `S.player.attack_range` (65px): walk toward target at `player.moveSpeed`
2. Once in range: decrement `atkTimer` by `dt*1000` each frame
3. When `atkTimer <= 0`: trigger `doAttack()`, reset `atkTimer = player.atkCooldown`
4. Attack cooldown starts at `S.player.initial_atk_cooldown` (1000ms) and decreases by `S.progression.atk_cooldown_reduction_per_level` per base level, floored at `S.progression.min_atk_cooldown` (500ms)

### Damage Calculation (`doAttack()`)
```
base = S.combat.damage_base + player.str + player.baseLv * S.combat.damage_per_level
dmg  = base + random(0, S.combat.damage_variance)
if crit: dmg *= S.combat.crit_multiplier
```
- **Crit chance**: `S.combat.crit_chance` (15%) — triggers screen shake, yellow particles, crit sound, enlarged damage number
- **Cleave**: `S.combat.cleave_chance` (40%) — hits one nearby monster within `S.combat.cleave_range` (60px) for `dmg * S.combat.cleave_damage_ratio` (50%)
- **Double Attack**: `S.combat.double_attack_chance` (30%) — fires a second `doAttack()` after `S.combat.double_attack_delay_ms` (350ms) delay via `setTimeout`

### On-Hit Effects
- Monster `hurtTimer` set to `S.monsters.hurt_duration` — tints sprite red, shows hurt frame
- Damage number spawned via `addDmgNum()` — rises, fades, pops on crits
- If HP <= 0: `killMonster()` handles death (dying animation, EXP/zeny/drops, particles, boss spawn check)

### Attack Animation
- 5-frame body animation (`SWORD_ATK_DIR`), matched 1:1 with weapon frames (`WPN_ATK_DIR`)
- Animation duration = `min(0.7s, atkCooldown/1000)` — scales with ASPD
- Weapon drawn at hand position using `WPN_HAND_POS` fractions + `WPN_GRIP_OFF` vertical offset
- Head uses `HEAD_ANCHOR_ATK` per-frame offsets to track body crouch

### Key Functions
| Function | Location | Purpose |
|---|---|---|
| `updatePlayer(dt)` | index.html | Targeting, movement, attack state machine |
| `doAttack(m)` | index.html | Damage calc, crit/cleave/double-attack rolls |
| `killMonster(m)` | index.html | Death handling, EXP, zeny, drops, particles, boss check |
| `addDmgNum(x,y,val,isCrit,isMiss)` | index.html | Spawn floating damage number |

---

## AoE Fire Ring (Q / 1 key)

### Overview
Area-of-effect skill that damages all monsters within radius of the player. Uses the fire ring effect sprite (`sprites/other/Effect_1_127418.png`). 15-second cooldown.

### Trigger
- **Keys**: `Q` or `1`
- **Conditions**: `aoeSkillTimer <= 0` (off cooldown) AND `aoeActive === null` (no animation playing) AND `player` exists
- Keyboard listener: `document.addEventListener('keydown', ...)` — fires `triggerAoE()`

### Damage Calculation (deferred to mid-animation)
```
base   = S.combat.damage_base + player.str + player.baseLv * S.combat.damage_per_level
aoeDmg = floor(base * S.aoe_skill.damage_multiplier)
per-hit = aoeDmg + random(0, S.combat.damage_variance)
```
- **Damage is NOT applied on cast** — it fires once at the midpoint frame (`floor(totalFrames/2)`) of the animation
- Handled in the update loop: when `aoeActive.frame >= aoeActive.hitFrame` and `!aoeActive.hitDone`, damage + effects trigger and `hitDone` is set
- All damage numbers display as crit-style (yellow gradient, enlarged)
- Every alive monster within `S.aoe_skill.radius` (150px) of the cast position is hit
- Monsters killed by AoE go through normal `killMonster()` — full EXP, zeny, drops, boss spawn counting

### Visual Effect
- **Sprite**: `sprites/other/Effect_1_127418.png` — multi-row sprite sheet, all frames extracted via `extractAllFrames()`
- **Frame extraction**: `extractAllFrames()` scans every row band (not just Row 0 like `extractFrames()`), returns flat array of `[x, y, w, h]` rects in reading order (left-to-right, top-to-bottom)
- **Frames cached** in `aoeFramesCache` on first use
- **Animation**: each frame displayed for `S.aoe_skill.frame_duration` (0.06s), centered on player's cast position
- **Scale**: `S.aoe_skill.scale` (2.5x) — drawn at 90% opacity on top of entities, under particles/damage numbers
- Animation state stored in `aoeActive = { frame, frameTimer, x, y, frames[], hitDone, hitFrame }`
- When `frame >= frames.length`, animation ends (`aoeActive = null`)

### Effects (at mid-animation hit frame)
1. Screen shake for `S.aoe_skill.shake_duration` (0.3s)
2. Fire particles: 25 red-orange (`#ff4400`) + 25 orange (`#ffaa00`) + 10 white
3. Sound: layered low boom (80Hz sawtooth) + mid rumble (120Hz sine) + crackle (200Hz square + 500Hz)
- All three effects are deferred to the hit frame along with damage (not on initial cast)

### Cooldown
- `aoeSkillTimer` set to `S.aoe_skill.cooldown` (15s) on trigger
- Decremented by `dt` each update frame
- Skill blocked while `aoeSkillTimer > 0` or `aoeActive !== null`

### Cooldown UI
- Bottom-left of screen (8px from edges), 80x16px bar
- **Ready**: solid orange bar, white text "Q: Ready"
- **On cooldown**: dark background filling left-to-right as cooldown elapses, gray text "Q: Xs" (ceiling of remaining seconds)

### State Variables
| Variable | Type | Purpose |
|---|---|---|
| `aoeSkillTimer` | number | Cooldown countdown in seconds (0 = ready) |
| `aoeActive` | object/null | Animation state `{ frame, frameTimer, x, y, frames[], hitDone, hitFrame }` |
| `aoeFramesCache` | array/null | Cached `[x,y,w,h]` frame rects from effect sprite |

### Settings (`S.aoe_skill`)
| Key | Default | Purpose |
|---|---|---|
| `cooldown` | 15 | Seconds between uses |
| `damage_multiplier` | 5 | Multiplier on base damage formula |
| `radius` | 150 | Hit radius in pixels from player |
| `frame_duration` | 0.06 | Seconds per animation frame |
| `scale` | 2.5 | Sprite render scale |
| `shake_duration` | 0.3 | Screen shake duration in seconds |
| `particle_fire` | 25 | Number of fire-colored particles per color |
| `particle_white` | 10 | Number of white particles |

### Key Functions
| Function | Purpose |
|---|---|
| `triggerAoE()` | Start animation and cooldown; damage/effects deferred to mid-animation hit frame in update loop |
| `sndAoE()` | Layered fire boom sound effect |
| `extractAllFrames(img)` | Extract all frames from multi-row sprite sheet |
