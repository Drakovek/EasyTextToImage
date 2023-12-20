#!/usr/bin/env python3

import random
from PIL import ImageColor
from typing import List

def get_hue_in_range(hue:int) -> int:
    """
    Adds or subtracts to get a given hue value into the range of 0-359.
    
    :param hue: Hue value
    :type hue: int, required
    :return: Hue modified to fit in the standart hue range of 0-359
    :rtype: int
    """
    # Add if hue is below range
    modified_hue = hue
    while modified_hue < 0:
        modified_hue += 360
    # Subract if hue is above range
    while modified_hue > 359:
        modified_hue -= 360
    # Return the hue
    return modified_hue

def get_hue_offsets(hue:int, offset:int) -> List[int]:
    """
    Returns a list of hues, each separated by a different offset.
    
    :param hue: The first hue value of the list (0-359)
    :type hue: int, required
    :param offset: Amount of offset between hues
    :type offset: int, required
    :return: List of hue values
    :rtype: List[int]
    """
    hues = []
    for i in range(0, int(360/offset)):
        hues.append(get_hue_in_range(hue + (i * offset)))
    return hues

def rgb_to_hex_color(rgb:(int,int,int)) -> str:
    """
    Converts a tuple of RGB values into an RGBA hex color value.
    
    :param rgb: Tuple of (Red, Green, Blue) values
    :type rgb: (int, int, int)
    :return: Hex color in #RRGGBBAA format
    :rtype: str
    """
    # Get the hex values of each color
    red = hex(rgb[0])[2:].zfill(2).lower()
    green = hex(rgb[1])[2:].zfill(2).lower()
    blue = hex(rgb[2])[2:].zfill(2).lower()
    # Return the hex color
    return f"#{red}{green}{blue}ff"

def get_monochrome_palette(hue:int) -> dict:
    """
    Creates a monochrome color palette based on a single hue value.
    Returns #RRGGBBAA hex colors with light, dark, saturated, and desaturated varients.
    Dictionary contains keys "light-saturated", "dark-saturated", "light-desaturated", and "dark-desaturated"
    
    :param hue: Hue value used to generate the palette (0-359)
    :type hue: int, required
    :return: Dictionary containing hex colors for four color varients
    :rtype: dict
    """
    # Get the light saturated color
    palette = dict()
    palette["light-saturated"] = rgb_to_hex_color(ImageColor.getrgb(f"hsv({hue}, 80%, 90%)"))
    # Get the dark saturated color
    palette["dark-saturated"] = rgb_to_hex_color(ImageColor.getrgb(f"hsv({hue}, 80%, 30%)"))
    # Get the light desaturated color
    palette["light-desaturated"] = rgb_to_hex_color(ImageColor.getrgb(f"hsv({hue}, 20%, 100%)"))
    # Get the dark desaturated color
    palette["dark-desaturated"] = rgb_to_hex_color(ImageColor.getrgb(f"hsv({hue}, 50%, 20%)"))
    # Return the color palette
    return palette

def get_dual_hue_palette(dark_hue:int, light_hue:int) -> dict:
    """
    Creates a dual-hue color palette based on a light and a dark hue value.
    Returns #RRGGBBAA hex colors with light, dark, saturated, and desaturated varients.
    Dictionary contains keys "light-saturated", "dark-saturated", "light-desaturated", and "dark-desaturated"
    
    :param dark_hue: Hue value used for the dark saturated and desaturated colors (0-359)
    :type dark_hue: int, required
    :param light_hue: Hue value used for the light saturated and desaturated colors (0-359)
    :type light_hue: int, required
    :return: Dictionary containing hex colors for four color varients
    :rtype: dict
    """
    # Get monochrome palettes for both hues
    dark_palette = get_monochrome_palette(dark_hue)
    light_palette = get_monochrome_palette(light_hue)
    # Combine into one palette
    palette = dict()
    palette["light-saturated"] = light_palette["light-saturated"]
    palette["light-desaturated"] = light_palette["light-desaturated"]
    palette["dark-saturated"] = dark_palette["dark-saturated"]
    palette["dark-desaturated"] = dark_palette["dark-desaturated"]
    # Return the color palette
    return palette

def get_random_color_palette() -> dict:
    """
    Creates a random dual-hue color palette with saturated and desaturated colors.
    Returns #RRGGBBAA hex colors with primary and secondary colors, saturated, and desaturated varients.
    Dictionary contains keys "primary-saturated", "primary-desaturated", "secondary-saturated", and "secondary-desaturated"
    
    :return: Dictionary containing hex colors for four color varients
    :rtype: dict
    """
    # Randomly select a either a triadic or tetradic palette
    hue_offset = int(360/random.randint(3,4))
    # Generate hues based on a random starting value
    hues = get_hue_offsets(random.randint(0, 359), offset=hue_offset)[:2]
    hues = sorted(hues, reverse=(random.randint(0,1) == 1))
    # Create a dual hue palette from the randomly generated hues
    base_palette = get_dual_hue_palette(hues[0], hues[1])
    # Randomly choose whether dark or light hue should be the primary hue
    palette = dict()
    if random.randint(0,1) == 1:
        # Dark Primary
        palette["primary-saturated"] = base_palette["dark-saturated"]
        palette["primary-desaturated"] = base_palette["dark-desaturated"]
        palette["secondary-saturated"] = base_palette["light-saturated"]
        palette["secondary-desaturated"] = base_palette["light-desaturated"]
    else:
        # Light Primary
        palette["primary-saturated"] = base_palette["light-saturated"]
        palette["primary-desaturated"] = base_palette["light-desaturated"]
        palette["secondary-saturated"] = base_palette["dark-saturated"]
        palette["secondary-desaturated"] = base_palette["dark-desaturated"]
    # Return the palette
    return palette
    
