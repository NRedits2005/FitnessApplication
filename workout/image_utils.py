"""Utility functions for matching exercise images by gender and auto-generating missing PNG exercise cards."""
import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

STATIC_IMAGES_DIR = os.path.join(settings.BASE_DIR, 'workout', 'static', 'workout', 'images')


def normalize_key(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text or '').lower()


def find_existing_image(exercise_name, gender):
    gender_dir = os.path.join(STATIC_IMAGES_DIR, gender)
    if not os.path.exists(gender_dir):
        os.makedirs(gender_dir, exist_ok=True)
        return None

    key = normalize_key(exercise_name)
    try:
        files = os.listdir(gender_dir)
    except OSError:
        return None

    # 1. Exact filename match (case-insensitive without extension)
    for f in files:
        f_name, ext = os.path.splitext(f)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            if f_name.lower() == exercise_name.lower():
                return f

    # 2. Normalized alphanumeric key match
    for f in files:
        f_name, ext = os.path.splitext(f)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            if normalize_key(f_name) == key:
                return f

    # 3. Singular/plural match
    for f in files:
        f_name, ext = os.path.splitext(f)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            fk = normalize_key(f_name).rstrip('s')
            if fk == key.rstrip('s'):
                return f

    return None


def create_exercise_png(exercise_name, category, gender):
    gender_dir = os.path.join(STATIC_IMAGES_DIR, gender)
    os.makedirs(gender_dir, exist_ok=True)

    clean_filename = re.sub(r'[^a-zA-Z0-9]', '', exercise_name) + '.png'
    filepath = os.path.join(gender_dir, clean_filename)

    if os.path.exists(filepath):
        return clean_filename

    width, height = 640, 360

    if gender == 'female':
        bg_color = (30, 27, 75)
        accent_color = (168, 85, 247)
        accent_gradient = (225, 29, 72)
        badge_bg = (124, 58, 237)
    else:
        bg_color = (15, 23, 42)
        accent_color = (56, 189, 248)
        accent_gradient = (16, 185, 129)
        badge_bg = (14, 116, 144)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, height], fill=bg_color)
    draw.rectangle([16, 16, width - 16, height - 16], outline=accent_color, width=3)

    draw.line([(30, 40), (120, 40)], fill=accent_gradient, width=2)
    draw.line([(width - 120, height - 40), (width - 30, height - 40)], fill=accent_gradient, width=2)

    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_badge = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_badge = font_title

    gender_label = "WOMEN'S FITNESS" if gender == 'female' else "FITNESS+"
    draw.rectangle([36, 36, 195, 62], fill=badge_bg)
    draw.text((44, 42), gender_label, fill=(255, 255, 255), font=font_badge)

    cat_text = (category or "Exercise").upper()
    draw.text((36, 78), cat_text, fill=accent_color, font=font_sub)

    try:
        bbox = draw.textbbox((0, 0), exercise_name, font=font_title)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        tw, th = 300, 30

    tx = max(20, (width - tw) // 2)
    ty = max(100, (height - th) // 2 + 10)

    draw.text((tx + 2, ty + 2), exercise_name, fill=(0, 0, 0), font=font_title)
    draw.text((tx, ty), exercise_name, fill=(255, 255, 255), font=font_title)

    sub_text = "Movement & Form Visual Guide"
    try:
        sbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        sw = sbox[2] - sbox[0]
    except AttributeError:
        sw = 200
    draw.text(((width - sw) // 2, height - 60), sub_text, fill=(203, 213, 225), font=font_sub)

    img.save(filepath, 'PNG')
    return clean_filename


def get_exercise_image_path(exercise_name, category='Full Body', gender='male'):
    gender = 'female' if str(gender).lower() == 'female' else 'male'
    matched = find_existing_image(exercise_name, gender)
    if not matched:
        matched = create_exercise_png(exercise_name, category, gender)
    
    filepath = os.path.join(STATIC_IMAGES_DIR, gender, matched)
    try:
        v = int(os.path.getmtime(filepath))
        return f'/static/workout/images/{gender}/{matched}?v={v}'
    except OSError:
        return f'/static/workout/images/{gender}/{matched}'


def attach_exercise_images(exercises, gender='male'):
    """Attach gender-matched image URLs (or auto-generated PNGs) to exercise instances."""
    gender = 'female' if str(gender).lower() == 'female' else 'male'
    if exercises is None:
        return exercises
    ex_list = list(exercises)
    for ex in ex_list:
        ex.image = get_exercise_image_path(ex.name, getattr(ex, 'category', 'Full Body'), gender)
    return ex_list
