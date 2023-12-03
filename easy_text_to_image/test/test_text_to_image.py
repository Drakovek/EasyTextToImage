#!/usr/bin/env python3

import os
import re
import shutil
import easy_text_to_image.text_to_image as etti
import metadata_magic.file_tools as mm_file_tools
from os.path import abspath, exists, join
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

def test_get_system_fonts():
    """
    Tests the get_all_system_fonts function.
    """
    # Test getting all system fonts
    fonts = etti.get_system_fonts()
    assert len(fonts) > 0
    assert exists(fonts[0])
    # Get the extenstions
    extensions = []
    for font in fonts:
        extensions.append(re.findall(r"\..+$", font)[0])
    assert ".ttf" in extensions
    assert ".otc" in extensions or ".otf" in extensions or ".ttc" in extensions

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
    test_font = abspath(join(font_dir_1, "test.otf"))
    different_font = abspath(join(font_dir_2, "different.ttf"))
    mm_file_tools.write_text_file(test_font, "Not Font")
    mm_file_tools.write_text_file(different_font, "Not Font")
    assert sorted(os.listdir(font_dir_1)) == ["test.otf"]
    assert sorted(os.listdir(font_dir_2)) == ["different.ttf"]
    # Test getting font that doesn't exist
    font = etti.get_font("Blah", [test_font, different_font])
    assert font is None
    # Test getting file that isn't a font
    font = etti.get_font("test", [test_font, different_font])
    assert font is None
    font = etti.get_font("different", [test_font, different_font])
    assert font is None
    # Test getting a vaild font
    new_font = abspath(join(font_dir_2, "valid.ttf"))
    system_fonts = etti.get_system_fonts()
    for system_font in system_fonts:
        if system_font.endswith(".ttf"):
            shutil.copy(system_font, new_font)
    assert exists(new_font)
    assert sorted(os.listdir(font_dir_2)) == ["different.ttf", "valid.ttf"]
    font = etti.get_font("valid", [test_font, different_font, new_font])
    assert not font.getname() == ("NOT REAL", "FONT")

def test_get_basic_font():
    """
    Tests the get_basic_font function.
    """
    # Test getting a serif font
    system_fonts = etti.get_system_fonts()
    font = etti.get_basic_font("serif", system_fonts)
    name = font.getname()[0]
    assert not name == "Aileron"
    assert (name == "Garamond" or name == "Georgia" or name == "Baskerville"
            or name == "Times" or name == "FreeSerif" or name == "DejaVu Serif")
    # Test getting a sans-serif font.
    font = etti.get_basic_font("sans-serif", system_fonts)
    name = font.getname()[0]
    assert not name == "Aileron"
    assert (name == "Helvetica" or name == "Arial" or name == "Verdana" or name == "Tahoma"
            or name == "FreeSans" or name == "DejaVu Sans")
    # Test getting a monospace font.
    font = etti.get_basic_font("monospace", system_fonts)
    name = font.getname()[0]
    assert not name == "Aileron"
    assert (name == "Courier" or name == "Lucida" or name ==  "Monaco"
            or name == "FreeMono" or name == "DejaVu Sans Mono")
    # Test getting the default font
    font = etti.get_basic_font("serif", [])
    assert font.getname() == ("Aileron", "Regular")
    font = etti.get_basic_font("blah", system_fonts)
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
    image = etti.get_text_line_image("Text thing,", font, font_size=20, image_width=300,
            foreground="#0000ffff", background="#ff0000ff", justified="c")
    assert image.size[0] == 300
    assert image.size[1] < 28 and image.size[1] > 22
    left, top, right, bottom = etti.get_bounds(image, "#ff0000ff")
    assert top < 5
    assert bottom > 18
    assert left < 110
    assert right > 190
    # Test getting a left justified image
    image = etti.get_text_line_image("123jkl", font, font_size=70, image_width=600, justified="l")
    assert image.size[0] == 600
    assert image.size[1] < 85 and image.size[1] > 78
    left, top, right, bottom = etti.get_bounds(image, "#000000ff", foreground=True)
    assert top < 5
    assert bottom > 60
    assert left < 5
    assert right < 200
    #Test getting a right justified image
    image = etti.get_text_line_image("Many Words", font, font_size=32, image_width=400,
                foreground="#ffff00ff", background="#ff0000ff", justified="r", space=1.5)
    assert image.size[0] == 400
    assert image.size[1] < 50 and image.size[1] > 46
    left, top, right, bottom = etti.get_bounds(image, "#ff0000ff")
    assert top < 5
    assert bottom > 28
    assert left > 200
    assert right > 395
    
