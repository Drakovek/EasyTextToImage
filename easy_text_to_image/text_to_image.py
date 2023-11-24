#!/usr/bin/env python3

import re
import math
import metadata_magic.file_tools as mm_file_tools
from PIL import Image, ImageColor, ImageDraw, ImageFont
from os.path import abspath, basename, exists, expandvars, join
from typing import List

def get_font_locations() -> List[str]:
    """
    Returns a list of directories on the system that contain fonts.
    
    :return: List of font directories on the system
    :rtype: List[str]
    """
    font_directories = []
    # Windows Directories
    font_directories.append("C:\\Windows\\Fonts\\")
    # Linux Directories
    font_directories.append("/usr/share/fonts/")
    font_directories.append("/usr/local/share/fonts/")
    font_directories.append("${HOME}/.local/share/fonts")
    # MacOS Directories
    font_directories.append("/Library/Fonts/")
    font_directories.append("/System/Library/Fonts/")
    font_directories.append("${HOME}/Library/Fonts")
    # Replace the environment variables
    existing_directories = []
    for font_directory in font_directories:
        # Check if the directory exists
        full_directory = abspath(expandvars(font_directory))
        if exists(full_directory):
            existing_directories.append(full_directory)
    # Return the font directories
    return existing_directories

def get_system_fonts() -> List[str]:
    """
    Returns a list of all the fonts installed on the system.
    
    :return: List of paths to fonts on the system
    :rtype: List[str]
    """
    # Get the system font locations
    font_locations = get_font_locations()
    # Get fonts from each directory
    fonts = []
    for location in font_locations:
        fonts.extend(mm_file_tools.find_files_of_type(location, [".ttf", ".otf", ".otc", ".ttc"]))
    # Return the list of fonts
    return fonts

def get_font(font_name:str, fonts:List[str]) -> ImageFont:
    """
    Returns a Pillow ImageFont object for a font with the given name.
    Returns None if no valid font was found
    
    :param font_name: Name of the font to search for, with no extension
    :type font_name: str, required
    :param fonts: List of paths to system fonts
    :type fonts: List[str]
    :return: Pillow ImageFont object
    :rtype: PIL.ImageFont
    """
    # Run through each font
    for font in fonts:
        system_font_name = re.sub(r"\..+$", "", basename(font))
        # See if the font exists
        if system_font_name == font_name:
            try:
                # Attempt to load the font
                image_font = ImageFont.truetype(font)
                # Return the font if valid
                return image_font
            except OSError: pass
    # Return None if the font could not be found
    return None

def get_basic_font(font_style:str, fonts:List[str]) -> ImageFont:
    """
    Returns a Pillow ImageFont object for a font of a given style.
    Returns a default font if no valid font was found.
    
    :param font_style: Style of the font to search for ("serif", "sans-serif", or "monospace")
    :type font_style: str, required
    :param fonts: List of paths to system fonts
    :type fonts: List[str]
    :return: Pillow ImageFont object
    :rtype: PIL.ImageFont
    """
    font_types = dict()
    font_types["serif"] = ["Garamond", "Georgia", "Baskerville", "Times", "FreeSerif", "DejaVuSerif"]
    font_types["sans-serif"] = ["Helvetica", "Arial", "Verdana", "Tahoma", "FreeSans", "DejaVuSans"]
    font_types["monospace"] = ["Courier", "Lucida", "Monaco", "FreeMono", "DejaVu Sans Mono"]
    # Try to get a font
    try:
        for font in font_types[font_style]:
            image_font = get_font(font, fonts)
            if image_font is not None:
                return image_font
    except KeyError: pass
    # Return the default font if no fonts were found
    return ImageFont.load_default()

