# TODO

## Sword weapon overlay - STILL BROKEN, need ACT file anchor data

### Why this is broken

In Ragnarok Online, character sprites are composited from layers (body + head + weapon). Each layer's
position is defined by **anchor points** stored in ACT (Action) files — binary animation files that
ship with the game client. Each body animation frame has an anchor point (x, y) that tells the
renderer exactly where the head attaches. Similarly, weapon sprites have their own ACT files with
per-frame positions.

Our sprite sheets (from spriters-resource.com) are just PNG rips — they have the pixel data but
**none of the animation metadata** (anchor points, frame timing, layer offsets). Without that data,
we're guessing where to draw the head and weapon during attacks, and the guesses are wrong.

Walking looks fine because the body barely moves (head stays centered, no weapon). Attacking looks
broken because the body crouches, lunges, and swings — every frame needs different head/weapon offsets.

### What we learned about ACT files

**Format**: Binary files, header "AC", version 0x200-0x205. Structure:
- Actions grouped in sets of 8 (one per direction: S/SW/W/NW/N/NE/E/SE)
- Player action groups: 0=stand, 1=walk, 2=sit, 3=pickup, 4=attackwait, 5=attack1, 6=hurt, etc.
- Each frame has layers (sprite references + positions) and **anchor points** (x, y offsets)
- Anchor point = head attachment position relative to body origin (character's feet)

**Compositing formula** (from roBrowser source):
```
head_render_x = body_anchor.x - head_anchor.x
head_render_y = body_anchor.y - head_anchor.y
```

**Real data extracted from Guillotine Cross (melee class, same job tree)**:
```
Attack S direction (5 frames):
  F0: anchor (3,-66)   — head 66px above feet, 3px right (windup)
  F1: anchor (3,-65)   — almost same
  F2: anchor (-6,-49)  — HEAD DROPS 17px, shifts 9px left (body crouches into swing)
  F3: anchor (-7,-49)  — continuing
  F4: anchor (-19,-49) — head 22px left of start (follow-through lunge)

Attack W direction:
  F0: anchor (13,-79)  — head higher in side view
  F1: anchor (13,-77)
  F2: anchor (4,-80)
  F3: anchor (3,-80)
  F4: anchor (-3,-79)  — less vertical change, mostly horizontal shift
```

Key patterns from comparing 10 classes:
- Melee classes (GC, Shadow Chaser, Assassin Cross) have **dynamic anchors** that shift per frame
- Ranged/magic classes (Ranger, Wizard, Professor) have **static anchors** (same for all frames)
- S and SW share identical anchors; W and NW share identical anchors
- E/SE/NE are mirrors of W/NW/SW with flipped X values

### What we already changed (v2 rewrite, still not right)
- 5 weapon frames per direction (was 3), mapped 1:1 to body frames (was [0,0,1,2,2])
- Per-frame hand positions from visual estimates (WPN_HAND_POS arrays)
- Weapon drawn centered on hand with grip offset
- Weapon scale: SCALE*0.9 (was SCALE*0.55)
- Actual NW weapon frames from sprite sheet NW section (was reusing W)
- Per-frame head anchors during attack (HEAD_ANCHOR_ATK)

### How to continue: extract exact swordsman ACT data

**Step 1: Download kRO data.grf** (~2-3GB)

Full client (2023-04-04):
https://mega.nz/folder/jUsDgRxQ#ttLmLjPY9p9cfU5_ShWVCw

Just data.grf (2020-06-03):
https://mega.nz/file/ci4l2LLK#_MBdWO_VGkIHXAufxd4ywJf-DUVE6QpoO-Es6-mTccQQ

Also rdata.grf (may be needed):
https://mega.nz/file/0v4hGBDZ#7qkuFVuDGmzJqhkOBsO84epzCADfpK93Edpejnk6C7A

**Step 2: Extract the 3 ACT files we need**

The files inside data.grf (Korean EUC-KR paths):
- Body: `data/sprite/인간족/몸통/남/검사_남.act` (Swordsman male body)
- Head: `data/sprite/인간족/머리통/남/1_남.act` (Male head style 1)
- Weapon: `data/sprite/인간족/검사/검사_남.act` or similar (Sword weapon)

We have a Python GRF reader (written inline during research) and the ACT parser at:
`scripts/parse_act.py`

```bash
# Once data.grf is downloaded, extract and parse:
python3 scripts/parse_act.py /path/to/검사_남.act --focus 5    # attack1 anchors
python3 scripts/parse_act.py /path/to/검사_남.act --json        # full JSON dump
```

**Step 3: Apply the real anchor data to index.html**

Replace the estimated `WPN_HAND_POS`, `HEAD_ANCHOR_ATK`, and `WPN_GRIP_OFF` arrays
with values derived from the actual ACT anchor points. The head compositing changes to:
```javascript
// Per-frame head offset from ACT data (not estimated)
const HEAD_ATK_ANCHOR_S = [[+3,-66],[+3,-65],[-6,-49],[-7,-49],[-19,-49]];
// headX = playerX + anchor.x * SCALE_FACTOR
// headY = playerY + anchor.y * SCALE_FACTOR
```

We'll also need the weapon ACT data for proper weapon-to-body alignment.

**Step 4: Also extract weapon ACT for sword positioning**

The weapon ACT file has its own anchor points per frame. The weapon is positioned using
the same body_anchor - weapon_anchor formula. This replaces all the hand-position guessing.

### Tools and references
- ACT parser: `scripts/parse_act.py` (supports --json, --focus, --all-groups)
- ACT format spec: https://github.com/rdw-archive/RagnarokFileFormats/blob/master/ACT.MD
- roBrowser compositing: https://github.com/MrAntares/roBrowserLegacy (src/Renderer/Entity/EntityRender.js)
- Extracted sample data: `/tmp/ro_act_files/` (10 third-class body ACTs from nodelay GRF)
- Full anchor dump: `/tmp/guillotine_cross_m_anchors.json`

### Current tuning knobs (estimated, will be replaced by ACT data)
- `WPN_HAND_POS[dir][frame]` - [xFrac, yFrac] on body where hand is
- `WPN_GRIP_OFF[frame]` - grip offset below weapon center
- Weapon scale multiplier (currently 0.9)
- `HEAD_ANCHOR_ATK[frame]` - head overlap into body per attack frame

---

## Monster Sprite Tuning (692 monsters)

700 monster sprites use auto-extraction (`extractFrames()`) which doesn't work well for all sprite sheets. Each monster needs visual inspection and potentially manual frame overrides in `sprite_overrides.json`.

8 monsters are already hand-tuned in code: Poring, Poporing, Drops, Fabre, Lunatic, Spore, Wolf, Skeleton.

### Sprite Sheet Structure

Each monster PNG contains animation sections laid out in rows. The extractor must identify and extract ALL of these sections:

1. **Standing** (idle) — the default looping animation
2. **Walking** — movement frames (sometimes grouped with Attacking)
3. **Attacking** — attack animation (sometimes grouped with Walking)
4. **Hurt** — hit reaction (sometimes grouped with Dying)
5. **Dying** — death animation (sometimes grouped with Hurt)

**Important**: Sprite sheets may contain extra data that must be IGNORED:
- Text labels baked into the image ("Standing", "Walking & Attacking", etc.)
- Variant monsters on the same sheet (e.g. Poring sheet has Santa Poring and Angeling too)
- Accessory/equipment pieces (hats, weapons, wings, halos)
- Pet/mount variants
- Effect sprites

The extractor must distinguish real animation frames from this extra data. Each section's frames should be extracted separately per monster.

### Procedure (Per Monster)

#### Step 1: Generate debug image
```bash
python3 scripts/sprite_debug.py <MonsterName>
```
Creates `sprites/debug/<MonsterName>_debug.png` showing:
- Full sprite sheet with row bands highlighted
- Auto-detected frame bounding boxes (colored, numbered F0-F7)
- Frame coordinates on right panel
- Extracted frames rendered at game scale at bottom

#### Step 2: Review the debug image
Check in `sprites/debug/<MonsterName>_debug.png`:
- Are the correct frames detected? (Should be idle animation from Row 0)
- Are bounding boxes tight? (No extra whitespace, no clipping)
- Is the scale reasonable? (~60-80px rendered height)
- Right number of frames? (Most RO sprites have 4-8 idle frames)

#### Step 3: Describe issues to Claude
Common issues:
- "Frame F2 is too wide - merging two frames into one"
- "Wrong row - idle is Row 1, not Row 0"
- "Scale too big/small"
- "Only finding 2 frames but should be 6"
- "Feet are cut off"

#### Step 4: Add override to sprite_overrides.json
```json
{
  "MonsterName": {
    "idle": [[sx, sy, sw, sh], ...],
    "scale": 1.2,
    "status": "done"
  }
}
```

#### Step 5: Verify
```bash
python3 scripts/sprite_debug.py <MonsterName> --show-overrides
```

#### Tips
- `--row N` to test different rows
- `--gap N` to adjust frame separation (default 3px)
- `--alpha N` to adjust transparency threshold (default 50)
- `--list` to see all names
- `--all` to batch-generate all debug images

### Quick Batch Triage
```bash
python3 scripts/sprite_debug.py --all
# Then browse sprites/debug/ to spot problems
```

### Monster Checklist

`[x]` done | `[~]` WIP | `[-]` looks fine | `[ ]` not checked

#### Enhanced (full directional animations via sprite_overrides.json)
- [x] Poring — standardized sheet in enemies_x/, 10 rows (stand/walk/attack/hurt/dying × S/N)

#### Hand-Tuned (idle + hurt only)
- [x] Poporing
- [x] Drops
- [x] Fabre
- [x] Lunatic
- [x] Spore
- [x] Wolf
- [x] Skeleton

#### Auto-Extracted (692 remaining)
- [ ] Abysmal_Knight
- [ ] Acidus_(Blue)
- [ ] Acidus_(Gold)
- [ ] Agav
- [ ] Aira
- [ ] Alarm
- [ ] Alice
- [ ] Alicel
- [ ] Aliot
- [ ] Aliza
- [ ] Alligator
- [ ] Am_Mut
- [ ] Ambernite
- [ ] Amdarais
- [ ] Amelit
- [ ] Amon_Ra
- [ ] Anacondaq
- [ ] Ancient_Mimic
- [ ] Ancient_Mummy
- [ ] Ancient_Tree
- [ ] Ancient_Worm
- [ ] Andre
- [ ] Angra_Mantis
- [ ] Angry_Penguin
- [ ] Anolian
- [ ] Antique_Book
- [ ] Antler_Scaraba
- [ ] Antler_Scaraba_Egg
- [ ] Antonio
- [ ] Anubis
- [ ] Apocalipse
- [ ] Aqua_Elemental
- [ ] Arc_Angeling
- [ ] Arc_Elder
- [ ] Archdam
- [ ] Arclouze
- [ ] Argiope
- [ ] Argos
- [ ] Assaulter
- [ ] Aster
- [ ] Atroce
- [ ] Aunoe
- [ ] Baba_Yaga
- [ ] Bacsojin
- [ ] Bakonawa
- [ ] Banaspaty
- [ ] Bandit
- [ ] Bangungot
- [ ] Banshee
- [ ] Banshee_Master
- [ ] Baphomet
- [ ] Baphomet_Jr
- [ ] Baroness_of_Retribution
- [ ] Bathory
- [ ] Beelzebub
- [ ] Beetle_King
- [ ] Beholder
- [ ] Beholder_Master
- [ ] Big_Bell
- [ ] Bigfoot
- [ ] Bijou
- [ ] Blazer
- [ ] Bloody_Butterfly
- [ ] Bloody_Knight
- [ ] Bloody_Murderer
- [ ] Blue_Unicorn
- [ ] Boa
- [ ] Boiled_Rice
- [ ] Boitata
- [ ] Bomb_Poring
- [ ] Bongun
- [ ] Botaring
- [ ] Bradium_Golem
- [ ] Breeze
- [ ] Brilight
- [ ] Brinaranea
- [ ] Bungisngis
- [ ] Butoijo
- [ ] Buwaya
- [ ] Byorgue
- [ ] Caramel
- [ ] Carat
- [ ] Cat_O_Nine_Tails
- [ ] Caterpillar
- [ ] Cendrawasih
- [ ] Cenere
- [ ] Centipede
- [ ] Charleston
- [ ] Chepet
- [ ] Chimera_(Green)
- [ ] Chimera_(Red)
- [ ] Choco
- [ ] Chonchon
- [ ] Christmas_Cookie
- [ ] Clock
- [ ] Cobalt_Mineral
- [ ] Coco
- [ ] Comodo
- [ ] Condor
- [ ] Constant
- [ ] Cookie
- [ ] Cornus
- [ ] Cornutus
- [ ] Corruption_Root
- [ ] Crab
- [ ] Cramp
- [ ] Creamy
- [ ] Creamy_Fear
- [ ] Creeper
- [ ] Cruiser
- [ ] Crystals
- [ ] Curupira
- [ ] DR815
- [ ] Daehyon
- [ ] Dame_of_Sentinel
- [ ] Dandelion
- [ ] Dark_Coelacanth
- [ ] Dark_Frame
- [ ] Dark_Illusion
- [ ] Dark_Lord
- [ ] Dark_Pinguicula
- [ ] Dark_Priest
- [ ] Dark_Shadow
- [ ] Dead_Plankton
- [ ] Deathword
- [ ] Deleter_(Ground)
- [ ] Deleter_(Sky)
- [ ] Demon_Pungus
- [ ] Deniro
- [ ] Desert_Wolf
- [ ] Desert_Wolf_(Baby)
- [ ] Despero_of_Thanatos
- [ ] Detardeurus
- [ ] Deviace
- [ ] Deviling
- [ ] Deviruchi
- [ ] Deviruchi_(White)
- [ ] Diabolic
- [ ] Dimik
- [ ] Dimik_(Blue)
- [ ] Dimik_(Green)
- [ ] Dimik_(Orange)
- [ ] Dimik_(Red)
- [ ] Disguise
- [ ] Dokebi
- [ ] Dolomedes
- [ ] Dolor_of_Thanatos
- [ ] Draco
- [ ] Dracula
- [ ] Dragon_Egg
- [ ] Dragon_Fly
- [ ] Dragon_Tail
- [ ] Drainliar
- [ ] Drake
- [ ] Driller
- [ ] Drosera
- [ ] Dryad
- [ ] Dullahan
- [ ] Dumpling_Child
- [ ] Duneyrr
- [ ] Dustiness
- [ ] Echio
- [ ] Eclipse
- [ ] Eddga
- [ ] Eggyra
- [ ] Elder
- [ ] Elder_Willow
- [ ] Elvira
- [ ] Emelit
- [ ] Enchanted_Peach_Tree
- [ ] Engkanto
- [ ] Entweihen_Crothen
- [ ] Event_Firefox
- [ ] Evil_Druid
- [ ] Evil_Fanatic
- [ ] Evil_Nymph
- [ ] Evil_Shadow_1
- [ ] Evil_Shadow_2
- [ ] Evil_Shadow_3
- [ ] Evil_Snake_Lord
- [ ] Excavator_Robot
- [ ] Executioner
- [ ] Exploration_Rover
- [ ] Explosion
- [ ] Ezella
- [ ] Faceworm
- [ ] Faceworm_(Dark)
- [ ] Faceworm_Queen
- [ ] Faithful_Manager
- [ ] Fallen_Bishop
- [ ] False_Angel
- [ ] Familiar
- [ ] Fanat
- [ ] Fei_Kanabian
- [ ] Felock
- [ ] Fenrir
- [ ] Ferus_(Green)
- [ ] Ferus_(Red)
- [ ] Fire_Condor
- [ ] Fire_Frilldora
- [ ] Fire_Golem
- [ ] Fire_Sandman
- [ ] Firelock_Soldier
- [ ] Flame_Skull
- [ ] Flora
- [ ] Freezer
- [ ] Frilldora
- [ ] Frozenwolf
- [ ] Frus
- [ ] Fulbuk
- [ ] GC109
- [ ] Gajomart
- [ ] Galapago
- [ ] Galion
- [ ] Galion_(Alternate)
- [ ] Garden_Keeper
- [ ] Garden_Watcher
- [ ] Gargoyle
- [ ] Gargoyle_(Alternate)
- [ ] Gazeti
- [ ] Geffen_Mage_01
- [ ] Geffen_Mage_02
- [ ] Geffen_Mage_03
- [ ] Geffen_Mage_04
- [ ] Geffen_Mage_05
- [ ] Geffen_Mage_06
- [ ] Geffen_Mage_07
- [ ] Geffen_Mage_08
- [ ] Geffen_Mage_09
- [ ] Geffen_Mage_10
- [ ] Geffen_Mage_11
- [ ] Geffen_Mage_12
- [ ] Geffen_Mage_13
- [ ] Geffen_Mage_14
- [ ] Gemini-S58
- [ ] Geographer
- [ ] Ghostring
- [ ] Ghoul
- [ ] Giant_Hornet
- [ ] Giant_Octopus
- [ ] Giant_Spider
- [ ] Gibbet
- [ ] Giearth
- [ ] Gig
- [ ] Gigan_(L)
- [ ] Gigan_(M)
- [ ] Gioia
- [ ] Gloom_Under_Night
- [ ] Goat
- [ ] Goblin_(Axe)
- [ ] Goblin_(Dagger)
- [ ] Goblin_(Flail)
- [ ] Goblin_(Hammer)
- [ ] Goblin_(Mace)
- [ ] Goblin_Archer
- [ ] Goblin_Leader
- [ ] Goblin_Steamrider
- [ ] Gold_Antler_Scaraba
- [ ] Gold_Horn_Scaraba
- [ ] Gold_One-Horn_Scaraba
- [ ] Gold_Poring
- [ ] Gold_Queen_Scaraba
- [ ] Gold_Rake_Horn_Scaraba
- [ ] Gold_Scaraba_Eggs
- [ ] Golden_Savage
- [ ] Golden_Thiefbug
- [ ] Golem
- [ ] Gopinch
- [ ] Grand_Peco
- [ ] Grand_Pere
- [ ] Greatest_General
- [ ] Green_Maiden
- [ ] Gremlin
- [ ] Grim_Reaper_Ankou
- [ ] Grizzly
- [ ] Grove
- [ ] Gryphon
- [ ] Gullinbursti
- [ ] Hardrock_Mammoth
- [ ] Harpy
- [ ] Hatii
- [ ] Hatii_(Baby)
- [ ] Headless_Mule
- [ ] Headless_Mule_(Alternate)
- [ ] Heart_Hunter
- [ ] Heater
- [ ] Heavy_Metaling
- [ ] Heirozoist
- [ ] Hell_Apocalypse
- [ ] Hell_Fly
- [ ] Hellhound
- [ ] Hermit_Plant
- [ ] Heydrich
- [ ] High_Orc
- [ ] Hill_Wind
- [ ] Hill_Wind_(Spear)
- [ ] Hillsrion
- [ ] Hode
- [ ] Hodremlin
- [ ] Holden
- [ ] Horn
- [ ] Horn_Scaraba
- [ ] Hornet
- [ ] Horong
- [ ] Hunter_Fly
- [ ] Hydra
- [ ] Hydrolancer
- [ ] Iara
- [ ] Ice_Titan
- [ ] Icicle
- [ ] Ifrit
- [ ] Immortal_Corpse
- [ ] Imp
- [ ] Incarnation_of_Morroc_(Angel)
- [ ] Incarnation_of_Morroc_(Golem)
- [ ] Incarnation_of_Morroc_(Human)
- [ ] Incarnation_of_Morroc_(Spirit)
- [ ] Incubus
- [ ] Injustice
- [ ] Irene_Elder
- [ ] Iron_Fist
- [ ] Isilla
- [ ] Isis
- [ ] Jaguar
- [ ] Jakk
- [ ] Jakk_(With_Santa_Hat)
- [ ] Jakk_(Without_Santa_Hat)
- [ ] Jejeling
- [ ] Jing_Guai
- [ ] Jitterbug
- [ ] Joker
- [ ] Kades
- [ ] Kaho
- [ ] Kapha
- [ ] Karakasa
- [ ] Kasa
- [ ] Kick_Step
- [ ] Kick_and_Kick
- [ ] Kiel
- [ ] Killer_Mantis
- [ ] King_Kray
- [ ] King_Poring
- [ ] Knocker
- [ ] Kobold
- [ ] Kobold_Archer
- [ ] Kobold_Leader
- [ ] Kraben
- [ ] Kraken
- [ ] Kraken_Tentacle
- [ ] Ktullanux
- [ ] Kublin
- [ ] Kukre
- [ ] Kuluna
- [ ] Lady_Solace
- [ ] Lady_Tanee
- [ ] Lamp_Ray
- [ ] Lava_Golem
- [ ] Leaf_Cat
- [ ] Leak
- [ ] Leib_Olmai
- [ ] Leopard_(Baby)
- [ ] Les
- [ ] Lichtern
- [ ] Little_Fatum
- [ ] Loki
- [ ] Loli_Ruri
- [ ] Lora
- [ ] Lord_of_Death
- [ ] Lost_Dragon
- [ ] Luciola_Vespa
- [ ] Lude
- [ ] Lune
- [ ] Maero_of_Thanatos
- [ ] Magic_Seal
- [ ] Magmaring
- [ ] Magnolia
- [ ] Majoruros
- [ ] Mallina
- [ ] Manananggal
- [ ] Mandragora
- [ ] Mangkukulam
- [ ] Mantis
- [ ] Mao_Guai
- [ ] Marc
- [ ] Marduk
- [ ] Marin
- [ ] Marina
- [ ] Marine_Sphere
- [ ] Marionette
- [ ] Marse
- [ ] Martin
- [ ] Matyr
- [ ] Mavka
- [ ] Maya_(Purple)
- [ ] Megalith
- [ ] Megalodon
- [ ] Memory_of_Thanatos
- [ ] Menblatt
- [ ] Merman
- [ ] Metal_Dragon
- [ ] Metaling
- [ ] Metaller
- [ ] Mi_Gao
- [ ] Mime_Monkey
- [ ] Mimic
- [ ] Miming
- [ ] Mineral
- [ ] Mini_Demon
- [ ] Minorous
- [ ] Mistress
- [ ] Mistress_of_Shelter
- [ ] Miyabi
- [ ] Mobster
- [ ] Monemus
- [ ] Morin
- [ ] Morroc_(Adult)
- [ ] Morroc_(Boy)
- [ ] Muka
- [ ] Mummy
- [ ] Munak
- [ ] Muscipular
- [ ] Muspellskoll
- [ ] Mutant_Dragonoid
- [ ] Mutant_Dragonoid_(Alternate)
- [ ] Myst
- [ ] Myst_Case
- [ ] Mysteltainn
- [ ] Mythlit
- [ ] Naga
- [ ] Naght_Sieger
- [ ] Nasarin
- [ ] Necromancer
- [ ] Neo_Punk
- [ ] Nepenthes
- [ ] Nereid
- [ ] New_Years_Doll
- [ ] Nidhogger_Shadow
- [ ] Nightmare
- [ ] Nightmare_Amon_Ra
- [ ] Nightmare_Ancient_Mummy
- [ ] Nightmare_Arclouze
- [ ] Nightmare_Mimic
- [ ] Nightmare_Minorous
- [ ] Nightmare_Terror
- [ ] Nightmare_Verit
- [ ] Nine_Tail
- [ ] Novus_(Red)
- [ ] Novus_(Yellow)
- [ ] Noxious
- [ ] Obeaune
- [ ] Obsidian
- [ ] Octopot
- [ ] Octopus
- [ ] Odium_of_Thanatos
- [ ] Ogretooth
- [ ] Orc_Archer
- [ ] Orc_Baby
- [ ] Orc_Hero
- [ ] Orc_Lady
- [ ] Orc_Lord
- [ ] Orc_Santa
- [ ] Orc_Skeleton
- [ ] Orc_Warrior
- [ ] Orc_Zombie
- [ ] Osiris
- [ ] Owl_Baron
- [ ] Owl_Duke
- [ ] Owl_Marquess
- [ ] Owl_Viscount
- [ ] Panzer_Goblin
- [ ] Parasite
- [ ] Parus
- [ ] Pasana
- [ ] Payon_Soldier
- [ ] Payon_Soldier_(Alternate)
- [ ] Peco_Peco
- [ ] Penomena
- [ ] Pere
- [ ] Permeter
- [ ] Pest
- [ ] Petal
- [ ] Petite_(Ground)
- [ ] Petite_(Sky)
- [ ] Pharaoh
- [ ] Phen
- [ ] Phendark
- [ ] Photon_Cannon
- [ ] Phreeoni
- [ ] Phylla
- [ ] Piamette
- [ ] Picky
- [ ] Piere
- [ ] Pinguicula
- [ ] Piranha
- [ ] Pirate_Skeleton
- [ ] Pitman
- [ ] Plankton
- [ ] Plant_(Blue)
- [ ] Plant_(Green)
- [ ] Plant_(Red)
- [ ] Plant_(White)
- [ ] Plant_(Yellow)
- [ ] Plasma
- [ ] Poison_Spore
- [ ] Poisonous_Toad
- [ ] Pom_Spider
- [ ] Pope_(Casual)
- [ ] Pope_(Normal)
- [ ] Pope_Bishop
- [ ] Pope_Guard
- [ ] Pope_Luwmin
- [ ] Porcellio
- [ ] Poring_Santa_Poring_Angeling
- [ ] Pouring
- [ ] Punk
- [ ] Pupa
- [ ] Pyuriel
- [ ] Queen_Scaraba
- [ ] Quve
- [ ] RSX_0806
- [ ] RSX_Event
- [ ] Rafflesia
- [ ] Rafflesia_Arnoldi
- [ ] Ragged_Zombie
- [ ] Raggler
- [ ] Rake_Horn_Scaraba
- [ ] Raptice
- [ ] Rata
- [ ] Raydric
- [ ] Raydric_Archer
- [ ] Recon_Robot
- [ ] Red_Eruma
- [ ] Red_Mushroom
- [ ] Remover
- [ ] Repair_Robot
- [ ] Rhyncho
- [ ] Rice_Cake
- [ ] Rideword
- [ ] Rock_Step
- [ ] Rocker
- [ ] Roda_Frog
- [ ] Rotar_Zairo
- [ ] Roween
- [ ] Rubylit
- [ ] Rudo
- [ ] Rybio
- [ ] SCR_MT_Robot
- [ ] Sageworm
- [ ] Salamander
- [ ] Samurai_Specter
- [ ] Sandman
- [ ] Sapphilit
- [ ] Sarah
- [ ] Sasquatch
- [ ] Savage
- [ ] Savage_(Baby)
- [ ] Scorpion
- [ ] Sea_Otter
- [ ] Seal
- [ ] Seaweed
- [ ] Seeker
- [ ] Shellfish
- [ ] Shinobi
- [ ] Side_Winder
- [ ] Siorava
- [ ] Siroma
- [ ] Skeggiold_(Black)
- [ ] Skeggiold_(Blue)
- [ ] Skeleton_(Archer)
- [ ] Skeleton_(Sailor)
- [ ] Skeleton_(Soldier)
- [ ] Skeleton_(Weak)
- [ ] Skeleton_(Weak,_Soldier)
- [ ] Skeleton_General
- [ ] Skeleton_Prisoner
- [ ] Skeleton_Worker
- [ ] Skogul
- [ ] Sleeper
- [ ] Smokie
- [ ] Snowier
- [ ] Sohee
- [ ] Soheon
- [ ] Solider
- [ ] Spring_Rabbit_(Grey)
- [ ] Spring_Rabbit_(White)
- [ ] Squidgitte__Sedora
- [ ] Stainer
- [ ] Stalactic_Golem
- [ ] Standing_Soul
- [ ] Stapo
- [ ] Steel_Chonchon
- [ ] Stem_Worm
- [ ] Step
- [ ] Sting
- [ ] Stone_Shooter
- [ ] Stormy_Knight
- [ ] Strouf
- [ ] Succubus
- [ ] Swordfish
- [ ] Taffy
- [ ] Tamadora
- [ ] Tamruan
- [ ] Tao_Gunka
- [ ] Taoist_Hermit
- [ ] Tarou
- [ ] Tatacho
- [ ] Teddy_Bear
- [ ] Tendrilrion
- [ ] Tengu
- [ ] Thara_Frog
- [ ] The_Paper
- [ ] Thief_Bug
- [ ] Thief_Bug_(Female)
- [ ] Thief_Bug_(Male)
- [ ] Thief_Bug_Egg
- [ ] Thorn
- [ ] Tikbalang
- [ ] Time_Keeper
- [ ] Timeholder
- [ ] Tiyanak
- [ ] Toad
- [ ] Topalit
- [ ] Torturous_Redeemer
- [ ] Toucan
- [ ] Tower_Keeper
- [ ] Tri_Joint
- [ ] Tristan_III
- [ ] Turtle_General
- [ ] Undead_Knight_(Female)
- [ ] Undead_Knight_(Male)
- [ ] Ungoliant
- [ ] Uni-horn_Scaraba
- [ ] Uzhas
- [ ] Vadon
- [ ] Valkyrie
- [ ] Valkyrie_Randgris
- [ ] Vanberk
- [ ] Venatu
- [ ] Venatu_(Blue)
- [ ] Venatu_(Green)
- [ ] Venatu_(Orange)
- [ ] Venatu_(Red)
- [ ] Venemous
- [ ] Venom_Bug
- [ ] Verit
- [ ] Vesper
- [ ] Violent_Coelacanth
- [ ] Violy
- [ ] Vitata
- [ ] Wakwak
- [ ] Wanderer
- [ ] Waste_Stove
- [ ] Watcher
- [ ] Werewolf
- [ ] Whisper
- [ ] White_Lady
- [ ] Wild_Rider
- [ ] Wild_Rose
- [ ] Willow
- [ ] Wind_Ghost
- [ ] Wish_Maiden
- [ ] Wood_Goblin
- [ ] Wooden_Golem
- [ ] Woodie
- [ ] Wootan_Fighter
- [ ] Wootan_Shooter
- [ ] Wormtail
- [ ] Wounded_Morroc
- [ ] Wraith
- [ ] Wraith_(Dead)
- [ ] XM_Celine_Kimi
- [ ] XM_Cookie
- [ ] XM_Cruiser
- [ ] XM_Hylozoist
- [ ] XM_Lude
- [ ] XM_Marionette
- [ ] XM_Mystcase
- [ ] XM_Teddy_Bear
- [ ] XM_Tree
- [ ] Xmas_Smokie
- [ ] Yao_Jun
- [ ] Yoyo
- [ ] Zealotus
- [ ] Zenorc
- [ ] Zerom
- [ ] Zhu_Po_Long
- [ ] Zipper_Bear
- [ ] Zombie
- [ ] Zombie_Guard
- [ ] Zombie_Master
- [ ] Zombie_Prisoner
- [ ] Zombie_Slaughter