def test_get_text_multiline_image():
    """
    Tests the get_text_line_image function.
    """
    # Test getting a center justified image
    font = etti.get_basic_font("serif", [])
    image = etti.get_text_multiline_image(["Something", "text and", "such."],
            font, font_size=30, image_width=300, foreground="#0000ffff",
            background="#ff0000ff", justified="c")
    assert image.size[0] == 300
    assert image.size[1] < 110 and image.size[1] > 95
    left, top, right, bottom = etti.get_bounds(image, "#ff0000ff")
    assert top < 4
    assert bottom > 86
    assert left < 85
    assert right > 215
    # Test getting a left justified image
    image = etti.get_text_multiline_image(["More things", "Stuff to read."],
            font, font_size=20, image_width=200, justified="l")
    assert image.size[0] == 200
    assert image.size[1] < 55 and image.size[1] > 45
    left, top, right, bottom = etti.get_bounds(image, "#000000ff", foreground=True)
    assert top < 5
    assert bottom > 38
    assert left < 5
    assert right < 130
    # Test getting a right justified image
    image = etti.get_text_multiline_image(["A", "B", "C", "D", "Yet More Things"],
            font, font_size=72, image_width=700, foreground="#00aa00ff",
            background="#000000ff", justified="r", space=1.5)
    assert image.size[0] == 700
    assert image.size[1] < 530 and image.size[1] > 520
    left, top, right, bottom = etti.get_bounds(image, "#000000ff")
    assert top < 12
    assert bottom > 485
    assert left > 150
    assert right > 695

def test_get_word_wrap():
    """
    Tests the get_word_wrap function.
    """
    # Test if the minimum character value is less than the largest word.
    font = etti.get_basic_font("serif", [])
    lines, size = etti.get_word_wrap("This is an example sentence!!!", font, image_width=300, minimum_characters=4)
    assert lines == ["This is an", "example", "sentence!!!"]
    assert size > 58 and size < 64
    # Test if the minimum character value is greater
    font = etti.get_basic_font("serif", [])
    lines, size = etti.get_word_wrap("Just one line.", font, image_width=300, minimum_characters=50)
    assert lines == ["Just one line."]
    assert size > 46 and size < 54

def test_text_image_fit_width():
    """
    Tests the text_image_fit_width function.
    """
    font = etti.get_basic_font("serif", [])
    text = "Here is a decent number of words."
    image = etti.text_image_fit_width(text, font, image_width=300,
            foreground="#101010ff", background="#0000aaff",
            justified="l")
    assert image.size[0] == 300
    assert image.size[1] > 540 and image.size[1] < 565
    left, top, right, bottom = etti.get_bounds(image, "#0000aaff")
    assert top < 4
    assert bottom > 540
    assert left < 4
    assert right > 285

def test_text_image_fit_box():
    """
    Tests the text_image_fit_box function.
    """
    # Test aligning text to the top of the image
    font = etti.get_basic_font("serif", [])
    text = "Here is a fairly long string of text to format into a word-wrapped image."
    image = etti.text_image_fit_box(text, font, image_width=300, image_height=400,
            foreground="#ffffffff", background="#300000ff",
            justified="c", vertical="t")
    assert image.size == (300, 400)
    left, top, right, bottom = etti.get_bounds(image, "#300000ff")
    assert top < 4
    assert bottom < 385
    assert left < 6
    assert right > 294
    # Test aligning text to the bottom of the image
    font = etti.get_basic_font("serif", [])
    image = etti.text_image_fit_box(text, font, image_width=300, image_height=200,
            foreground="#010101ff", background="#aaaaaaff",
            justified="l", vertical="b")
    assert image.size == (300, 200)
    left, top, right, bottom = etti.get_bounds(image, "#aaaaaaff")
    assert top > 50
    assert bottom > 195
    assert left < 5
    assert right > 290
     # Test aligning text vertically to the center of the image
    font = etti.get_basic_font("serif", [])
    image = etti.text_image_fit_box(text, font, image_width=300, image_height=150,
            foreground="#bb0000ff", background="#202020ff",
            justified="r", vertical="c")
    assert image.size == (300, 150)
    left, top, right, bottom = etti.get_bounds(image, "#202020ff")
    assert top < 15
    assert bottom > 135
    assert left < 8
    assert right > 292