def get_bounds(image:Image, color:str, foreground:bool=False) -> (int, int, int, int):
    """
    Returns a tuple with a bounding box of where a certain color or lack of color exists in an image.
    
    :param image: Image to search for the color within
    :type image: PIL.Image, required
    :param color: Foreground/Background color to search for/against
    :type color: str, required
    :param foreground: If true, searches for the color, otherwise searches for abscence of color, defaults to False
    :type foreground: bool, optional
    :return: Tuple of (left, top, right, bottom)
    :rtype: (int, int, int, int)
    """
    # Set the default bounds
    width, height = image.size
    left, right, top, bottom = (-1, -1, -1, -1)
    color_tuple = ImageColor.getrgb(color)
    # Get the leftmost part of the image that matches the color
    for left in range(0, width):
        for y in range(0, height):
            if (image.getpixel((left,y)) == color_tuple) is foreground:
                break
        else: continue
        break
    # Get the rightmost part of the image that matches the color
    for right in range(width-1, -1, -1):
        for y in range(0, height):
            if (image.getpixel((right,y)) == color_tuple) is foreground:
                right +=1
                break
        else: continue
        break
    # Get the topmost part of the image that matches the color
    for top in range(0, height):
        for x in range(0, width):
            if (image.getpixel((x,top)) == color_tuple) is foreground:
                break
        else: continue
        break
    # Get the bottommost part of the image that matches the color
    for bottom in range(height-1, -1, -1):
        for x in range(0, width):
            if (image.getpixel((x,bottom)) == color_tuple) is foreground:
                bottom += 1
                break
        else: continue
        break
    # Correct if the bounding values are invalid
    if left > right or left == right:
        left, right = (0, width)
    if top > bottom or bottom == top:
        top, bottom = (0, height)
    # Return the bounds
    return (left, top, right, bottom)
    
def get_text_line_image(text:str, font:ImageFont, font_size:int,
            image_width:int, foreground:str="#000000ff", background:str="#ffffff00",
            space:float=1.1, justified:str="c") -> Image:
    """
    Creates an image containing text in one continuous line.
    
    :param text: Text to write to the image
    :type text: str, required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param font_size: Size of the font height in pixels
    :type font_size: int, required
    :param foreground: Width of the generated image in pixels
    :type foreground: int required
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param justified: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type justified: str, optional
    :param space: Multiplied by font_size for space under the text, defaults to 1.25
    :type space: float, optional
    :return: Image with the given text on one line
    :rtype: PIL.Image
    """
    # Create an image that's larger than necessary
    image = Image.new("RGBA", size=(image_width*2, font_size*4), color="#00000000")
    # Set the font size
    altered_font = font.font_variant(size=font_size)
    # Print the text on the image
    draw = ImageDraw.Draw(image)
    draw.text(xy=(font_size,font_size), text=text, fill=foreground, font=altered_font)
    # Crop the image
    image = image.crop(get_bounds(image, "#00000000"))
    # Create the backround image with the right size
    background = Image.new("RGBA", size=(image_width, math.floor(font_size*space)), color=background)
    # Get the points in which to past the text
    text_width, text_height = image.size
    y = 1
    if justified == "l":
        x = 1
    elif justified == "r":
        x = image_width - (1 + text_width)
    else:
        x = math.floor((image_width - text_width)/2)
    # Paste the text onto the image
    background.alpha_composite(image, (x,y))
    # Return the new image
    return background

def get_text_multiline_image(lines:List[str], font:ImageFont, font_size:int,
            image_width:int, foreground:str="#000000ff", background:str="#ffffff00",
            space:float=1.1, justified:str="c") -> Image:
    """
    Creates an image containing text in multiple lines
    
    :param lines: Text to write to the image
    :type lines: Line[str], required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param font_size: Size of the font height in pixels
    :type font_size: int, required
    :param foreground: Width of the generated image in pixels
    :type foreground: int required
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param justified: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type justified: str, optional
    :param space: Multiplied by font_size for space between the text, defaults to 1.25
    :type space: float, optional
    :return: Image with the given text in multiple lines
    :rtype: PIL.Image
    """
    # Create the base for the image
    image_height = math.floor(font_size*space)
    background = Image.new("RGBA", size=(image_width, image_height*len(lines)), color=background)
    # Get a line image for each line of text
    for i in range(0, len(lines)):
        # Get a line image
        image = get_text_line_image(lines[i], font=font, font_size=font_size,
            image_width=image_width, foreground=foreground, background="#00000000",
            space=space, justified=justified)
        # Paste to the background
        background.alpha_composite(image, (0,i*image_height))
    return background

def get_word_wrap(text:str, pixel_width:int, space:float=1.1):
