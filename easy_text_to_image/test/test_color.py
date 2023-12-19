#!/usr/bin/env python3

import re
import easy_text_to_image.color as etti_color

def test_get_hue_in_range():
    """
    Tests the get_hue_in_range function.
    """
    # Test if hue is in range
    assert etti_color.get_hue_in_range(0) == 0
    assert etti_color.get_hue_in_range(37) == 37
    assert etti_color.get_hue_in_range(180) == 180
    assert etti_color.get_hue_in_range(359) == 359
    # Test if hue is below range
    assert etti_color.get_hue_in_range(-1) == 359
    assert etti_color.get_hue_in_range(-50) == 310
    assert etti_color.get_hue_in_range(-180) == 180
    assert etti_color.get_hue_in_range(-300) == 60
    assert etti_color.get_hue_in_range(-400) == 320
    # Test if hue is above range
    assert etti_color.get_hue_in_range(360) == 0
    assert etti_color.get_hue_in_range(400) == 40
    assert etti_color.get_hue_in_range(560) == 200
    assert etti_color.get_hue_in_range(660) == 300
    assert etti_color.get_hue_in_range(800) == 80

def test_get_hue_offsets():
    """
    Tests the get_hue_offsets function.
    """
    # Test triadic hues
    assert etti_color.get_hue_offsets(0, offset=120) == [0, 120, 240]
    assert etti_color.get_hue_offsets(60, offset=120) == [60, 180, 300]
    assert etti_color.get_hue_offsets(100, offset=120) == [100, 220, 340]
    assert etti_color.get_hue_offsets(128, offset=120) == [128, 248, 8]
    assert etti_color.get_hue_offsets(120, offset=120) == [120, 240, 0]
    # Test tetradic hues
    assert etti_color.get_hue_offsets(0, offset=90) == [0, 90, 180, 270]
    assert etti_color.get_hue_offsets(30, offset=90) == [30, 120, 210, 300]
    assert etti_color.get_hue_offsets(45, offset=90) == [45, 135, 225, 315]
    assert etti_color.get_hue_offsets(90, offset=90) == [90, 180, 270, 0]
    # Test complimentary hues
    assert etti_color.get_hue_offsets(0, offset=180) == [0, 180]
    assert etti_color.get_hue_offsets(90, offset=180) == [90, 270]
    assert etti_color.get_hue_offsets(100, offset=180) == [100, 280]
    assert etti_color.get_hue_offsets(180, offset=180) == [180, 0]

def test_rgb_to_hex_color():
    """
    Tests the rgb_to_hex_color function.
    """
    assert etti_color.rgb_to_hex_color((255,0,0)) == "#ff0000ff"
    assert etti_color.rgb_to_hex_color((0,255,0)) == "#00ff00ff"
    assert etti_color.rgb_to_hex_color((0,0,255)) == "#0000ffff"
    assert etti_color.rgb_to_hex_color((12,13,14)) == "#0c0d0eff"

def test_get_monochrome_palette():
    """
    Tests the get_monochrome_palette function.
    """
    palette = etti_color.get_monochrome_palette(0)
    assert palette["light-saturated"] == "#e62e2eff"
    assert palette["light-desaturated"] == "#ffccccff"
    assert palette["dark-saturated"] == "#4d0f0fff"
    assert palette["dark-desaturated"] == "#331a1aff"
    palette = etti_color.get_monochrome_palette(90)
    assert palette["light-saturated"] == "#8ae62eff"
    assert palette["light-desaturated"] == "#e6ffccff"
    assert palette["dark-saturated"] == "#2e4d0fff"
    assert palette["dark-desaturated"] == "#26331aff"

def test_get_dual_hue_palette():
    """
    Tests the get_dual_hue_palette function.
    """
    palette = etti_color.get_dual_hue_palette(light_hue=30, dark_hue=120)
    assert palette["light-saturated"] == "#e68a2eff"
    assert palette["light-desaturated"] == "#ffe6ccff"
    assert palette["dark-saturated"] == "#0f4d0fff"
    assert palette["dark-desaturated"] == "#1a331aff"
    palette = etti_color.get_dual_hue_palette(light_hue=135, dark_hue=225)
    assert palette["light-saturated"] == "#2ee65cff"
    assert palette["light-desaturated"] == "#ccffd9ff"
    assert palette["dark-saturated"] == "#0f1f4dff"
    assert palette["dark-desaturated"] == "#1a2033ff"

def test_get_random_color_palette():
    """
    Tests the get_random_color_palette function.
    """
    palette = etti_color.get_random_color_palette()
    assert len(re.findall(r"^#[0-9a-f]{6}ff$", palette["primary-saturated"])) == 1
    assert len(re.findall(r"^#[0-9a-f]{6}ff$", palette["primary-desaturated"])) == 1
    assert len(re.findall(r"^#[0-9a-f]{6}ff$", palette["secondary-saturated"])) == 1
    assert len(re.findall(r"^#[0-9a-f]{6}ff$", palette["secondary-desaturated"])) == 1
