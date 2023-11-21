#!/usr/bin/env python3

import os
import shutil
import easy_text_to_image.text_to_image as etti
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, join
from PIL import Image, ImageDraw

def test_get_font_locations():
    """
    Tests the get_font_locations function.
    """
    # Test getting font locations
    font_directories = etti.get_font_locations()
    assert len(font_directories) > 0
    assert len(font_directories) < 4
    # Test that some fonts exist in the given directories
    fonts = 0
    for directory in font_directories:
        assert "fonts" in directory.lower()
        fonts += len(mm_file_tools.find_files_of_type(directory, ".ttf"))
    assert fonts > 0

def test_get_font():
    """
    Tests the get_font function.
    """
    # Create test fonts
    temp_dir = mm_file_tools.get_temp_dir()
    font_dir_1 = abspath(join(temp_dir, "font_dir_1"))
    font_dir_2 = abspath(join(temp_dir, "font_dir_2"))
    os.mkdir(font_dir_1)
    os.mkdir(font_dir_2)
    mm_file_tools.write_text_file(abspath(join(font_dir_1, "test.otf")), "Not Font")
    mm_file_tools.write_text_file(abspath(join(font_dir_2, "different.ttf")), "Not Font")
    assert sorted(os.listdir(font_dir_1)) == ["test.otf"]
    assert sorted(os.listdir(font_dir_2)) == ["different.ttf"]
    # Test getting font that doesn't exist
    font = etti.get_font("Blah", [font_dir_1, font_dir_2])
    assert font is None
    # Test getting file that isn't a font
    font = etti.get_font("test", [font_dir_1, font_dir_2])
    assert font is None
    font = etti.get_font("different", [font_dir_1, font_dir_2])
    assert font is None
    # Test getting a vaild font
    real_fonts = []
    for location in etti.get_font_locations():
        real_fonts.extend(mm_file_tools.find_files_of_type(location, ".ttf"))
    assert len(real_fonts) > 0
    shutil.copy(real_fonts[0], abspath(join(font_dir_2, "valid.ttf")))
    assert sorted(os.listdir(font_dir_2)) == ["different.ttf", "valid.ttf"]
    font = etti.get_font("valid", [font_dir_1, font_dir_2])
    assert not font.getname() == ("NOT REAL", "FONT")

def test_get_basic_font():
    """
    Tests the get_basic_font function.
    """
    # Test getting a serif font
    font_locations = etti.get_font_locations()
    font = etti.get_basic_font("serif", font_locations)
    name = font.getname()[0]
    assert name == "Garamond" or name == "Georgia" or name == "Baskerville" or name == "Times"
    # Test getting a sans-serif font.
    font = etti.get_basic_font("sans-serif", font_locations)
    name = font.getname()[0]
    assert name == "Helvetica" or name == "Arial" or name == "Verdana" or name == "Tahoma"
    # Test getting a monospace font.
    font = etti.get_basic_font("monospace", font_locations)
    name = font.getname()[0]
    assert name == "Courier" or name == "Lucida" or name ==  "Monaco"
    # Test getting the default font
    font = etti.get_basic_font("serif", [])
    assert font.getname() == ("Aileron", "Regular")
    font = etti.get_basic_font("blah", font_locations)
    assert font.getname() == ("Aileron", "Regular")

def test_get_bounds():
    """
    Tests the get_bounds function.
    """
    # Test finding bounds of a colored object
    image = Image.new("RGB", size=(200, 200), color="#00ff00")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(30, 30), (170, 170)], radius=30, fill="#ff0000")
    assert etti.get_bounds(image, "#00ff00") == (30,30,171,171)
    # Test finding bounds based on foreground color
    image = Image.new("RGBA", size=(200, 200), color="#0000acff")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([(20, 50), (160, 180)], radius=30, fill="#00000000")
    assert etti.get_bounds(image, "#00000000", foreground=True) == (20,50,161,181)
    # Test finding bounds that encompass the full image
    image = Image.new("RGB", size=(150, 150), color="#220000")
    assert etti.get_bounds(image, "#ff0000") == (0,0,150,150)
    assert etti.get_bounds(image, "#220000", foreground=True) == (0,0,150,150)
    # Test finding bounds for a color that does not exist in the image
    assert etti.get_bounds(image, "#002200", foreground=True) == (0,0,150,150)
    assert etti.get_bounds(image, "#220000", foreground=False) == (0,0,150,150)

def test_get_text_line_image():
    """
    Tests the get_text_line_image function.
    """
    # Test getting a center justified image
    font = etti.get_basic_font("serif", [])
    image = etti.get_text_line_image("Text thing,", font, font_size=20, image_width=300, image_height=60,
                foreground="#0000ffff", background="#ff0000ff", justified="c")
    assert image.size == (300, 60)
    left, top, right, bottom = etti.get_bounds(image, "#ff0000ff")
    assert top > 16 and top < 24
    assert bottom > 36 and bottom < 44
    assert left > 60 and left < 150
    assert right < 250 and right > 150
    # Test getting a left justified image
    image = etti.get_text_line_image("123jkl", font, font_size=72, image_width=600, image_height=100, justified="l")
    assert image.size == (600, 100)
    left, top, right, bottom = etti.get_bounds(image, "#000000ff", foreground=True)
    assert top > 10 and top < 18
    assert bottom > 82 and bottom < 90
    assert left < 4
    assert right < 300
    #Test getting a right justified image
    image = etti.get_text_line_image("Many Words", font, font_size=32, image_width=400, image_height=80,
                foreground="#ffff00ff", background="#ff0000ff", justified="r")
    assert image.size == (400, 80)
    left, top, right, bottom = etti.get_bounds(image, "#ff0000ff")
    assert top > 20 and top < 28
    assert bottom > 52 and bottom < 60
    assert left > 200
    assert right > 396
    