# TODO

## Sword weapon overlay broken during attack animation

The sword sprite appears briefly in multiple wrong positions during the attack swing. This was introduced when fixing two original issues:

1. **Original problem**: Sword was invisible during attacks (weapon frames were from the idle/standing section of the sprite sheet - tiny 24x20px frames instead of actual attack frames)
2. **Original problem**: Attack animation was choppy and direction-locked (always used south-facing body frames)

**What was changed**:
- Replaced `WPN_ATK` (idle frames from section 0) with `WPN_ATK_DIR` (attack frames from sections 2-5, up to 86x68px)
- Added `SWORD_ATK_DIR` with per-direction body attack frames (Rows 6-9)
- Changed weapon positioning to use a swing arc formula: `wpnXOff=(10+swing*14)*(flipX?-1:1)`, `wpnY=p.y-bodyH*(0.55-swing*0.25)`
- Weapon drawn at `SCALE*0.85`
- 3 weapon frames mapped to 5 body frames via `[0,0,1,2,2]`

**Current symptom**: The weapon sprite flashes in multiple regions during the attack. Likely causes:
- Weapon frame coordinates from automated extraction may not be the correct attack overlay frames (the sprite sheet has 16 sections and the mapping to directions/actions is assumed, not verified)
- The positioning formula (swing arc) doesn't account for per-frame anchor points that RO sprites normally have (from ACT files)
- The 3-to-5 frame mapping may cause visual jumps when the weapon frame switches
- Weapon scale (0.85) and center-bottom anchoring may not match how these overlay frames are designed to composite
