"""
Diet meal image matching and generation utility.

Matches diet food names with existing photographic images in
static/workout/images/diet/. If no matching image exists in the folder,
a styled PNG meal card is automatically generated and saved in that directory.
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

DIET_IMAGES_DIR = os.path.join(
    settings.BASE_DIR, 'workout', 'static', 'workout', 'images', 'diet'
)

# ───────────────────────── ─────────────────────────────────────────────────────
# Name → filename mapping for existing photographic images in diet folder.
# Keys are normalized (lowercase, alphanumeric characters only).
# ──────────────────────────────────────────────────────────────────────────────
EXISTING_IMAGE_MAP = {
    # Apple variations
    'applewithalmonds':                         'ApplewithAlmonds.png',
    'applewithcurd':                            'Applewithcurd.png',
    'applewithyogurt':                          'Applewithyogurt.png',

    # Oats variations
    'oatseggsandbanana':                        'Oatseggsandbanana.png',
    'oatsmilkandbanana':                        'Oatsmilkandbanana.png',
    'oatsmilkandfruit':                         'Oatsmilkandfruit.png',
    'oatswithmilkfruitandseeds':                'Oatswithmilkfruitandseeds.png',
    'vegetableoatsandcurd':                     'VegetableOatsandCurd.png',

    # Idli & Dosa variations
    'idlisambarandcurd':                        'Idlisambarandcurd.png',
    'idlisambarandfruit':                       'Idlisambarandfruit.png',
    'idlisambareggsandfruit':                   'Idlisambareggsandfruit.png',
    'dosasambarandfruit':                       'dosa_sambar_fruits.png',
    'dosasambarandcurd':                        'dosa_sambar_fruits.png',

    # Poha variations
    'pohawitheggsandfruit':                     'PohawithEggsandFruit.png',
    'pohawitheggs':                            'PohawithEggsandFruit.png',
    'pohaeggstofuandfruit':                     'Pohaeggstofuandfruit.png',
    'pohaeggsofruit':                          'Pohaeggstofuandfruit.png',
    'pohavegetableomeletteandfruit':            'Pohavegetableomeletteandfruit.png',

    # Upma & Eggs
    'vegetableupmaandeggs':                     'vegtableupmaandeggs.png',
    'upmaeggsandfruit':                         'vegtableupmaandeggs.png',
    'upmaeggstofuandfruit':                     'vegtableupmaandeggs.png',

    # Toast & Eggs
    'eggswholegraintoastandfruit':              'Eggswholegraintoastandfruit.png',

    # Yogurt & Curd variations
    'curdwithbanana':                           'Curdwithbanana.png',
    'curdwithwalnuts':                          'Curdwithwalnuts.png',
    'greekyogurtandnuts':                       'Greekyogurtandnuts.png',
    'greekyogurtfruitandnuts':                  'Greekyogurtfruitandnuts.png',
    'greekyogurtwithfruit':                     'Greekyogurtfruitandnuts.png',
    'guavawithgreekyogurt':                     'GuavawithGreekYogurt.png',
    'guavawithpeanuts':                         'Guavawithpeanuts.png',
    'orangewithyogurt':                         'OrangewithYogurt.png',
    'fruitwithyogurt':                          'OrangewithYogurt.png',
    'curdwithberriesseasonalfruit':             'curdwithberries.jpeg',
    'curdwithberries':                          'curdwithberries.jpeg',
    'curdwithfruit':                            'curdwithberries.jpeg',
    'curdwithfruitandnuts':                     'curdwithberries.jpeg',
    'yogurtwithbanana':                         'Curdwithbanana.png',

    # Fruit & Nuts / Peanuts
    'fruitwithnuts':                            'fruitwithnuts.png',
    'fruitwithasmallservingofnuts':             'fruitwithnuts.png',
    'bananaandmixednuts':                       'fruitwithnuts.png',
    'bananawithnuts':                           'fruitwithnuts.png',
    'bananawithmixednuts':                      'fruitwithnuts.png',
    'milksoymilkwithalmonds':                   'fruitwithnuts.png',
    'milksoymilkwithnuts':                      'fruitwithnuts.png',
    'fruitwithpeanuts':                         'fruitwithpeanuts.png',
    'bananawithpeanuts':                        'fruitwithpeanuts.png',
    'bananawithpeanutbutter':                   'fruitwithpeanuts.png',
    'peanutbuttertoast':                        'fruitwithpeanuts.png',
    'peanutbuttertoastwithfruit':               'fruitwithpeanuts.png',

    # Roasted chana variations
    'roastedchana':                             'RoastedChana.png',
    'roastedchanaandorange':                    'Roastedchanaandorange.png',
    'roastedchanawithcurd':                     'Roastedchanawithcurd.png',
    'roastedchanawithlemon':                    'roastedchannawithlemon.png',
    'roastedchannawithlemon':                   'roastedchannawithlemon.png',

    # Rice variations
    'brownricewithdalandvegetables':            'BrownRicewithDalandVegetables.png',
    'ricewithdalandvegetables':                 'BrownRicewithDalandVegetables.png',
    'brownricewithchickenpaneerandvegetables':  'brownricewithchicken.png',
    'brownricewithleanproteinandvegetables':    'brownricewithchicken.png',
    'brownricewithchicken':                     'brownricewithchicken.png',
    'brownricewithchickentofu':                 'brownricewithchicken.png',
    'ricewithfishtofuandvegetables':            'ricewithfishtofuandvegetables.png',
    'ricewithfishpaneerandvegetables':          'ricewithfishtofuandvegetables.png',
    'ricewithfishtofu':                         'ricewithfishtofuandvegetables.png',
    'ricewithchickenpaneerandvegetables':       'ricewithpanner.png',
    'ricewithpaneerchickenandvegetables':       'ricewithpanner.png',
    'ricewithchickentofuandvegetables':         'ricewithpanner.png',
    'ricewithdalchickenandvegetables':          'ricewithpanner.png',
    'ricewithdalpaneerandvegetables':           'ricewithpanner.png',
    'ricewithrajmaandvegetables':               'ricewithpanner.png',
    'brownricewithrajmaandvegetables':          'ricewithpanner.png',
    'ricewithpanner':                           'ricewithpanner.png',

    # Chapati & Roti variations
    'chapatiwithvegetablesandpaneer':           'Chapatiwithvegetablesandpaneer.png',
    'chapatiwithpaneerchickensalad':            'ChappathiwithPannerChickenSalad.png',
    'chappathiwithpannerchickensalad':          'ChappathiwithPannerChickenSalad.png',
    'chapatiwithdalandmixedvegetables':         'chappathiwithdal.png',
    'chapatiwithdalandvegetables':              'chappathiwithdal.png',
    'chapatiwithmixedvegetablesanddal':         'chappathiwithdal.png',
    'chappatiwithdalandmixedvegetables':        'chappathiwithdal.png',
    'chappatiwithdal':                          'chappathiwithdal.png',
    'chappathiwithdal':                         'chappathiwithdal.png',
    'chapatiwithdalpaneerandvegetables':        'ricewithpanner.png',
    'chappatiwithdalpaneerandvegetables':       'ricewithpanner.png',
    'chapatiwithfishpaneerandvegetables':       'ricewithfishtofuandvegetables.png',
    'chapatiwithfishtofuandvegetables':         'ricewithfishtofuandvegetables.png',
    'chappatiwithfishpaneerandvegetables':      'ricewithfishtofuandvegetables.png',
    'rotiwithtofuchickenandvegetables':         'RotiwithTofuChickenandVegetables.png',
    'rotiwithchickenpaneerandvegetables':       'RotiwithTofuChickenandVegetables.png',
    'rotiwithchickentofuandvegetables':         'RotiwithTofuChickenandVegetables.png',
    'rotiwithpaneerchickenandvegetables':       'RotiwithTofuChickenandVegetables.png',
    'rotiwithpaneertofuandvegetables':          'RotiwithTofuChickenandVegetables.png',
    'rotiwithpaneerandvegetables':              'RotiwithTofuChickenandVegetables.png',
    'rotiwithchickentofu':                      'RotiwithTofuChickenandVegetables.png',
    'rotiwithtofu':                             'RotiwithTofuChickenandVegetables.png',
    'rotiwithdalandvegetables':                 'chappathiwithdal.png',
    'rotiwithmixedvegetablesanddal':            'chappathiwithdal.png',

    # Soup
    'vegetablesoupwithproteinandroti':          'vegetablesoup.png',
    'vegetablesoup':                            'vegetablesoup.png',

    # Build Muscle / Bulk Specific Entries
    'oatswithmilkbanana23eggs':                 'Oatseggsandbanana.png',
    'greekyogurtalmonds':                       'Greekyogurtandnuts.png',
    'ricechickenpaneervegetables':              'ricewithpanner.png',
    'peanutbutterwholegraintoastfruit':         'fruitwithpeanuts.png',
    'rotipaneerchickendalvegetables':           'RotiwithTofuChickenandVegetables.png',
    '34eggswholegraintoastbanana':              'Eggswholegraintoastandfruit.png',
    'curdmixednuts':                            'Curdwithwalnuts.png',
    'brownricechickentofudalvegetables':        'brownricewithchicken.png',
    'bananapeanutbutter':                       'Curdwithbanana.png',
    'chapatipaneercurryvegetables':             'ChappathiwithPannerChickenSalad.png',
    'vegetabledosasambareggs':                  'dosa_sambar_fruits.png',
    'greekyogurtbananawalnuts':                 'Greekyogurtfruitandnuts.png',
    'ricefishpaneervegetables':                 'ricewithfishtofuandvegetables.png',
    'sproutsfruit':                             'fruitwithnuts.png',
    'rotichickentofudal':                       'RotiwithTofuChickenandVegetables.png',
    'vegetableupmaeggscurd':                    'vegtableupmaandeggs.png',
    'milkbananaalmonds':                        'Oatsmilkandbanana.png',
    'ricechickenpaneerrajmavegetables':         'ricewithpanner.png',
    'peanutbuttersandwichfruit':                'fruitwithpeanuts.png',
    'chapatifishpaneervegetables':              'ricewithfishtofuandvegetables.png',
    'pohawithpeanutseggsfruit':                 'PohawithEggsandFruit.png',
    'greekyogurtnuts':                          'Greekyogurtandnuts.png',
    'milkbananapeanutbutter':                   'Curdwithbanana.png',
    'rotipaneerchickenvegetables':              'RotiwithTofuChickenandVegetables.png',
    'oatsmilkbananapeanutbuttereggs':           'Oatseggsandbanana.png',
    'curdfruitalmonds':                         'Applewithcurd.png',
    'ricefishchickenpaneerdalvegetables':       'ricewithfishtofuandvegetables.png',
    'sproutswholegraintoast':                   'Eggswholegraintoastandfruit.png',
    'chapatichickenpaneervegetables':           'ChappathiwithPannerChickenSalad.png',
    'idlisambareggsfruit':                      'Idlisambareggsandfruit.png',
    'greekyogurtbanananuts':                    'Greekyogurtfruitandnuts.png',
    'ricechickenpaneerdalvegetables':           'ricewithpanner.png',
    'peanutbuttertoastmilk':                    'fruitwithpeanuts.png',
    # Lose Fat / Cut Specific Entries
    'vegetableupma2eggs':                       'vegtableupmaandeggs.png',
    'appleasmallhandfulofalmonds':              'ApplewithAlmonds.png',
    'applesmallhandfulofalmonds':               'ApplewithAlmonds.png',
    'brownricechickenpaneervegetables':         'brownricewithchicken.png',
    'roastedchanalemon':                        'roastedchannawithlemon.png',
    'vegetablesouppaneerchicken12roti':         'vegetablesoup.png',
    'idlisambarcurd':                           'Idlisambarandcurd.png',
    'greekyogurtfruit':                         'Greekyogurtfruitandnuts.png',
    'ricedalvegetablesgrilledchickentofu':      'BrownRicewithDalandVegetables.png',
    'guavapeanuts':                             'Guavawithpeanuts.png',
    'rotipaneerchickenvegetables':              'RotiwithTofuChickenandVegetables.png',
    'eggswholegraintoastfruit':                 'Eggswholegraintoastandfruit.png',
    'applecurd':                                'Applewithcurd.png',
    'brownriceleanchickentofuvegetables':       'brownricewithchicken.png',
    'fruitasmallhandfulofnuts':                 'fruitwithnuts.png',
    'fruitasmallservingofnuts':                 'fruitwithnuts.png',
    'rotidalmixedvegetables':                   'chappathiwithdal.png',
    'vegetableoatscurd':                        'VegetableOatsandCurd.png',
    'guavagreekyogurt':                         'GuavawithGreekYogurt.png',
    'ricefishpaneervegetables':                 'ricewithfishtofuandvegetables.png',
    'roastedchana':                             'RoastedChana.png',
    'vegetablesoup12rotiprotein':               'vegetablesoup.png',
    'pohawithvegetableseggs':                   'PohawithEggsandFruit.png',
    'orangeyogurt':                             'OrangewithYogurt.png',
    'brownricedalvegetableschickentofu':        'BrownRicewithDalandVegetables.png',
    'applealmonds':                             'ApplewithAlmonds.png',
    'rotipaneervegetables':                     'RotiwithTofuChickenandVegetables.png',
    'dosasambareggs':                           'dosa_sambar_fruits.png',
    'fruitcurd':                                'Curdwithbanana.png',
    'ricefishchickenvegetables':                'ricewithfishtofuandvegetables.png',
    'roastedchanafruit':                        'Roastedchanaandorange.png',
    'rotidalvegetables':                        'chappathiwithdal.png',
    'oatsmilkfruiteggs':                        'Oatsmilkandfruit.png',
    'guavaasmallhandfulofpeanuts':              'Guavawithpeanuts.png',
    # Maintain Weight Specific Entries
    'vegetabledosasambar2eggs':                 'dosa_sambar_fruits.png',
    'applegreekyogurt':                         'Applewithyogurt.png',
    'ricedalmixedvegetablesgrilledchickenpaneer': 'BrownRicewithDalandVegetables.png',
    'roastedchanaseasonalfruit':                'Roastedchanaandorange.png',
    '2rotipaneertofumixedvegetables':           'RotiwithTofuChickenandVegetables.png',
    'oatswithmilkbananaalmonds':                'Oatsmilkandbanana.png',
    'guavacurd':                                'GuavawithGreekYogurt.png',
    'brownricechickentofuvegetables':           'brownricewithchicken.png',
    'fruitsmallhandfulofpeanuts':               'fruitwithpeanuts.png',
    'chapatidalvegetablecurrycurd':             'chappathiwithdal.png',
    'idlisambarcurdfruit':                      'Idlisambareggsandfruit.png',
    'greekyogurtmixedfruit':                    'Greekyogurtfruitandnuts.png',
    'ricefishpaneervegetables':                 'ricewithfishtofuandvegetables.png',
    'rotichickentofuvegetablecurry':            'RotiwithTofuChickenandVegetables.png',
    'vegetablepoha2eggsfruit':                  'PohawithEggsandFruit.png',
    'bananacurd':                               'Curdwithbanana.png',
    'brownricedalvegetablespaneer':             'BrownRicewithDalandVegetables.png',
    'chapatichickenfishvegetables':             'ChappathiwithPannerChickenSalad.png',
    'vegetableupmaeggscurd':                    'vegtableupmaandeggs.png',
    'orangegreekyogurt':                        'OrangewithYogurt.png',
    'ricechickentofudalvegetables':             'ricewithpanner.png',
    'applesmallhandfulofnuts':                  'fruitwithnuts.png',
    'rotipaneervegetablescurd':                 'RotiwithTofuChickenandVegetables.png',
    'wholegraintoastvegetableomelettefruit':    'Pohavegetableomeletteandfruit.png',
    'brownricefishchickenvegetables':           'brownricewithchicken.png',
    'greekyogurtbanana':                        'Curdwithbanana.png',
    'chapatidalmixedvegetablespaneertofu':      'chappathiwithdal.png',
    'dosasambareggsfruit':                      'dosa_sambar_fruits.png',
    'curdalmondsseasonalfruit':                 'Applewithcurd.png',
    'ricepaneerchickendalvegetables':           'ricewithpanner.png',
    # Build Strength Specific Entries
    'oatswithmilkbanana3eggs':                  'Oatseggsandbanana.png',
    'chickenricedalmixedvegetables':            'BrownRicewithDalandVegetables.png',
    'rotichickenpaneervegetablescurd':          'RotiwithTofuChickenandVegetables.png',
    'vegetableomelettewholegraintoastfruit':    'Pohavegetableomeletteandfruit.png',
    'brownricefishvegetablesdal':               'ricewithfishtofuandvegetables.png',
    'chapatipaneervegetablecurrycurd':          'chappathiwithdal.png',
    'idlisambar3eggsfruit':                     'Idlisambareggsandfruit.png',
    'ricechickendalvegetables':                 'ricewithpanner.png',
    'rotifishvegetablescurd':                   'RotiwithTofuChickenandVegetables.png',
    'pohawithpeanutseggscurd':                  'PohawithEggsandFruit.png',
    'ricepaneerdalmixedvegetables':             'ricewithpanner.png',
    'wholegraintoastgreekyogurt':               'Eggswholegraintoastandfruit.png',
    'chapatichickenvegetablesdal':              'ChappathiwithPannerChickenSalad.png',
    'dosasambareggscurd':                       'dosa_sambar_fruits.png',
    'bananagreekyogurtwalnuts':                 'Greekyogurtfruitandnuts.png',
    'brownricechickenvegetablesdal':            'brownricewithchicken.png',
    'vegetableupmaeggscurdfruit':               'vegtableupmaandeggs.png',

    # General Fitness Specific Entries
    'vegetableupma2eggscurd':                   'vegtableupmaandeggs.png',
    'ricedalmixedvegetableschickenpaneer':      'BrownRicewithDalandVegetables.png',
    'bananapeanuts':                            'Curdwithbanana.png',
    'oatswithmilkbanananuts':                   'Oatsmilkandbanana.png',
    'greekyogurtseasonalfruit':                 'Greekyogurtfruitandnuts.png',
    'ricefishpaneervegetablesdal':              'ricewithfishtofuandvegetables.png',
    'rotichickentofumixedvegetables':           'RotiwithTofuChickenandVegetables.png',
    'brownricedalpaneervegetables':             'BrownRicewithDalandVegetables.png',
    'rotipaneervegetablecurrycurd':             'RotiwithTofuChickenandVegetables.png',
    'bananacurdafewnuts':                       'Curdwithbanana.png',
    'chapatidalpaneertofuvegetables':           'chappathiwithdal.png',
    'vegetableoatseggscurd':                    'VegetableOatsandCurd.png',
    'fruitmixednuts':                           'fruitwithnuts.png',

    # Hydration
    'keepwaternearbyanddrinkregularlythroughouttheday': 'Keepwaternearbyanddrinkregularlythroughouttheday.png',
}

# Color palettes & icons for auto-generated PNG cards per meal type
MEAL_PALETTES = {
    'breakfast': {
        'bg_top': (255, 248, 238),
        'bg_bottom': (254, 237, 213),
        'primary': (217, 119, 6),     # amber-600
        'accent': (180, 83, 9),       # amber-700
        'badge_bg': (245, 158, 11),   # amber-500
        'badge_text': (255, 255, 255),
        'border': (251, 191, 36),
        'icon': 'BREAKFAST',
    },
    'morning_snack': {
        'bg_top': (240, 253, 244),
        'bg_bottom': (220, 252, 231),
        'primary': (16, 185, 129),    # emerald-500
        'accent': (5, 150, 105),      # emerald-600
        'badge_bg': (16, 185, 129),
        'badge_text': (255, 255, 255),
        'border': (110, 231, 183),
        'icon': 'MORNING SNACK',
    },
    'lunch': {
        'bg_top': (238, 249, 255),
        'bg_bottom': (224, 242, 254),
        'primary': (14, 165, 233),    # sky-500
        'accent': (3, 105, 161),      # sky-700
        'badge_bg': (2, 132, 199),
        'badge_text': (255, 255, 255),
        'border': (125, 211, 252),
        'icon': 'LUNCH',
    },
    'evening_snack': {
        'bg_top': (253, 244, 255),
        'bg_bottom': (245, 208, 254),
        'primary': (168, 85, 247),    # purple-500
        'accent': (126, 34, 206),     # purple-700
        'badge_bg': (147, 51, 234),
        'badge_text': (255, 255, 255),
        'border': (216, 180, 254),
        'icon': 'EVENING SNACK',
    },
    'dinner': {
        'bg_top': (241, 245, 249),
        'bg_bottom': (226, 232, 240),
        'primary': (79, 70, 229),     # indigo-600
        'accent': (55, 48, 163),      # indigo-800
        'badge_bg': (99, 102, 241),
        'badge_text': (255, 255, 255),
        'border': (165, 180, 252),
        'icon': 'DINNER',
    },
    'hydration': {
        'bg_top': (236, 254, 255),
        'bg_bottom': (207, 250, 254),
        'primary': (6, 182, 212),     # cyan-500
        'accent': (14, 116, 144),     # cyan-700
        'badge_bg': (8, 145, 178),
        'badge_text': (255, 255, 255),
        'border': (103, 232, 249),
        'icon': 'HYDRATION',
    },
}


def normalize_key(text):
    """Normalize text by keeping only alphanumeric lowercase characters."""
    return re.sub(r'[^a-zA-Z0-9]', '', (text or '')).lower()


def find_existing_image(meal_name):
    """
    Search for a matching existing image in static/workout/images/diet/.
    Checks:
    1. Exact normalized key in EXISTING_IMAGE_MAP
    2. Exact normalized filename on disk in DIET_IMAGES_DIR
    3. Prefix / stem match against disk files
    """
    if not os.path.exists(DIET_IMAGES_DIR):
        os.makedirs(DIET_IMAGES_DIR, exist_ok=True)
        return None

    key = normalize_key(meal_name)
    if not key:
        return None

    # 1. Check mapped dictionary
    if key in EXISTING_IMAGE_MAP:
        fname = EXISTING_IMAGE_MAP[key]
        if os.path.exists(os.path.join(DIET_IMAGES_DIR, fname)):
            return fname

    # 2. Check disk files for exact normalized match
    try:
        disk_files = os.listdir(DIET_IMAGES_DIR)
    except OSError:
        disk_files = []

    for f in disk_files:
        stem, ext = os.path.splitext(f)
        if ext.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            if normalize_key(stem) == key:
                return f

    return None


def create_diet_png(meal_name, meal_type='breakfast'):
    """
    Generate a high-quality 640×360 PNG meal card image in DIET_IMAGES_DIR.
    Returns the filename of the created (or existing) PNG.
    """
    os.makedirs(DIET_IMAGES_DIR, exist_ok=True)

    clean_stem = re.sub(r'[^a-zA-Z0-9]', '', meal_name)[:48]
    if not clean_stem:
        clean_stem = f'meal_{meal_type}'
    filename = f'{clean_stem}.png'
    filepath = os.path.join(DIET_IMAGES_DIR, filename)

    if os.path.exists(filepath):
        return filename

    width, height = 640, 360
    palette = MEAL_PALETTES.get(meal_type, MEAL_PALETTES['breakfast'])

    img = Image.new('RGB', (width, height), palette['bg_top'])
    draw = ImageDraw.Draw(img)

    # Vertical gradient backdrop
    top_r, top_g, top_b = palette['bg_top']
    bot_r, bot_g, bot_b = palette['bg_bottom']
    for y in range(height):
        ratio = y / height
        r = int(top_r + (bot_r - top_r) * ratio)
        g = int(top_g + (bot_g - top_g) * ratio)
        b = int(top_b + (bot_b - top_b) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Inner decorative rounded card
    pad = 14
    draw.rounded_rectangle(
        [pad, pad, width - pad, height - pad],
        radius=20,
        fill=(255, 255, 255),
        outline=palette['border'],
        width=2
    )

    # Top accent header band
    draw.rounded_rectangle(
        [pad + 2, pad + 2, width - pad - 2, pad + 54],
        radius=18,
        fill=palette['bg_top']
    )
    # Square bottom of header band to merge smoothly
    draw.rectangle(
        [pad + 2, pad + 30, width - pad - 2, pad + 54],
        fill=palette['bg_top']
    )
    draw.line([(pad + 2, pad + 54), (width - pad - 2, pad + 54)], fill=palette['border'], width=1)

    # Fonts
    try:
        font_badge = ImageFont.truetype("segoeuib.ttf", 12)
        font_title = ImageFont.truetype("segoeuib.ttf", 23)
        font_sub = ImageFont.truetype("segoeui.ttf", 13)
        font_tag = ImageFont.truetype("segoeui.ttf", 11)
    except Exception:
        try:
            font_badge = ImageFont.truetype("arialbd.ttf", 12)
            font_title = ImageFont.truetype("arialbd.ttf", 22)
            font_sub = ImageFont.truetype("arial.ttf", 13)
            font_tag = ImageFont.truetype("arial.ttf", 11)
        except Exception:
            font_badge = font_title = font_sub = font_tag = ImageFont.load_default()

    # Meal Type Badge Pill in top left
    badge_label = meal_type.replace('_', ' ').upper()
    badge_w = max(110, len(badge_label) * 9 + 20)
    draw.rounded_rectangle(
        [pad + 16, pad + 14, pad + 16 + badge_w, pad + 40],
        radius=13,
        fill=palette['badge_bg']
    )
    draw.text(
        (pad + 26, pad + 19),
        badge_label,
        fill=palette['badge_text'],
        font=font_badge
    )

    # Top right brand label
    brand_text = "FITNESS+ DIET"
    try:
        bbox = draw.textbbox((0, 0), brand_text, font=font_badge)
        bw = bbox[2] - bbox[0]
    except Exception:
        bw = 90
    draw.text(
        (width - pad - 20 - bw, pad + 20),
        brand_text,
        fill=palette['accent'],
        font=font_badge
    )

    # Central Decorative Motif Circle
    cx, cy, cr = width // 2, 136, 42
    draw.ellipse(
        [cx - cr, cy - cr, cx + cr, cy + cr],
        fill=palette['bg_top'],
        outline=palette['border'],
        width=2
    )

    # Central symbol / geometric shape
    symbol_color = palette['primary']
    if meal_type == 'hydration':
        # Water droplet shape
        draw.polygon([(cx, cy - 24), (cx - 16, cy + 8), (cx, cy + 22), (cx + 16, cy + 8)], fill=symbol_color)
    else:
        # Balanced meal icon / bowl motif
        draw.chord([cx - 24, cy - 10, cx + 24, cy + 24], start=0, end=180, fill=symbol_color)
        draw.rectangle([cx - 24, cy - 12, cx + 24, cy - 8], fill=palette['accent'])
        draw.arc([cx - 14, cy - 22, cx + 14, cy - 12], start=180, end=0, fill=symbol_color, width=3)

    # Word-wrap meal name for clean centered presentation
    words = meal_name.split()
    lines = []
    current_line = ""
    for w in words:
        test_line = f"{current_line} {w}".strip()
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font_title)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = len(test_line) * 12

        if tw <= (width - 2 * pad - 48):
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = w
    if current_line:
        lines.append(current_line)

    # Draw Meal Name lines centered
    y_start = 198 if len(lines) <= 2 else 188
    for line in lines[:3]:
        try:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            lw = bbox[2] - bbox[0]
        except Exception:
            lw = len(line) * 12
        tx = (width - lw) // 2
        # Soft shadow
        draw.text((tx + 1, y_start + 1), line, fill=(226, 232, 240), font=font_title)
        draw.text((tx, y_start), line, fill=(30, 41, 59), font=font_title)
        y_start += 28

    # Bottom sub-badge
    bottom_tag = "HEALTHY CHOICE  •  BALANCED EVERYDAY NUTRITION"
    if meal_type == 'hydration':
        bottom_tag = "DAILY HYDRATION  •  DRINK REGULARLY"
    try:
        sbox = draw.textbbox((0, 0), bottom_tag, font=font_tag)
        sw = sbox[2] - sbox[0]
    except Exception:
        sw = 200

    tag_bg = palette['bg_top']
    tag_x1 = (width - sw) // 2 - 12
    tag_y1 = height - pad - 32
    draw.rounded_rectangle(
        [tag_x1, tag_y1, tag_x1 + sw + 24, tag_y1 + 22],
        radius=10,
        fill=tag_bg,
        outline=palette['border'],
        width=1
    )
    draw.text(
        ((width - sw) // 2, tag_y1 + 4),
        bottom_tag,
        fill=palette['accent'],
        font=font_tag
    )

    img.save(filepath, 'PNG')
    return filename


def get_diet_image_path(meal_name, meal_type='breakfast'):
    """
    Return a /static/workout/images/diet/... URL for the given meal.
    If an existing photographic image matches, returns its static path.
    Otherwise, generates a clean PNG meal card in the diet directory and returns it.
    """
    matched = find_existing_image(meal_name)
    if not matched:
        matched = create_diet_png(meal_name, meal_type)
    
    filepath = os.path.join(DIET_IMAGES_DIR, matched)
    try:
        v = int(os.path.getmtime(filepath))
        return f'/static/workout/images/diet/{matched}?v={v}'
    except OSError:
        return f'/static/workout/images/diet/{matched}'


def attach_diet_images(meals):
    """
    Attach matching or generated static image paths to a list of DietMeal objects.
    """
    if meals is None:
        return meals
    meal_list = list(meals)
    for m in meal_list:
        m.image = get_diet_image_path(m.name, m.meal_type)
    return meal_list
