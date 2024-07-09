#!/usr/bin/env python3

import os
import re
import shutil
import easy_text_to_image.text_to_image as etti
from os.path import abspath, basename, exists, join
from PIL import Image, ImageDraw
from PIL.ImageFont import ImageFont

TEST_DIRECTORY = abspath(join(abspath(join(abspath(__file__), os.pardir)), "test_files"))
FONT_DIRECTORY = abspath(join(TEST_DIRECTORY, "fonts"))
IMAGE_DIRECTORY = abspath(join(TEST_DIRECTORY, "images"))

def test_get_font_locations():
    """
    Tests the get_font_locations function.
    """
    # Test getting font locations
    font_directories = etti.get_font_locations()
    assert len(font_directories) > 0
    assert len(font_directories) < 4

def test_get_system_fonts():
    """
    Tests the get_all_system_fonts function.
    """
    # Test getting all fonts on a system
    fonts = etti.get_system_fonts([TEST_DIRECTORY])
    assert len(fonts) == 6
    assert basename(fonts[0]) == "DejaVuSans-Bold.ttf"
    assert basename(fonts[1]) == "DejaVuSans-Oblique.ttf"
    assert basename(fonts[2]) == "DejaVuSans.ttf"
    assert basename(fonts[3]) == "DejaVuSansMono.ttf"
    assert basename(fonts[4]) == "DejaVuSerif-BoldItalic.ttf"
    assert basename(fonts[5]) == "DejaVuSerif.ttf"
    assert abspath(join(fonts[0], os.pardir)) == FONT_DIRECTORY

def test_get_font():
    """
    Tests the get_font function.
    """
    # Test getting font that doesn't exist
    fonts = etti.get_system_fonts([TEST_DIRECTORY])
    fonts.append(abspath(join(FONT_DIRECTORY, "DejaVu Font Licence.txt")))
    font = etti.get_font("Blah", fonts)
    assert font is None
    # Test getting file that isn't a font
    font = etti.get_font("DejaVu Font Licence", fonts)
    assert font is None
    # Test getting a vaild font
    font = etti.get_font("DejaVuSans", fonts)
    assert font.getname() == ("DejaVu Sans", "Book")

def test_get_basic_font():
    """
    Tests the get_basic_font function.
    """
    # Test getting a serif font
    all_fonts = fonts = etti.get_system_fonts([TEST_DIRECTORY])
    font = etti.get_basic_font("serif", all_fonts)
    assert font.getname() == ("DejaVu Serif", "Book")
    # Test getting a sans-serif font.
    font = etti.get_basic_font("sans-serif", all_fonts)
    assert font.getname() == ("DejaVu Sans", "Book")
    # Test getting a monospace font.
    font = etti.get_basic_font("monospace", all_fonts)
    assert font.getname() == ("DejaVu Sans Mono", "Book")
    # Test getting a bold font
    font = etti.get_basic_font("sans-serif", all_fonts, bold=True)
    assert font.getname() == ("DejaVu Sans", "Bold")
    # Test getting italic font
    font = etti.get_basic_font("sans-serif", all_fonts, italic=True)
    assert font.getname() == ("DejaVu Sans", "Oblique")
    # Test getting bold-italic font
    font = etti.get_basic_font("serif", all_fonts, bold=True, italic=True)
    assert font.getname() == ("DejaVu Serif", "Bold Italic")
    # Test getting the default font
    font = etti.get_basic_font("serif", [])
    assert font.getname() == ("Aileron", "Regular")
    font = etti.get_basic_font("blah", all_fonts)
    assert font.getname() == ("Aileron", "Regular")
    # Test getting fallback font if bold/italic font can't be found
    font = etti.get_basic_font("monospace", all_fonts, bold=True)
    assert font.getname() == ("DejaVu Sans Mono", "Book")

def test_get_bounds():
    """
    Tests the get_bounds function.
    """
    # Test finding the bounds of a colored object in a small image
    small_image = Image.open(abspath(join(IMAGE_DIRECTORY, "small.png")))
    assert small_image.size == (200, 100)
    assert etti.get_bounds(small_image, "#d02000") == (157,72, 177, 92)
    # Test finding bounds that encompasses the whole image
    assert etti.get_bounds(small_image, "#404080") == (0,0, 200, 100)
    # Test on a large image
    small_image = Image.open(abspath(join(IMAGE_DIRECTORY, "large.png")))
    assert small_image.size == (800, 1000)
    assert etti.get_bounds(small_image, "#FFFFFF") == (32, 136, 520, 466)
    assert etti.get_bounds(small_image, "#0000FF") == (718, 920, 800, 1000)
    assert etti.get_bounds(small_image, "#FF0000") == (0, 0, 800, 1000)
    # Test image with transparency
    small_image = Image.open(abspath(join(IMAGE_DIRECTORY, "transparent.png")))
    assert small_image.size == (300, 100)
    assert etti.get_bounds(small_image, "#FFFFFF") == (72, 47, 289, 93)
    assert etti.get_bounds(small_image, "#000000") == (7, 12, 60, 37)

