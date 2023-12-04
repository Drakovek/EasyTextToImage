#!/usr/bin/env python3

import re
import math
import random
import textwrap
import metadata_magic.file_tools as mm_file_tools
from PIL import Image, ImageColor, ImageDraw, ImageFont
from os.path import abspath, basename, exists, expandvars, join
from typing import List

TEXT_REF = "ÅBCDÉFGHIJKLMNÖPQRSTÜVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"

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

def get_font(font_name:str, fonts:List[str], font_style:str=None) -> ImageFont:
    """
    Returns a Pillow ImageFont object for a font with the given name.
    Returns None if no valid font was found
    
    :param font_name: Name of the font to search for, with no extension
    :type font_name: str, required
    :param fonts: List of paths to system fonts
    :type fonts: List[str]
    :param font_style: Substyle of the font to attempt using, defaults to None
    :type font_style: str, optional
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

def get_basic_font(font_style:str, fonts:List[str], bold:bool=False, italic:bool=False) -> ImageFont:
    """
    Returns a Pillow ImageFont object for a font of a given style.
    If a bold/italic version of a font style can't be found, the standard version of that font will be returned.
    Returns a default font if no valid font was found.
    
    :param font_style: Style of the font to search for ("serif", "sans-serif", or "monospace")
    :type font_style: str, required
    :param fonts: List of paths to system fonts
    :type fonts: List[str]
    :param bold: Whether to try to get a bold version of this font, defaults to False
    :type bold: bool, optional
    :param italic:Whether to try to get a italic version of this font, defaults to False
    :type italic: bool, optional
    :return: Pillow ImageFont object
    :rtype: PIL.ImageFont
    """
    # Serif fonts
    font_types = dict()
    font_types["serif"] = ["Garamond", "Georgia", "Baskerville", "Times New Roman", "FreeSerif", "DejaVuSerif"]
    font_types["serif-bold"] = ["Georgia Bold", "Times New Roman Bold", "FreeSerifBold", "DejaVuSerif-Bold"]
    font_types["serif-italic"] = ["Georgia Italic", "Times New Roman Italic", "FreeSerifItalic", "DejaVuSerif-Italic"]
    font_types["serif-bold-italic"] = ["Georgia Bold Italic", "Times New Roman Bold Italic", "FreeSerifBoldItalic", "DejaVuSerif-BoldItalic"]
    # Sans-Serif fonts
    font_types["sans-serif"] = ["Helvetica", "Arial", "Verdana", "Tahoma", "FreeSans", "DejaVuSans"]
    font_types["sans-serif-bold"] = ["Arial Bold", "Verdana Bold", "Tahoma Bold", "FreeSansBold", "DejaVuSans-Bold"]
    font_types["sans-serif-italic"] = ["Arial Italic", "Verdana Italic", "FreeSansOblique", "DejaVuSans-Oblique"]
    font_types["sans-serif-bold-italic"] = ["Arial Bold Italic", "Verdana Bold Italic", "FreeSansBoldOblique", "DejaVuSans-BoldOblique"]
    # Monospace fonts
    font_types["monospace"] = ["Courier", "Courier New", "Lucida", "Monaco", "FreeMono", "DejaVu Sans Mono"]
    font_types["monospace-bold"] = ["Courier New Bold", "FreeMonoBold", "DejaVuSansMono-Bold"]
    font_types["monospace-italic"] = ["Courier New Italic", "FreeMonoOblique", "DejaVuSansMono-Oblique"]
    font_types["monospace-bold-italic"] = ["Courier New Bold Italic", "FreeMonoBoldOblique", "DejaVuSansMono-BoldOblique"]
    # Add bold/italic qualifiers to the font key if necessary
    font_key = font_style
    if bold:
        font_key = f"{font_key}-bold"
    if italic:
        font_key = f"{font_key}-italic"
    # Try to get a font
    try:
        for font in font_types[font_key]:
            image_font = get_font(font, fonts)
            if image_font is not None:
                return image_font
    except KeyError: pass
    # Try to get standard version of the font
    if bold or italic:
        return get_basic_font(font_style, fonts)
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
            space:float=1.2, justified:str="c") -> Image:
    """
    Creates an image containing text in one continuous line.
    
    :param text: Text to write to the image
    :type text: str, required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param font_size: Size of the font height in pixels
    :type font_size: int, required
    :param image_width: Width of the generated image in pixels
    :type image_width: int required
    :param foreground: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type foreground: str, optional
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param space: Multiplied by font_size for space under the text, defaults to 1.25
    :type space: float, optional
    :param justified: How to align the image ("l":left, "c":center, "r":right), defaults to "c"
    :type justified: str, optional
    :return: Image with the given text on one line
    :rtype: PIL.Image
    """
    # Create an image that's larger than necessary
    image = Image.new("RGBA", size=(image_width*2, font_size*4), color="#00000000")
    # Set the font size
    altered_font = font.font_variant(size=font_size)
    # Print the text on the image
    draw = ImageDraw.Draw(image)
    draw.text(xy=(1, 1), text=text, fill=foreground, font=altered_font)
    # Get reference text bounding box
    rl, ref_top, rr, ref_bottom = altered_font.getbbox(TEXT_REF)
    ref_bottom +=1
    # Crop the image
    left, top, right, bottom = get_bounds(image, "#00000000")
    image = image.crop((left, ref_top, right+1, ref_bottom))
    # Create the backround image with the right size
    image_height = math.floor((ref_bottom - ref_top) * space)
    background = Image.new("RGBA", size=(image_width, image_height), color=background)
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
            space:float=1.2, justified:str="c") -> Image:
    """
    Creates an image containing text in multiple lines
    
    :param lines: Text to write to the image
    :type lines: Line[str], required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param font_size: Size of the font height in pixels
    :type font_size: int, required
    :param image_width: Width of the generated image in pixels
    :type image_width: int required
    :param foreground: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type foreground: str, optional
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param space: Multiplied by font_size for space under the text, defaults to 1.25
    :type space: float, optional
    :param justified: How to align the image ("l":left, "c":center, "r":right), defaults to "c"
    :type justified: str, optional
    :return: Image with the given text in multiple lines
    :rtype: PIL.Image
    """
    # Get the basic image height
    ref_image = get_text_line_image("abc", font=font, font_size=font_size,
            image_width=100, space=space)
    image_height = ref_image.size[1]
    # Create the base for the image
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

def get_word_wrap(text:str, font:ImageFont, image_width:int, minimum_characters:int) -> (List[str], int):
    """
    Takes a text string from the user and splits it into lines based on the minimum number of characters per line.
    A value for the text size based on what can fit into a given width is also given.
    The text size will be the largest size that the given font can be to fit all the lines in the given image width.
    
    :param text: Text string to split into individual lines
    :type text: str, required
    :param font: Font intended to be used when drawing text
    :type font: ImageFont, required
    :param image_width: Width of the image that is ment to have text applied
    :type image_width: int, required
    :param minimum_characters: The minimum number of characters that can be allowed on a single line
    :type minimum_characters: int
    :return: String split into lines, size of the font to fit the width
    :rtype: (List[str], int)
    """
    # Get the longest character string in the given text
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    words = sorted(words, key=len, reverse=True)
    characters = len(words[0])
    # Make sure the character length doesn't exceed the given minumum and maximum
    if characters < minimum_characters:
        characters = minimum_characters
    # Create the wrapped text
    lines = textwrap.wrap(text.strip(), width=characters, break_long_words=False)
    # Set the conservative font size
    font_size = math.floor(image_width/(characters*2))
    # Get the line with the longest width
    line_width = 0
    largest_line = ""
    for line in lines:
        altered_font = font.font_variant(size=font_size)
        ref_left, a, ref_right, b = altered_font.getbbox(line)
        if ((ref_right+1) - ref_left) > line_width:
            line_width = (ref_right+1) - ref_left
            largest_line = line
    # Get the maximum font size
    while line_width < image_width:
        font_size += 1
        altered_font = font.font_variant(size=font_size)
        ref_left, a, ref_right, b = altered_font.getbbox(largest_line)
        line_width = (ref_right+1) - ref_left
    font_size -= 1
    # Return the lines and the font size
    return (lines, font_size)

def text_image_fit_width(text:str, font:ImageFont, image_width:int,
            foreground:str="#000000ff", background:str="#ffffff00",
            space:float=1.2, justified:str="c",
            minimum_characters:int=1) -> Image:
    """
    Returns an image containing the given text in an image with a given width in pixels.
    Text will be word-wrapped based on the minimum characters per line.
    Text will fill as much horizontal space as possible, and vertical resolution is variable.
    
    :param lines: Text to write to the image
    :type lines: Line[str], required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param image_width: Width of the generated image in pixels
    :type image_width: int, required
    :param foreground: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type foreground: str, optional
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param space: Multiplied by font_size for space under the text, defaults to 1.25
    :type space: float, optional
    :param justified: How to align the image ("l":left, "c":center, "r":right), defaults to "c"
    :type justified: str, optional
    :param minimum_characters: The minimum number of characters allowed on a single line of text, defaults to 1
    :type minimum_characters: int, optional
    :return: Image with text, wrapped to fit the given image width
    :rtype: PIL.Image
    """
    # Get the word wrap lines
    lines, font_size = get_word_wrap(text, font, image_width, minimum_characters)
    # Create the image
    image = get_text_multiline_image(lines, font, font_size, image_width=image_width,
            foreground=foreground, background="#00000000", space=space, justified=justified)
    # Crop the image
    left, top, right, bottom = get_bounds(image, "#00000000")
    right = image.size[0]
    cropped = image.crop((0, top, right, bottom))
    # Add the background
    background = Image.new("RGBA", size=(cropped.size), color=background)
    background.alpha_composite(cropped, (0,0))
    # Return the image
    return background

def text_image_fit_box(text:str, font:ImageFont, image_width:int, image_height:int,
            foreground:str="#000000ff", background:str="#ffffff00",
            space:float=1.2, justified:str="c", vertical:str="c",
            minimum_characters:int=1) -> Image:
    """
    Returns an image containing the given text in within a given width and height.
    Text will be word-wrapped based on the minimum characters per line.
    Text will fill as much of the dimensions as possible.
    
    :param lines: Text to write to the image
    :type lines: Line[str], required
    :param font: ImageFont to use for the text
    :type font: PIL.ImageFont, required
    :param image_width: Width of the generated image in pixels
    :type image_width: int, required
    :param image_height: Height of the generated image in pixels
    :type image_height: int, required
    :param foreground: Hex color value of the text in the generated image, defaults to "#000000ff"
    :type foreground: str, optional
    :param background: Hex color value of the generated image backround, defaults to "#ffffff00"
    :type background: str, optional
    :param space: Multiplied by font_size for space under the text, defaults to 1.25
    :type space: float, optional
    :param justified: How to align the image ("l":left, "c":center, "r":right), defaults to "c"
    :type justified: str, optional
    :param vertical: How to align the image vertically ("t":top, "c":center, "b":bottom), defaults to "c"
    :type vertical: str, optional
    :param minimum_characters: The minimum number of characters allowed on a single line of text, defaults to 1
    :type minimum_characters: int, optional
    :return: Image with text, wrapped to fit the given image width and height
    :rtype: PIL.Image
    """
    characters = minimum_characters - 1
    calc_height = image_height + 100
    while calc_height > image_height:
        # Set the calculated_height and text wrap character values
        characters += 1
        calc_height = image_height + 100
        # Get the word wrap lines
        lines, font_size = get_word_wrap(text, font, image_width, characters)
        low_font_size = math.floor(font_size * 0.9) - 1
        font_size += 1
        # Attempt to lower the font size until text fits in the box
        while calc_height > image_height and (font_size > low_font_size or len(lines) == 1):
            # Calculate the height of a line of text
            font_size -= 1
            altered_font = font.font_variant(size=font_size)
            rl, ref_top, rr, ref_bottom = altered_font.getbbox(TEXT_REF)
            line_height = (ref_bottom + 1) - ref_top
            # Calculate the height of the image with this font size
            calc_height = line_height + ((len(lines) - 1) * (line_height * space))
    # Create the image
    image = get_text_multiline_image(lines, font, font_size, image_width=image_width,
            foreground=foreground, background="#00000000", space=space, justified=justified)
    # Crop the image
    left, top, right, bottom = get_bounds(image, "#00000000")
    right = image.size[0]
    cropped = image.crop((0, top, right, bottom))
    # Add the background
    background = Image.new("RGBA", size=(image_width, image_height), color=background)
    cropped_height = cropped.size[1]
    if vertical == "t":
        y_position = 0
    elif vertical == "b":
        y_position = image_height - cropped_height
    else:
        y_position = math.floor((image_height - cropped_height) / 2)
    background.alpha_composite(cropped, (0,y_position))
    # Return the image
    return background

def get_color_palette() -> (str, str, str):
    """
    Returns a unique color palette with contrasting colors for text.
    Palette is randomly generated with either triadic or analogous foreground and background colors.
    Colors are generated for the foreground, background and text.
    
    :return: Tuple of #RRGGBBAA formatted colors (foreground, background, text)
    :rtype: (str, str, str)
    """
    # Randomly determine the text color, basing foreground and background values off of the result
    text_color = "#000000ff"
    foreground_value = 30
    background_value = 90
    if random.randint(0, 1) == 1:
        text_color = "#ffffffff"
        foreground_value = 90
        background_value = 30
    # Randomly determine the primary color
    foreground_hue = random.randint(0, 24) * 15
    r, g, b = ImageColor.getrgb(f"hsv({foreground_hue}, 100%, {foreground_value}%)")
    foreground_color = "#" + hex(r)[2:].zfill(2) +  hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2) + "ff"
    # Randomly determine whether to use triadic or analogous color
    hue_shift = 30
    if random.randint(0, 1) == 1:
        hue_shift = 120
    # Randomly determine whether to add or subtract the hue
    if random.randint(0, 1) == 1:
        hue_shift = hue_shift * -1
    # Get the secondary hue
    background_hue = foreground_hue + hue_shift
    if background_hue > 359:
        background_hue -= 360
    if background_hue < 0:
        background_hue += 360
    # Get the secondary_color
    r, g, b = ImageColor.getrgb(f"hsv({background_hue}, 100%, {background_value}%)")
    background_color = "#" + hex(r)[2:].zfill(2) +  hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2) + "ff"
    # Return the color palette
    return (foreground_color, background_color, text_color)
    