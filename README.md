# Symphony-of-the-Lost

## How to setup
Most importantly, you should have pygame installed. If you have pygame installed, simply execute the main.py file to play the game.

## Procession

### Phase 1: Core Mechanics (~65%)
- Movement ✅
- Four Note Action ✅
- Map Transition Systems ✅
- Collisions System ✅
- Combo UI ✅
- Animation ❌
- NPC ❌
- Quest ❌

### Phase2: Skill System (~30%)
- Skill Database Structure ✅
- Connect Skill Database to Player ✅
- Trigger Skill ❌
- Skill Animation ❌

### Phase3: Combat System (~10%)
- Enemy Profile ✅
- Hitbox ✅
- Take Damage System ❌
- Attack System ❌

### Phase4: Polishing & VFX (~30%)
- Decorate Combo Bar ✅
- Decorate HP and Stamina Bar ✅
- SFX ❌
- Menu ❌
- Setting ❌

### Phase5: Assets Preparing (0%)
- 😭

## How to Play
- Movement: Use arrow key to movement
- Dash: Press shift to dash
- Actions: In this game you'll have four action to use base on music note such as Whole Note, Half Note, Quarter Note and Eight Note
  - Whole Note (Soundquake): Press A to use --> Players generates a circular sound wave around itself, dealing damage and inflicting a stun. Soundquake can be held down to enhance its radius and damage
  - Half Note (Sound Barrier): Press S to use --> Players can build a sound shield that surrounds them in a circle, lowering damage by 10%
  - Quarter Note (Strike Beat): Press D to use --> Players use notes to generate power and strike foes at close range (Melee Attack)
  - Eight Note (Note Flurry): Press F to use --> Players rapidly unleash sound energy as a missile (Range Attack)
 
- Combo: In music theory, each note has its own weight, such as the whole note (4 tone), half note (2 tone), quarter note (1 tone), and eighth note (0.5 tone). In this game, if you can combine attack patterns to get four tones, you will develop an ability. For example, pressing Half Note twice in a row: 2+2=4. Alternatively, pressing Half 1, Quarter 1, and Eight 2 will result in 2+1+0.5+0.5=4, which will produce another ability. However, if the player pushes more than four tones, the combo is deemed unsuccessful and must be redone

However, as previously said, our Combo system is not yet finalized. We can now display the notes, but there are still many elements to work on (the strike beat animation is still experiencing issues), so you may not be able to view the entire image. We apologize about that

Finally, we have a cute little slime on the left. Everyone can walk over to see it, but you can't kill it yet because the combat system isn't finished yet😿


