import pygame
import random
from block import Block
from constants import BLOCK_SIZE, CHUNK_HEIGHT, CHUNK_WIDTH, SEED

def generate_noise_ranges(block_weights):
    """
    Generate noise value ranges based on block rarity weights.
    
    :param block_weights: Dict of block names and their rarity weights.
                          Higher values mean more common.
    :return: List of (block_name, min_value, max_value)
    """
    sorted_blocks = sorted(block_weights.items(), key=lambda x: x[1], reverse=True)  # Sort by weight
    total_weight = sum(block_weights.values())  # Get total weight
    min_noise = -1.0  # Start from minimum noise value
    noise_ranges = []

    for block, weight in sorted_blocks:
        range_size = (weight / total_weight) * 2.0  # Scale to noise range (-1 to 1)
        max_noise = min_noise + range_size
        noise_ranges.append((block, min_noise, max_noise))
        min_noise = max_noise  # Move to next range

    return noise_ranges


def get_block_for_noise(noise_value, noise_ranges):
    """
    Get the corresponding block based on a noise value.
    
    :param noise_value: The Perlin noise value (-1 to 1)
    :param noise_ranges: List of (block_name, min_value, max_value)
    :return: Block name corresponding to the noise value
    """
    for block, min_val, max_val in noise_ranges:
        if min_val <= noise_value < max_val:
            return block
    return "stone"  # Default fallback

block_weights = {
    "stone": 40,  
    "andesite": 30,
    "diorite": 10,
    "granite": 10,
    "coal_ore": 10,  
    "iron_ore": 8,
    "copper_ore": 8,  
    "gold_ore": 5,  
    "diamond_ore": 2,  
    "emerald_ore": 1,  
    "obsidian": 1,  
    "redstone_ore": 7,  
    "lapis_ore": 6,
    "mossy_cobblestone": 4,
    "cobblestone": 20
}

# Generate noise ranges
noise_ranges = generate_noise_ranges(block_weights)

def generate_first_chunk(texture_atlas, atlas_items, space): 
    chunk = []
    for y in range(CHUNK_HEIGHT):
        row = []
        for x in range(CHUNK_WIDTH):
            if(x == 0 or x == CHUNK_WIDTH - 1):
                block_x = (0 * CHUNK_WIDTH + x) * BLOCK_SIZE
                block_y = (0 * CHUNK_HEIGHT + y) * BLOCK_SIZE
                row.append(Block(space, block_x, block_y, "bedrock", texture_atlas, atlas_items))
                continue
            elif y == 0:
                block_x = (0 * CHUNK_WIDTH + x) * BLOCK_SIZE
                block_y = (0 * CHUNK_HEIGHT + y) * BLOCK_SIZE
                row.append(Block(space, block_x, block_y, "bedrock", texture_atlas, atlas_items))
                continue
            elif y == CHUNK_HEIGHT - 2:
                block_x = (0 * CHUNK_WIDTH + x) * BLOCK_SIZE
                block_y = (0 * CHUNK_HEIGHT + y) * BLOCK_SIZE
                row.append(Block(space, block_x, block_y, "grass_block", texture_atlas, atlas_items))
                continue
            elif y == CHUNK_HEIGHT - 1:
                block_x = (0 * CHUNK_WIDTH + x) * BLOCK_SIZE
                block_y = (0 * CHUNK_HEIGHT + y) * BLOCK_SIZE
                row.append(Block(space, block_x, block_y, "dirt", texture_atlas, atlas_items))
                continue
            row.append(None)
        chunk.append(row)
    return chunk

def generate_side_chunk(chunk_x, chunk_y, texture_atlas, atlas_items, space):
    chunk = []
    for y in range(CHUNK_HEIGHT):
        row = []
        for x in range(CHUNK_WIDTH):
            block_x = (chunk_x * CHUNK_WIDTH + x) * BLOCK_SIZE
            block_y = (chunk_y * CHUNK_HEIGHT + y) * BLOCK_SIZE
            row.append(Block(space, block_x, block_y, "bedrock", texture_atlas, atlas_items))
        chunk.append(row)
    return chunk

# Function to generate chunks using Perlin noise
def generate_chunk(chunk_x, chunk_y, texture_atlas, atlas_items, space):
    if(chunk_y <= 0):
        return generate_first_chunk(texture_atlas, atlas_items, space)

    chunk = []
    for y in range(CHUNK_HEIGHT):
        row = []
        for x in range(CHUNK_WIDTH):
            block_x = (0 * CHUNK_WIDTH + x) * BLOCK_SIZE
            block_y = (chunk_y * CHUNK_HEIGHT + y) * BLOCK_SIZE

            if(x == 0 or x == CHUNK_WIDTH - 1):
                row.append(Block(space, block_x, block_y, "bedrock", texture_atlas, atlas_items))
                continue

            noise_value = random.uniform(-1, 1)

            # Block selection based on noise val
            row.append(Block(space, block_x, block_y, get_block_for_noise(noise_value, noise_ranges), texture_atlas, atlas_items))

        chunk.append(row)
    return chunk

# Store generated chunks
chunks = {}

def _remove_block_from_space(block, space):
    if block is None or space is None:
        return
    try:
        if block.body in space.bodies or block.shape in space.shapes:
            space.remove(block.body, block.shape)
    except Exception:
        pass

def get_block(chunk_x, chunk_y, x, y, texture_atlas, atlas_items, space):
    if chunk_y < 0:
        return None

    if (chunk_x, chunk_y) not in chunks:
        if(chunk_x == 0):
            chunks[(chunk_x, chunk_y)] = generate_chunk(chunk_x, chunk_y, texture_atlas, atlas_items, space)
        else:
            chunks[(chunk_x, chunk_y)] = generate_side_chunk(chunk_x, chunk_y, texture_atlas, atlas_items, space)
            
    return chunks[(chunk_x, chunk_y)][y][x]

def delete_block(chunk_x, chunk_y, x, y, space=None):
    if (chunk_x, chunk_y) in chunks:
        block = chunks[(chunk_x, chunk_y)][y][x]
        if block is not None:
            block.hp = 0
            _remove_block_from_space(block, space)
        del chunks[(chunk_x, chunk_y)][y][x]
        chunks[(chunk_x, chunk_y)][y][x] = None

def clean_chunks(start_chunk_y, space):
    for (chunk_x, chunk_y) in list(chunks.keys()):
        if chunk_y < start_chunk_y:
            chunk = chunks[(chunk_x, chunk_y)]
            for row in chunk:
                for block in row:
                    _remove_block_from_space(block, space)
            del chunks[(chunk_x, chunk_y)]
