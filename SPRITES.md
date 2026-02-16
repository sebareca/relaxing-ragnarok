# Ragnarok Online Sprite Reference

## Source
All sprites downloaded from: https://www.spriters-resource.com/pc_computer/ragnarokonline/

## Sprite Sheet Structure

RO sprites are organized as sprite sheets (PNG with transparency). Each sheet contains multiple animation frames arranged in rows. Sprites are NOT on a regular grid - frame positions must be detected by scanning for non-transparent pixels.

## How RO Sprites Work

In Ragnarok Online, a character is composed of multiple layered sprites:
- **Body sprite**: The character class body (Swordsman, Mage, etc.)
- **Head sprite**: The character's head/hairstyle (separate sprite sheet, overlaid on body)
- **Weapon sprite**: The weapon held by the character (separate sprite, overlaid during attack)
- **Headgear/accessories**: Optional equipment sprites layered on top

These layers are composited together at render time, anchored to specific positions on the body sprite.

## Frame Extraction Lessons

### Extraction Method
Use Python with PIL/numpy to find frame boundaries by scanning for non-transparent pixels:
```python
from PIL import Image
import numpy as np
img = Image.open('sprite.png').convert('RGBA')
data = np.array(img)
alpha = data[:,:,3]
# 1. Find rows with pixels (alpha > 50) to get row boundaries
# 2. Within each row, find columns with pixels to get frame boundaries
# 3. For each frame region, get tight Y and X bounds
```

