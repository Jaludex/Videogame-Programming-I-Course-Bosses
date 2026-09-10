# Boss 05 - Princess

Things added:

 - Probability of spawning a chest in a room, the chest contains any player_item definition
 - Bow obtainable via a player_item, shoots arrows with cooldown (fire with "x")
 - Animation for firing the bow
 - Pause State (with "p")
 - Dragon Boss
    - After getting the bow, there's a chanche of entering the boss room
    - Collision with his body damages you by 2 points
    - Shoots fireball towards you, they instakill you
    - Moves his head around
    - Invulnerable until you shot an arrow to his head, then becomes weak for you to use your sword


Minor Changes from base game

 - Max travel for projectiles changed from 4 to 6 tiles
 - Make projectiles contain a sender attribute, in order to only ask collitions with their enemies

[Base game](https://github.com/R3mmurd/VideoGameProgrammingI/tree/main/06-princess)
