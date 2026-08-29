# Boss 04 - Match3

Things added:

 - Move tiles by dragging them with the mouse, not by clicking them
 - Only allow moves that start a match
 - Restart board if no valid match is possible
 - Spawn a move hint with highlight after some seconds of not doing nothing, to avoid getting stuck
 - MiniBomb tiles, generated from a match with exactly four tiles. When played it also plays the tiles on it sides
 - Bomb tiles, generated from a match with more than four tiles. When played it also plays all the tiles with the same color on the board
	- Matches that plays any bomb won't generate more bombs

Minor Changes from base game

 - Reduce the amount of colors for tiles, 18 are too much for the "Only allow moves that start a match" rule, because almost every move will restart the board and spawning bombs is really hard. Reduced to 6, the number increments with each level you complete.
 - Gave a new purpose to the varieties of tiles, instead of being random, they're used for indetifying the bombs, the unused ones can be used for future kinds of tiles

[Base game](https://github.com/R3mmurd/VideoGameProgrammingI/tree/main/04-match3)
