import pygame
from constants import BLOCK_SIZE, CHUNK_HEIGHT

def render_text_with_outline(text, font, text_color, outline_color, outline_width=2):
    # Render the text in the main color.
    text_surface = font.render(text, True, text_color)
    # Create a new surface larger than the text surface to hold the outline.
    w, h = text_surface.get_size()
    outline_surface = pygame.Surface((w + 2*outline_width, h + 2*outline_width), pygame.SRCALPHA)
    
    # Blit the text multiple times in the outline color, offset by outline_width in every direction.
    for dx in range(-outline_width, outline_width+1):
        for dy in range(-outline_width, outline_width+1):
            # Only draw outline if offset is non-zero (avoids overdraw, though it's not a big deal)
            if dx != 0 or dy != 0:
                pos = (dx + outline_width, dy + outline_width)
                outline_surface.blit(font.render(text, True, outline_color), pos)
    
    # Blit the main text in the center.
    outline_surface.blit(text_surface, (outline_width, outline_width))
    return outline_surface

class Hud:
    def __init__(self, texture_atlas, atlas_items, position=(32, 32)):
        """
        :param texture_atlas: The atlas surface containing the item icons.
        :param atlas_items: A dict with keys under "item" for each ore.
        :param position: Top-left position where the HUD will be drawn.
        """
        self.texture_atlas = texture_atlas
        self.atlas_items = atlas_items

        # Initialize ore amounts to 0.
        self.amounts = {
            "coal": 0,
            "iron_ingot": 0,
            "copper_ingot": 0,
            "gold_ingot": 0,
            "redstone": 0,
            "lapis_lazuli": 0,
            "diamond": 0,
            "emerald": 0,
        }

        self.position = position
        self.icon_size = (64, 64)  # Size to draw each icon
        self.spacing = 15  # Space between items

        # Initialize a font (using the default font and size 24)
        self.font = pygame.font.Font(None, 64)
        self.icon_cache = {}
        for ore in self.amounts:
            if ore in self.atlas_items["item"]:
                icon_rect = pygame.Rect(self.atlas_items["item"][ore])
                icon = self.texture_atlas.subsurface(icon_rect)
                icon = pygame.transform.scale(icon, self.icon_size)
                self.icon_cache[ore] = icon

        self.amount_text_cache = {}
        self.pickaxe_y_cache = None
        self.pickaxe_indicator_surface = None
        self.fast_slow_cache = None
        self.fast_slow_surface = None

    def update_amounts(self, new_amounts):
        """
        Update the ore amounts.
        :param new_amounts: Dict with ore names as keys and integer amounts as values.
        """
        self.amounts.update(new_amounts)

    def draw(self, screen, pickaxe_y, fast_slow_active, fast_slow):
        """
        Draws the HUD: each ore icon with its amount and other indicators.
        """
        x, y = self.position

        for ore, amount in self.amounts.items():
            # Retrieve the icon rect from atlas_items["item"][ore]
            if ore in self.icon_cache:
                screen.blit(self.icon_cache[ore], (x, y))
            else:
                # In case the ore key is missing, skip drawing the icon
                continue

            text_surface = self.amount_text_cache.get(ore)
            if text_surface is None or text_surface[0] != amount:
                text = str(amount)
                text_surface = (amount, render_text_with_outline(text, self.font, (255, 255, 255), (0, 0, 0), outline_width=2))
                self.amount_text_cache[ore] = text_surface
            
            # Position text to the right of the icon
            text_x = x + self.icon_size[0] + self.spacing
            text_y = y + (self.icon_size[1] - text_surface[1].get_height()) // 2 + 3
            screen.blit(text_surface[1], (text_x, text_y))

            # Move to the next line
            y += self.icon_size[1] + self.spacing

        # Draw the pickaxe position indicator with outlined text
        pickaxe_y_display = -int(pickaxe_y // BLOCK_SIZE)
        if self.pickaxe_y_cache != pickaxe_y_display:
            pickaxe_indicator_text = f"Y: {pickaxe_y_display}"
            self.pickaxe_indicator_surface = render_text_with_outline(pickaxe_indicator_text, self.font, (255, 255, 255), (0, 0, 0), outline_width=2)
            self.pickaxe_y_cache = pickaxe_y_display
        pickaxe_indicator_x = x + self.spacing
        pickaxe_indicator_y = y + self.spacing
        screen.blit(self.pickaxe_indicator_surface, (pickaxe_indicator_x, pickaxe_indicator_y))

        # Draw the fast/slow indicator with outlined text
        fast_slow_text = f"{fast_slow}" if fast_slow_active else "Normal"
        if self.fast_slow_cache != fast_slow_text:
            self.fast_slow_surface = render_text_with_outline(fast_slow_text, self.font, (255, 255, 255), (0, 0, 0), outline_width=2)
            self.fast_slow_cache = fast_slow_text
        fast_slow_x = x + self.spacing
        fast_slow_y = y + 2 * self.spacing + self.fast_slow_surface.get_height()
        screen.blit(self.fast_slow_surface, (fast_slow_x, fast_slow_y))

            

