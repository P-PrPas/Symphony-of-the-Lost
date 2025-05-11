# Symphony-of-the-Lost

## How to setup
Most importantly, you should have pygame installed. If you have pygame installed, simply execute the main.py file to play the game.
- pygame: python -m pip install pygame

## How to Play
- Movement: Use arrow key to movement
- Dash: Press shift to dash
- Actions: In this game you'll have four action to use base on music note such as Whole Note, Half Note, Quarter Note and Eight Note
  - Whole Note (Soundquake): Press A to use --> Players generates a circular sound wave around itself, dealing damage and inflicting a stun. Soundquake can be held down to enhance its radius and damage
  - Half Note (Sound Barrier): Press S to use --> Players can build a sound shield that surrounds them in a circle, lowering damage by 10%
  - Quarter Note (Strike Beat): Press D to use --> Players use notes to generate power and strike foes at close range (Melee Attack)
  - Eight Note (Note Flurry): Press F to use --> Players rapidly unleash sound energy as a missile (Range Attack)
 
- Combo: In music theory, each note has its own weight, such as the whole note (4 tone), half note (2 tone), quarter note (1 tone), and eighth note (0.5 tone). In this game, if you can combine attack patterns to get four tones, you will develop an ability. For example, pressing Half Note twice in a row: 2+2=4. Alternatively, pressing Half 1, Quarter 1, and Eight 2 will result in 2+1+0.5+0.5=4, which will produce another ability. However, if the player pushes more than four tones, the combo is deemed unsuccessful and must be redone

- Currently, we can only create two combinations, which is really unsatisfactory. Sorry about that. The current combo consists of 2 items: Heal [S][S] and Crescendo [S][D][F][F].
- Heal: Press S twice in a row to heal wounds.
- Crescendo: Press S D F F to buff attack power.

- Setting: For settings, adjusting the volume is available immediately, but toggling the hitboxes on and off requires a new game run.


