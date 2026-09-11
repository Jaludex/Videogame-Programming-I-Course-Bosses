import math
import pygame
from gale.physics.shapes import CircleShape
from gale.physics.world import World
import settings
from src.definitions.entity import BIRD, density_for_circle

class Bird:
    def __init__(self, world: World, x: float, y: float) -> None:
        self.radius: float = BIRD["radius"]
        self.mass: float = BIRD["mass"]

        density = density_for_circle(self.mass, self.radius)
        self.body = world.create_dynamic_body(
            x,
            y,
            CircleShape(
                radius=self.radius,
                density=density,
                friction=BIRD["friction"],
                restitution=BIRD["restitution"],
            ),
        )
        self.body.set_damping(BIRD["linear_damping"], BIRD["angular_damping"])
        self.body.user_data = self

        self.initial_position = pygame.Vector2(x, y)
        self.image = settings.TEXTURES[BIRD["sprite"]]
        
        self.has_collided = False

    @property
    def position(self) -> pygame.Vector2:
        return self.body.position

    def reset(self) -> None:
        self.body.position = self.initial_position
        self.body.angle = 0.0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0.0
        self.has_collided = False

    def split(self, world: World):
        bird_speed = pygame.Vector2(self.body.velocity.x, self.body.velocity.y)

        bird_1_speed = bird_speed.rotate(settings.EXTRA_BIRDS_SEPARATION)
        bird_2_speed = bird_speed.rotate(-settings.EXTRA_BIRDS_SEPARATION)

        bird_up = Bird(world, self.position.x, self.position.y)
        bird_up.body.velocity = (bird_1_speed.x, bird_1_speed.y)

        bird_down = Bird(world, self.position.x, self.position.y)
        bird_down.body.velocity = (bird_2_speed.x, bird_2_speed.y)

        return [bird_up, bird_down]

    def render(self, surface: pygame.Surface, camera) -> None:
        diameter = max(1, round(self.radius * 2 * camera.zoom))
        scaled = pygame.transform.smoothscale(self.image, (diameter, diameter))
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.body.angle))
        rect = rotated.get_rect(center=camera.world_to_screen(self.body.position))
        surface.blit(rotated, rect)
