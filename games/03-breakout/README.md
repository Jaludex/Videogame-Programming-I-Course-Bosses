# Boss 03 - Breakout

Things added:

 - Three new Power Ups, all with sounds and time bars
	 - Bazooka: Spawns bazookas on the paddle's sides, fire with "f", explodes on contact to brick damaging a up to a 3x3 area above the explosion position. Can't fire new rockets if the previus pair hasn't dissapeared yet. Last 8 seconds.
	 - Sticky Paddle: For the duration of the power up, balls sitck to the paddle, press "enter" to re-serve them all at once. Last 10 seconds, after that, it auto-serves all the sticked balls.
	 - Safety Net: For the duration of the power up, there's a barrier below your paddle stopping balls from dissapearing by bouncing them, in practical terms, a long and static paddle. Last 6 seconds.

Minor Fixes

 - Add victory condition for when there are no more bricks. Originally it stops when theres one and is broken in order to not wait his particles, but when several bricks are broken (With a rocket), it jumps to zero bricks, skipping the earlier victory condition. With both works perfectly.
 - Fix issue #1 from base game repo

[Base game](https://github.com/R3mmurd/VideoGameProgrammingI/tree/main/03-breakout)
