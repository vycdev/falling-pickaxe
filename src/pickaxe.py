import pygame
import math
import pymunk
import pymunk.autogeometry
from chunk import chunks
from constants import BLOCK_SIZE, CHUNK_WIDTH
import random

def rotate_point(x, y, angle):
    """Rotate a point (x, y) by angle (in radians) around the origin (0, 0)."""
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    new_x = cos_angle * x - sin_angle * y
    new_y = sin_angle * x + cos_angle * y
    return new_x, new_y

def rotate_vertices(vertices, angle):
        rotated_vertices = []

        for vertex in vertices:
            # Rotate each vertex based on the body's angle
            rotated_x, rotated_y = rotate_point(vertex[0] - BLOCK_SIZE / 2 , vertex[1] - BLOCK_SIZE / 2, angle)

            # Offset each rotated vertex by the body's position
            rotated_vertices.append((rotated_x, rotated_y))
        
        return rotated_vertices

class Pickaxe:
    def __init__(self, space, x, y, texture, sound_manager, damage=2, velocity=0, rotation=0, mass=100):
        self.texture = texture
        self.velocity = velocity
        self.rotation = rotation
        self.space = space
        self.damage = damage
        self.is_enlarged = False

        vertices = rotate_vertices([
                    (0, 0), # A
                    (10, 0), # C
                    (110, 100), # D
                    (100, 110), # E
                    (0, 10), # F
                    (110, 110), # G
                ], -math.pi / 2)
        
        vertices2 = rotate_vertices([
                    (110, 30), # H
                    (120, 40), # I
                    (120, 90), # J
                    (100, 90), # K
                    (100, 40), # L
                    (110, 100), # D
                ], -math.pi / 2)
        
        vertices3 = rotate_vertices([
                    (30, 110), # M
                    (40, 120), # N
                    (90, 120), # O
                    (40, 100), # P
                    (90, 100), # Q
                    (100, 110), # E
                ], -math.pi / 2)

        inertia = pymunk.moment_for_poly(mass, vertices)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = (x, y)
        self.body.angle = math.radians(rotation)

        self.sound_manager = sound_manager

        self.shapes = []
        for vertices in [vertices, vertices2, vertices3]:
            shape = pymunk.Poly(self.body, vertices)
            shape.elasticity = 0.7
            shape.friction = 0.7
            shape.collision_type = 1  # Identifier for collisions
            self.shapes.append(shape)

        self.space.add(self.body, *self.shapes)

        # Add collision handler for pickaxe & blocks
        handler = space.add_collision_handler(1, 2)  # (Pickaxe type, Block type)
        handler.post_solve = self.on_collision

    def on_collision(self, arbiter, space, data):
        """Handles collision with blocks: Reduce HP or destroy the block."""
        block_shape = arbiter.shapes[1]  # Get the block shape
        block = block_shape.block_ref  # Get the actual block instance

        block.first_hit_time = pygame.time.get_ticks()  
        block.last_heal_time = block.first_hit_time

        block.hp -= self.damage  # Reduce HP when hit

        if (block.name == "grass_block" or block.name == "dirt"):
            self.sound_manager.play_sound("grass" + str(random.randint(1, 4)))
        else:
            self.sound_manager.play_sound("stone" + str(random.randint(1, 4)))

        # Add small random rotation on hit
        self.body.angle += random.choice([0.01, -0.01])

    def random_pickaxe(self, texture_atlas, atlas_items): 
        """Randomly change the pickaxe's properties."""

        pickaxe_name = random.choice(list(atlas_items["pickaxe"].keys()))
        self.texture = texture_atlas.subsurface(atlas_items["pickaxe"][pickaxe_name])
        print("Setting pickaxe to:", pickaxe_name)

        if self.is_enlarged:
            # Scale up texture
            new_size = (BLOCK_SIZE * 3, BLOCK_SIZE * 3)
            self.texture = pygame.transform.scale(self.texture, new_size)

        if(pickaxe_name =="wooden_pickaxe"):  
            self.damage = 2
        elif(pickaxe_name =="stone_pickaxe"):
            self.damage = 4
        elif(pickaxe_name =="iron_pickaxe"):
            self.damage = 6
        elif(pickaxe_name =="golden_pickaxe"):
            self.damage = 8
        elif(pickaxe_name =="diamond_pickaxe"):
            self.damage = 10
        elif(pickaxe_name =="netherite_pickaxe"):
            self.damage = 12

    def pickaxe(self, name, texture_atlas, atlas_items):
        """Set the pickaxe's properties based on its name."""

        self.texture = texture_atlas.subsurface(atlas_items["pickaxe"][name])
        print("Setting pickaxe to:", name)

        if self.is_enlarged:
            # Scale up texture
            new_size = (BLOCK_SIZE * 3, BLOCK_SIZE * 3)
            self.texture = pygame.transform.scale(self.texture, new_size)

        if(name =="wooden_pickaxe"):  
            self.damage = 2
        elif(name =="stone_pickaxe"):
            self.damage = 4
        elif(name =="iron_pickaxe"):
            self.damage = 6
        elif(name =="golden_pickaxe"):
            self.damage = 8
        elif(name =="diamond_pickaxe"):
            self.damage = 10
        elif(name =="netherite_pickaxe"):
            self.damage = 12

    def update(self, current_time=None):
        """Apply gravity, update movement, check collisions, and rotate."""
        if current_time is None:
            current_time = pygame.time.get_ticks()
        # Manually limit the falling speed (terminal velocity)
        if self.body.velocity.y > 1000:
            self.body.velocity = (self.body.velocity.x, 1000)

        # --- Bounding box check for bedrock collision ---
        # Gather all vertices from all shapes, transformed to world coordinates
        all_vertices = []
        for shape in self.shapes:
            for v in shape.get_vertices():
                # Transform local vertex to world coordinates
                world_v = self.body.local_to_world(v)
                all_vertices.append(world_v)

        min_x = min(v.x for v in all_vertices)
        max_x = max(v.x for v in all_vertices)

        left_limit = BLOCK_SIZE
        right_limit = BLOCK_SIZE * (CHUNK_WIDTH - 1)

        # If any part is left of the left limit, shift the body right
        if min_x < left_limit:
            dx = left_limit - min_x
            self.body.position = (self.body.position.x + dx, self.body.position.y)

        # If any part is right of the right limit, shift the body left
        if max_x > right_limit:
            dx = max_x - right_limit
            self.body.position = (self.body.position.x - dx, self.body.position.y)

        # If pickaxe is enlarged, check if time is up
        if hasattr(self, "enlarge_end_time") and current_time > self.enlarge_end_time:
            self.reset_size()
            self.is_enlarged = False

    def draw(self, screen, camera):
        """Draw the pickaxe at its current position."""
        rotated_image = pygame.transform.rotate(self.texture, -math.degrees(self.body.angle))  # Convert to degrees
        rect = rotated_image.get_rect(center=(self.body.position.x, self.body.position.y))
        rect.y -= camera.offset_y
        rect.x -= camera.offset_x
        screen.blit(rotated_image, rect)

    def enlarge(self, duration=5000):
        """Temporarily makes the pickaxe 3 times bigger with a larger hitbox."""
        print("Enlarging pickaxe")

        # If already enlarged, just extend the duration.
        if hasattr(self, "is_enlarged") and self.is_enlarged:
            self.enlarge_end_time += duration
            return

        # Not enlarged yet, so store original texture and shapes
        self.original_texture = self.texture.copy()
        self.original_shapes = self.shapes[:]  # Store original hitbox shapes
        self.is_enlarged = True

        # Scale up texture using the original texture.
        new_size = (BLOCK_SIZE * 3, BLOCK_SIZE * 3)
        self.texture = pygame.transform.scale(self.original_texture, new_size)

        # Scale up hitbox:
        self.space.remove(*self.shapes)  # Remove current shapes
        new_shapes = []
        for shape in self.original_shapes:
            # Get vertices from original shape and scale them by 3.
            scaled_vertices = [(x * 3, y * 3) for x, y in shape.get_vertices()]
            new_shape = pymunk.Poly(self.body, scaled_vertices)
            new_shape.elasticity = shape.elasticity
            new_shape.friction = shape.friction
            new_shape.collision_type = shape.collision_type
            new_shapes.append(new_shape)
        self.shapes = new_shapes
        self.space.add(*self.shapes)  # Add new enlarged shapes

        # Track when the enlargement effect should end
        self.enlarge_end_time = pygame.time.get_ticks() + duration

    def reset_size(self):
        """Restore the pickaxe to its original size."""
        if hasattr(self, "original_shapes"):
            # Restore texture using the stored original.
            self.texture = self.original_texture.copy()

            # Reset hitbox: remove enlarged shapes and add back the original shapes.
            self.space.remove(*self.shapes)
            self.shapes = self.original_shapes[:]
            self.space.add(*self.shapes)
            self.is_enlarged = False

            del self.enlarge_end_time  # Remove the enlargement timer
