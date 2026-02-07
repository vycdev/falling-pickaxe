import pygame
import random

class ExplosionParticle:
    def __init__(self, pos, texture_atlas, atlas_items, frame_count=16, frame_duration=1):
        """
        :param pos: Starting position (tuple or pygame.Vector2)
        :param texture_atlas: The atlas surface containing the explosion frames.
        :param atlas_items: A dict with keys like "explosion_0", "explosion_1", ... up to frame_count-1.
        :param frame_count: Total number of explosion frames.
        :param animation_duration: Total duration of the animation. Interpreted either in ms or frames.
        :param duration_mode: Either 'ms' for milliseconds or 'frames' for game frames.
        """
        self.pos = pygame.Vector2(pos)
        self.texture_atlas = texture_atlas
        self.atlas_items = atlas_items
        self.frame_count = frame_count

        self.elapsed_time = 0.0
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.finished = False

        # Random rotation between 0 and 360 degrees.
        self.rotation = random.uniform(0, 360)
        self.frames = []
        for i in range(self.frame_count):
            key = f"explosion_{i}"
            rect = pygame.Rect(self.atlas_items["particle"][key])
            texture = self.texture_atlas.subsurface(rect)
            texture = pygame.transform.rotate(texture, self.rotation)
            self.frames.append(texture)

    def update(self, dt_ms):
        """Update animation frame based on elapsed time or frame count."""
        if self.finished:
            return

        self.elapsed_time += dt_ms
        if self.elapsed_time >= self.frame_duration:
            self.elapsed_time -= self.frame_duration
            self.current_frame += 1

            if self.current_frame >= self.frame_count:
                self.finished = True
                self.current_frame = self.frame_count - 1


    def draw(self, screen, camera):
        if self.finished:
            return
        
        # Adjust drawing position by camera offset (if only vertical, subtract camera.offset_y)
        draw_pos = (self.pos.x - camera.offset_x, self.pos.y - camera.offset_y)

        screen.blit(self.frames[self.current_frame], draw_pos)

class Explosion:
    def __init__(self, pos, texture_atlas, atlas_items, particle_count=20):
        """
        Creates an explosion effect at the given position.
        :param pos: The center position of the explosion.
        :param texture_atlas: The atlas surface.
        :param atlas_items: The atlas items dictionary.
        :param particle_count: Number of particles to spawn.
        """
        self.particles = []
        for _ in range(particle_count):
            # Give each particle a slight random offset around the explosion center
            offset = pygame.Vector2(random.randint(-200, 200), random.randint(-200, 200))
            particle = ExplosionParticle(pos + offset, texture_atlas, atlas_items)
            self.particles.append(particle)

    def update(self, dt_ms):
        for particle in self.particles:
            particle.update(dt_ms)

        # Optionally remove finished particles
        self.particles = [p for p in self.particles if not p.finished]

    def draw(self, screen, camera):
        for particle in self.particles:
            particle.draw(screen, camera)