def test_get_text_line_image():
    """
    Tests the get_text_line_image function.
    """
    # Test getting a center justified image
    fonts = etti.get_system_fonts([TEST_DIRECTORY])
    font = etti.get_font("DejaVuSans", fonts)
    image = etti.get_text_line_image("Text thing,", font, font_size=20, image_width=300,
            foreground="#0000ffff", background="#ff0000ff", justified="c")
    assert image.size[0] == 300
    assert image.size[1] < 30 and image.size[1] > 26
    left, top, right, bottom = etti.get_bounds(image, "#0000ff")
    assert top < 7
    assert bottom > 22
    assert left < 101
    assert right > 199
    # Test getting a left justified image
    image = etti.get_text_line_image("123jkl", font, font_size=70, image_width=600, justified="l")
    assert image.size[0] == 600
    assert image.size[1] < 99 and image.size[1] > 95
    left, top, right, bottom = etti.get_bounds(image, "#000000")
    assert top < 16
    assert bottom > 80
    assert left < 4
    assert right > 199
    #Test getting a right justified image
    image = etti.get_text_line_image("Many Words", font, font_size=32, image_width=400,
                foreground="#ffff00ff", background="#ff0000ff", justified="r", space=1.5)    
    assert image.size[0] == 400
    assert image.size[1] < 59 and image.size[1] > 55
    left, top, right, bottom = etti.get_bounds(image, "#ffff00")
    assert top < 10
    assert bottom > 37
    assert left < 210
    assert right > 396
    
def test_get_text_multiline_image():
    """
    Tests the get_text_line_image function.
    """
    # Test getting a center justified image
    fonts = etti.get_system_fonts([TEST_DIRECTORY])
    font = etti.get_font("DejaVuSans", fonts)
    image = etti.get_text_multiline_image(["Something", "text and", "such."],
            font, font_size=30, image_width=300, foreground="#0000ffff",
            background="#ff0000ff", justified="c")
    assert image.size[0] == 300
    assert image.size[1] < 128 and image.size[1] > 124
    left, top, right, bottom = etti.get_bounds(image, "#0000ff")
    assert top < 9
    assert bottom > 112
    assert left < 73
    assert right > 226
    # Test getting a left justified image
    image = etti.get_text_multiline_image(["More things", "Stuff to read."],
            font, font_size=20, image_width=200, justified="l")
    assert image.size[0] == 200
    assert image.size[1] < 58 and image.size[1] > 54
    left, top, right, bottom = etti.get_bounds(image, "#000000")
    assert top < 8
    assert bottom > 47
    assert left < 4
    assert right > 127
    # Test getting a right justified image
    image = etti.get_text_multiline_image(["A", "B", "C", "D", "Yet More Things"],
            font, font_size=72, image_width=700, foreground="#00aa00ff",
            background="#000000ff", justified="r", space=1.5)
    assert image.size[0] == 700
    assert image.size[1] < 622 and image.size[1] > 618
    left, top, right, bottom = etti.get_bounds(image, "#00aa00")
    assert top < 19
    assert bottom > 578
    assert left < 134
    assert right > 696

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
    assert image.size[1] > 554 and image.size[1] < 558
    left, top, right, bottom = etti.get_bounds(image, "#101010")
    assert top < 3
    assert bottom > 553
    assert left < 4
    assert right > 289

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
    left, top, right, bottom = etti.get_bounds(image, "#ffffff")
    assert top < 7
    assert bottom > 374
    assert left < 7
    assert right > 293
    # Test aligning text to the bottom of the image
    font = etti.get_basic_font("serif", [])
    image = etti.text_image_fit_box(text, font, image_width=300, image_height=200,
            foreground="#010101ff", background="#aaaaaaff",
            justified="l", vertical="b")
    assert image.size == (300, 200)
    left, top, right, bottom = etti.get_bounds(image, "#010101")
    assert top < 72
    assert bottom > 198
    assert left < 4
    assert right > 292
    # Test aligning text vertically to the center of the image
    font = etti.get_basic_font("serif", [])
    image = etti.text_image_fit_box(text, font, image_width=300, image_height=150,
            foreground="#bb0000ff", background="#202020ff",
            justified="r", vertical="c")
    assert image.size == (300, 150)
    left, top, right, bottom = etti.get_bounds(image, "#bb0000")
    assert top < 12
    assert bottom > 138
    assert left < 9
    assert right > 296