### Key Pitfalls
- **Alpha threshold doesn't matter much** (50 vs 200 gives identical results) - RO sprite pixels are fully opaque, not semi-transparent at edges
- **Always verify documented frame data against automated extraction** - manual measurements can be wrong (e.g. the original walk frame heights were 62-65px but actual data is 70-73px, which clipped the character's feet)
- **Frames are NOT on a regular grid** - every frame has unique position and size, must be extracted individually
- **Row detection**: scan for horizontal bands of non-transparent pixels separated by fully transparent rows

### Direction Mirroring
Only 5 unique directions need frame data (S, SW, W, NW, N). The other 3 are rendered by horizontally flipping:
- SE = flip SW frames
- E = flip W frames
- NE = flip NW frames
This cuts unique frame data nearly in half.

### Head Compositing Gotcha
Using different head sprite rows for different body states (idle vs walk vs attack) causes visual "hair changing" artifacts because each row has slightly different head appearances. **Use the same Row 0 direction frames for all body states** to keep the head consistent.

## Currently Downloaded Sprites

### Poring (sprites/poring.png) - 629x558
- **Idle/Standing** (Row 1, 8 frames): Bouncing animation
  - Frames: [7,11,37,36], [63,10,39,37], [122,9,41,39], [189,14,39,33], [251,12,37,36], [310,12,39,37], [371,10,41,39], [438,16,39,33]
- **Hurt/Dying** (Row 3-4, first 2 useful): Hit reaction
  - Frames: [12,213,37,36], [59,216,39,32]
- Contains: Poring, Santa Poring, Angeling variants
- Each frame ~37-41px wide, 33-39px tall

### Poporing (sprites/poporing.png) - 609x508
- **Idle/Standing** (Row 1, 8 frames): Same layout as Poring but green
  - Frames: [13,14,37,36], [69,13,39,37], [127,12,41,39], [187,17,39,33], [242,15,37,36], [299,14,39,37], [359,12,41,39], [423,17,39,33]
- **Hurt/Dying** (Row 3-4, first 2 useful):
  - Frames: [17,220,37,36], [75,224,39,32]

### Drops (sprites/enemies/Drops_127279.png) - 577x489
- **Idle/Standing** (Row 0, 8 frames): Bouncing animation (orange poring variant)
  - Frames: [15,19,37,36], [69,18,39,37], [127,16,41,39], [185,22,39,33], [243,18,37,36], [299,18,39,37], [363,15,41,39], [425,21,39,33]
- **Hurt** (Row 2, first 2 frames):
  - Frames: [10,217,37,36], [66,221,39,32]
- Same frame layout as Poring (poring family)

### Fabre (sprites/enemies/Fabre_127228.png) - 427x194
- **Idle/Standing** (Row 0, 8 frames): Caterpillar wiggle animation
  - Frames: [10,11,34,27], [58,11,34,27], [108,11,31,27], [154,12,33,26], [205,12,33,26], [251,12,32,25], [299,12,30,25], [344,13,32,26]
- **Hurt** (Row 1, first 2 frames):
  - Frames: [10,57,33,26], [60,55,41,26]
- Each frame ~30-34px wide, 25-27px tall

### Lunatic (sprites/enemies/Lunatic_126936.png) - 471x391
- **Idle/Standing** (Row 0, 8 frames): Rabbit hopping animation
  - Frames: [11,18,29,26], [55,18,30,25], [98,20,33,22], [142,18,30,25], [186,19,31,27], [233,20,33,26], [282,20,36,26], [333,20,33,26]
- **Hurt** (Row 5, first 2 frames):
  - Frames: [14,350,29,27], [57,350,29,27]
- Each frame ~29-36px wide, 22-27px tall

### Spore (sprites/enemies/Spore_126582.png) - 945x865
- **Idle/Standing** (Row 0, 8 frames): Mushroom bounce animation
  - Frames: [21,18,48,54], [111,19,48,52], [201,19,48,51], [291,19,48,52], [381,18,48,54], [471,18,48,53], [561,18,48,53], [651,18,48,53]
- **Hurt** (Row 6, first 2 frames):
  - Frames: [18,403,48,54], [108,405,48,50]
- Each frame ~48px wide, 51-54px tall (larger than poring)
- Uses SCALE*0.85 in-game to keep proportional

### Wolf (sprites/enemies/Wolf_126445.png) - 1018x505
- **Idle/Standing** (Row 0, 8 frames): Standing poses (may include direction variants)
  - Frames: [8,13,65,59], [93,12,76,62], [195,11,75,64], [293,16,75,60], [400,16,68,60], [500,11,67,64], [592,9,66,70], [685,9,66,70]
- Note: Row 0 frame 4 [392,24,3,11] is an artifact (skipped), frame 11 [966,34,49,13] is shadow
- Uses SCALE*0.7 in-game due to larger native size

### Skeleton (sprites/enemies/Skeleton_126591.png) - 1087x772
- **Idle/Standing** (Row 0, 8 frames): Standing poses (may include direction variants)
  - Frames: [16,20,67,79], [119,19,62,81], [218,19,63,81], [318,19,63,81], [421,20,58,80], [522,19,55,82], [619,19,61,82], [720,20,60,80]
- Each frame ~55-67px wide, 79-82px tall (tallest monster)
- Uses SCALE*0.75 in-game due to larger native size

### Swordsman Male Body (sprites/swordsman.png) - 801x992
10 rows total. Left side of each row has the main animation; right side has secondary poses.

- **Standing** (Row 0): 5 unique directions (+ sitting/dying poses on right)
  - S:  [10,10,36,72]
  - SW: [58,12,25,70]
  - W:  [95,13,33,69]
  - NW: [140,14,41,68]
  - N:  [193,12,33,70]
- **Walking S** (Row 1, 8 frames): [10,113,37,70], [59,112,35,71], [106,110,32,73], [150,111,34,72], [196,113,37,70], [245,112,35,71], [292,110,32,73], [336,110,34,73]
- **Walking SW** (Row 2, 8 frames): [10,212,32,70], [54,215,38,67], [104,217,44,65], [160,215,37,67], [209,215,32,67], [253,214,36,68], [301,214,36,68], [349,212,35,70]
- **Walking W** (Row 3, 8 frames): [10,312,25,70], [47,313,32,69], [91,315,44,67], [147,314,36,68], [195,314,25,68], [232,316,32,66], [276,315,43,67], [331,314,37,68]
- **Walking NW** (Row 4, 8 frames): [10,415,27,68], [49,414,29,69], [90,415,33,68], [135,416,28,67], [175,420,30,63], [217,420,38,63], [267,420,44,63], [323,419,39,64]
- **Walking N** (Row 5, 8 frames): [10,515,36,67], [58,511,35,71], [105,513,33,69], [150,513,34,69], [196,515,36,67], [244,511,35,71], [291,513,33,69], [336,513,34,69]
- **Attack S** (Row 6, 5 frames): [10,612,45,70], [67,611,41,71], [120,615,43,67], [175,622,47,60], [234,624,47,58]
- **Attack SW** (Row 7, 5 frames): [10,715,33,67], [55,715,33,67], [100,713,39,69], [151,721,43,61], [206,722,43,60]
- **Attack W** (Row 8, 5 frames from 6): [10,818,50,64], [72,816,40,66], [124,814,40,68], [228,819,54,63], [294,821,54,61]
- **Attack NW** (Row 9, 5 frames from 6): [10,920,41,62], [63,917,41,65], [116,916,38,66], [214,921,45,61], [271,923,45,59]
- Note: Each attack row also has a 2nd sub-sequence (6-7 frames) on the right side of the sheet

### Male Head - Brown Hair (sprites/heads/head_male_brown.png) - 752x607
11 rows, 15 frames per row. Row structure maps to body action rows.

- **Direction frames** (Row 0, first 5 frames - used for ALL body states):
  - S:  [10,15,28,25]
  - SW: [61,16,26,24]
  - W:  [112,16,24,24]
  - NW: [161,16,26,24]
  - N:  [210,15,28,25]
- **Note**: Width pattern (28,26,24,26,28) is symmetric - S/N widest, W narrowest (side view)
- **Important**: Use Row 0 direction frames for ALL body states (idle/walk/attack) to avoid hair appearance changes between states. Other rows exist but using them causes visual artifacts.
- Head Anchor offsets (pixels of overlap into body top):
  - Stand: 14, Walk: 22, Attack: 14
- Formula: `headY = player.y - bodyH + HEAD_ANCHOR[state] * SCALE`

### Swordman Swords (sprites/weapons/swordman_swords.png) - 761x2369
16 sections separated by 1px full-width separator lines. Sections 0-1 are idle/standing (tiny frames). Sections 2-5 are attack directions with full-size swing frames.

- **Section 0-1** (y=0-272): Idle/standing weapon overlay (small: ~24x20, NOT for attack)
- **Attack S** (Section 2, y=289-377, 3-frame summary): [4,290,32,80], [110,299,51,79], [216,297,86,68]
- **Attack SW** (Section 3, y=403-481, 3-frame summary): [5,403,24,79], [101,413,31,65], [141,412,78,70]
- **Attack W** (Section 4, y=513-610, 3-frame summary): [4,513,34,95], [119,525,53,86], [182,525,110,69]
- **Attack NW** (Section 5, y=637-722): Not yet fully extracted, reuse W frames
- Weapon is only drawn during attack animation
- Position: sword swings in arc from overhead (bodyH*0.55) to extended (bodyH*0.30)
- Scale: SCALE * 0.85

## Bulk Downloaded Assets (sprites/manifest.json)
All 1277 RO sprite assets organized into subfolders:
- `sprites/enemies/` - 700 monster sprites (Poring, Poporing, Baphomet, etc.)
- `sprites/classes/` - 164 class body sprites (Swordsman, Mage, Archer, etc. Male/Female/Other)
- `sprites/weapons/` - 103 weapon sprites per class
- `sprites/mounts/` - 106 premium mount sprites
- `sprites/other/` - 73 effects, homunculus, miscellaneous
- `sprites/headgear/` - 62 headgear/accessory sprites
- `sprites/npcs/` - 36 NPC sprites
- `sprites/heads/` - 35 head/hairstyle sprites (Male/Female, Original/New)

Use `sprites/manifest.json` to look up assets by name, category, or ID.
Each manifest entry: `{id, name, category, subfolder, file}`

## Direction Convention
RO uses 8 directions, enum: 0=S, 1=SW, 2=W, 3=NW, 4=N, 5=NE, 6=E, 7=SE
- South (S) = facing camera (front view) - this is the default/first direction
- Only 5 unique direction frames exist in sprite sheets (S, SW, W, NW, N)
- NE, E, SE are rendered by horizontally flipping NW, W, SW respectively
- Direction from movement vector: `atan2(dy,dx)` quantized to 8 sectors, then mapped to enum
- In the game code, `dirInfo(dir)` returns `[frameIndex (0-4), flipX (bool)]`

## Rendering Scale
Current game uses SCALE=1.8 to upscale sprites from their native ~40px size to ~70px display size.

## Compositing Order (bottom to top)
1. Shadow (ellipse on ground)
2. Body sprite
3. Head sprite (positioned relative to body anchor point)
4. Weapon sprite (visible during attack animation)
5. Headgear/accessories
6. Name label
7. HP bar
8. Damage numbers

## Head Positioning
The head sprite needs to be positioned at the top of the body sprite. In RO:
- The head anchor point is typically at the neck/shoulder area of the body
- Head position varies per animation frame (the body bobs during walk/attack)
- Each body frame has an implicit "head anchor" offset

## Important Notes
- All sprite sheets have transparent backgrounds (RGBA PNG)
- Sprites are hand-painted 2D art with soft edges and shading
- Frame sizes vary within a sheet - always use per-frame coordinates
- The sprite scale in-game should match: porings are small blobs, player is about 2x taller
