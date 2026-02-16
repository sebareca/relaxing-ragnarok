# TODO

## Sword weapon overlay - STILL BROKEN, need ACT file anchor data

Completely rewrote weapon attack rendering based on deep sprite analysis:

### What changed:
- **5 weapon frames** per direction (was 3), mapped 1:1 to body frames (was [0,0,1,2,2])
- **Per-frame hand positions** from body sprite analysis (WPN_HAND_POS arrays) replace formula-based handH
- **Weapon drawn centered on hand** with grip offset (was bottom-center at formula Y position)
- **Weapon scale: SCALE*0.9** (was SCALE*0.55 — weapon was nearly half body scale)
- **Actual NW weapon frames** from sprite sheet NW section (was reusing W frames)
- **Per-frame head anchors** during attack (HEAD_ANCHOR_ATK) — head tracks body crouch
- **Grip position offset** (WPN_GRIP_OFF) shifts weapon so handle aligns with hand

### Status: Still doesn't look right. Estimated positions are not accurate enough.
### Next step: Get actual ACT files and extract real anchor point data.

### Without ACT files, positions are estimated. Tuning knobs:
- `WPN_HAND_POS[dir][frame]` - [xFrac, yFrac] on body where hand is (most impactful)
- `WPN_GRIP_OFF[frame]` - how far below weapon-center the grip is (0.35=bottom for vertical, 0.0=center for horizontal)
- Weapon scale multiplier (currently 0.9)
- `HEAD_ANCHOR_ATK[frame]` - head overlap into body per attack frame
