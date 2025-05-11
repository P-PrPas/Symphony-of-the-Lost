# Symphony-of-the-Lost

## Project Overview
In the world of Harmonia, music is the essence of life. It is magic, 
weaponry, and the very force that binds existence together. However, one 
fateful night, the note "Sol" vanished from the grand symphony of the 
universe. Silence crept over the land, breaking apart its harmony, and the 
Maestros of Discord awakened. Once great musicians, these entities have 
succumbed to the abyss of nothingness, and now they seek to plunge the 
world into eternal silence. 

You are Melodia, The Last Virtuoso, the sole musician left with the ability to 
wield the sacred power of sound. Your journey will take you through the 
Seven Continents of Music, where you must reclaim the lost note, battle the 
Maestros, and restore the symphony that once sustained the world. 

Game Genre: Action RPG where players use musical notes 
as weapons and musical symbols as buffs/debuffs, incorporating strategic 
combat mechanics to defeat the forces of silence.

Youtube: https://youtu.be/72rU22wb9UU

## Project Review
I have inspired by Octopath Traveler – I like that this game has a strong and interesting storyline, which inspired me to make a story-based game.

## OOP Design

### Scene System
- BaseScene – Base class for all scenes, providing shared structure and logic
- MenuScene – The game's main menu scene
- GameScene – The main gameplay scene
- PauseScene – The pause menu scene
- GameOverScene – The scene shown when the player is defeated
- SettingScene – The settings/configuration screen
- SceneManager – Controls scene switching and runs the current scene
### Player & Combat
- Player – Controls player movement, dashing, skill casting, combos, EXP, and death
- ComboTracker – Tracks input notes to detect combos
- ComboEffectManager – Manages and renders combo visual effects
- SkillEffectManager – Handles skill effects, projectiles, healing, damage numbers
- SkillEffect / Projectile / CrescendoEffect / SoundquakeEffect / HealEffect / ImpactEffect – Various skill-related visual and logic effect
- SkillData – Data class defining the properties of a skill
- NoteType – Enum defining musical note types (WHOLE, HALF, QUARTER, EIGHTH)
### Enemy
- Enemy – Represents a single enemy with HP, AI movement, attack, animations, and death logic
- EnemyManager – Manages multiple enemies: spawning, updating, rendering
- EnemyHPBar – Renders HP bars above enemies
- ENEMY_PROFILES – Dictionary storing stats and animation configs per enemy type
### Map System
- Map – Loads and manages game maps: background image, NPCs, enemy data, transitions
- MAP_PROFILES – Dictionary defining layout, transitions, and enemy/NPC data per map
- CollisionHandler (from collisions.py) – Detects and manages collisions between player, enemies, and the map
### NPC & Dialog
- NPC – Non-player characters that display dialogue, animate, and interact with the player
- NPC_PROFILES – Stores NPC data and dialogue lines for each map
### UI 
- SymphonicHealthBar – Stylized HP bar with visual feedback and particle effects
- SymphonicStaminaBar – Stylized stamina bar with musical-themed particles
- FloatingNote – Floating musical notes used in health/stamina bar visuals
- BoxAura – Animated light trails around UI boxes
- FloatingDamageText – Floating text displaying damage dealt
### Utility Systems
- KeyPressManager – Detects new key presses and held keys
- SettingsManager – Loads and saves runtime settings
- StaminaSystem – Manages stamina, regeneration, and dash cost logic

Total Classes: 38

UML : I couldn't make it in time.😭
Statistical Data (Prop Stats) : I couldn't make it in time.😭
