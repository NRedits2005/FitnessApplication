"""
Diet Meal Detail Data Provider for FITNESS+.

Provides authentic, rich nutrition data, ingredients, step-by-step preparation,
scientific rationale ('Why This Meal?'), dynamic goal-specific benefits across all 5 goals,
ingredient substitutions, and food-specific nutrition tips for every meal in the platform.
"""
import re
from django.utils.html import escape

# Default fallback values for hydration
HYDRATION_DATA = {
    'name': 'Daily Hydration & Fluid Balance',
    'is_hydration': True,
    'meal_type': 'hydration',
    'description': 'Proper hydration maintains optimal cellular function, joint lubrication, cognitive clarity, and physical endurance during exercise.',
    'calories': 0,
    'protein': '0 g',
    'carbs': '0 g',
    'fat': '0 g',
    'fiber': '0 g',
    'habit_title': 'Recommended Habit',
    'habit_text': 'Keep water nearby and drink regularly throughout the day.',
    'guidance': [
        {'icon': '💧', 'title': 'Daily Target', 'text': 'Aim for 2.5 to 3.5 liters of clean water daily, increasing with high sweat rates or hot climates.'},
        {'icon': '⚡', 'title': 'Electrolyte Balance', 'text': 'Add lemon, coconut water, or a tiny pinch of pink salt during prolonged or intense training sessions.'},
        {'icon': '🏋️', 'title': 'Pre & Post Workout', 'text': 'Drink 250–350 ml of water 30 minutes before your workout and replenish fluids steadily afterwards.'},
        {'icon': '⏰', 'title': 'Hydration Timing', 'text': 'Sip water consistently through the day rather than chugging large volumes all at once.'}
    ],
    'why_this_meal': 'Water is essential for nutrient transport, temperature regulation, muscle protein synthesis, and waste elimination.',
    'goal_benefits': {
        'bulk': 'Hydration is crucial for nutrient delivery to muscle tissues and maintaining training volume and intensity.',
        'cut': 'Adequate water intake prevents misinterpreting thirst as hunger and supports metabolic metabolic efficiency.',
        'maintain': 'Consistent daily hydration supports balanced digestion, steady energy levels, and vital organ function.',
        'strength': 'Even mild dehydration of 2% can reduce neuromuscular power output and training capacity significantly.',
        'fitness': 'Optimal hydration keeps energy levels high, improves stamina, and speeds up post-workout recovery.',
    },
    'substitutions': [
        {'original': 'Plain water', 'alternative': 'Infused water with mint, cucumber, or lemon slices'},
        {'original': 'Bottled sports drink', 'alternative': 'Natural tender coconut water'}
    ],
    'nutrition_tip': 'Drink a large glass of warm water first thing in the morning to rehydrate after sleep and kickstart digestion.'
}

def normalize_meal_name(name):
    """Normalize string for consistent key matching."""
    if not name:
        return ''
    # Replace en-dash, em-dash with hyphen
    text = name.replace('–', '-').replace('—', '-')
    # Remove extra spaces and lower
    return ' '.join(text.strip().split()).lower()

# Comprehensive database of all unique diet meals
MEAL_DETAILS_REGISTRY = {
    # -------------------------------------------------------------
    # BREAKFAST ITEMS (29 items)
    # -------------------------------------------------------------
    '3-4 eggs + whole-grain toast + banana': {
        'description': 'A muscle-fueling high-protein breakfast pairing whole eggs, crisp whole-grain toast, and a potassium-rich ripe banana.',
        'calories': 520,
        'protein': '30 g',
        'carbs': '55 g',
        'fat': '18 g',
        'fiber': '6 g',
        'ingredients': [
            '3–4 whole eggs or egg whites',
            '2 slices whole-grain seeded bread',
            '1 medium ripe banana',
            '1 tsp olive oil or butter for cooking',
            'Pinch of black pepper and sea salt'
        ],
        'preparation_steps': [
            'Whisk eggs in a bowl with a pinch of salt and crushed black pepper.',
            'Heat a non-stick skillet over medium heat with a light brushing of olive oil and scramble or fry eggs to your preference.',
            'Toast the whole-grain bread slices until golden brown and crispy.',
            'Slice the banana and serve alongside the hot eggs and toasted bread.'
        ],
        'why_this_meal': 'Provides complete biological protein from whole eggs to support muscle recovery, paired with complex carbohydrates for sustained energy.',
        'goal_benefits': {
            'bulk': 'Delivers high-quality protein and calorie-dense clean carbohydrates to support surplus muscle growth and recovery.',
            'cut': 'High protein content promotes long-lasting satiety and preserves lean muscle mass during a calorie deficit.',
            'maintain': 'Provides balanced macronutrients that maintain lean mass and steady blood sugar throughout the morning.',
            'strength': 'Fuels heavy lifting sessions with readily available glycogen from banana and sustained amino acids from eggs.',
            'fitness': 'Offers balanced nutrition from wholesome ingredients to power morning cardio and strength workouts.'
        },
        'substitutions': [
            {'original': 'Whole eggs', 'alternative': 'Paneer bhurji (150g) or tofu scramble'},
            {'original': 'Whole-grain toast', 'alternative': 'Multigrain roti or rolled oats'},
            {'original': 'Banana', 'alternative': 'Apple or seasonal berries'}
        ],
        'nutrition_tip': 'Consume whole eggs rather than whites only to benefit from essential choline, lutein, and healthy fats.'
    },

    'dosa + sambar + eggs': {
        'description': 'Traditional crisp fermented rice-lentil dosa paired with aromatic vegetable sambar and boiled or fried eggs.',
        'calories': 460,
        'protein': '22 g',
        'carbs': '58 g',
        'fat': '14 g',
        'fiber': '7 g',
        'ingredients': [
            '2 medium fermented dosa (rice & urad dal batter)',
            '1 bowl vegetable sambar with toor dal',
            '2 whole eggs (boiled or sunny-side up)',
            '1 tsp sesame oil or ghee',
            'Fresh coriander for garnish'
        ],
        'preparation_steps': [
            'Heat a seasoned cast-iron griddle, pour a ladle of batter, and spread thinly in circular motions.',
            'Drizzle a few drops of oil/ghee around edges and cook until crisp and golden brown.',
            'Simmer prepared sambar loaded with drumsticks, carrots, and bottle gourd.',
            'Boil or fry 2 eggs to desired doneness and serve immediately with hot dosa and sambar.'
        ],
        'why_this_meal': 'Fermented batter promotes gut health and nutrient bioavailability, while lentils and eggs deliver complete complementary amino acids.',
        'goal_benefits': {
            'bulk': 'Easily digestible carbohydrates from fermented batter combined with egg protein support post-workout glycogen reload.',
            'cut': 'Rich fiber from vegetables and dal paired with egg protein provides strong fullness with moderate fat.',
            'maintain': 'A balanced traditional staple that provides essential electrolytes, complex carbs, and clean protein.',
            'strength': 'Provides sustained muscular energy and essential B-vitamins from fermented dal for athletic performance.',
            'fitness': 'Combines probiotic fermentation, dietary fiber, and complete protein for everyday metabolic vitality.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu scramble or 100g low-fat paneer'},
            {'original': 'White rice dosa', 'alternative': 'Ragi dosa or oats dosa for higher fiber'},
            {'original': 'Sambar', 'alternative': 'Spiced sprouted moong dal stew'}
        ],
        'nutrition_tip': 'Cook dosa on a well-seasoned iron tawa with minimal oil to keep calories controlled while enjoying crisp texture.'
    },

    'dosa + sambar + eggs + curd': {
        'description': 'A nutrient-dense South Indian breakfast featuring crisp dosa, vegetable-rich sambar, whole eggs, and probiotic fresh curd.',
        'calories': 510,
        'protein': '26 g',
        'carbs': '62 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '2 crisp dosas',
            '1 cup vegetable sambar',
            '2 whole eggs (boiled or poached)',
            '1/2 cup fresh plain curd (unsweetened)',
            'Cumin and mustard seeds for tempering'
        ],
        'preparation_steps': [
            'Spread fermented batter evenly on hot skillet and cook until edges turn golden and crisp.',
            'Heat fresh vegetable sambar simmered with lentils and Indian spices.',
            'Prepare 2 soft-boiled or poached eggs seasoned with black pepper.',
            'Serve the warm dosas accompanied by a side of chilled probiotic curd, warm sambar, and eggs.'
        ],
        'why_this_meal': 'Combines dual protein sources from eggs and curd with high-fiber lentils and prebiotic/probiotic digestive benefits.',
        'goal_benefits': {
            'bulk': 'Adds casein and whey protein from fresh curd to support sustained overnight muscle protein synthesis.',
            'cut': 'High protein and dietary fiber keep hunger hormones suppressed while nourishing gut flora.',
            'maintain': 'Provides stable morning blood sugar regulation through low-GI lentils and quality protein.',
            'strength': 'Delivers muscle-repairing amino acids along with calcium and potassium for neuromuscular function.',
            'fitness': 'Supports complete digestive health, stamina, and lean body composition.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Paneer cubes (100g) lightly sautéed'},
            {'original': 'Curd', 'alternative': 'Greek yogurt or unsweetened plant curd'},
            {'original': 'Regular dosa', 'alternative': 'Moong dal chilla or oats dosa'}
        ],
        'nutrition_tip': 'Opt for fresh homemade curd to ensure live active cultures without added sugars.'
    },

    'dosa + sambar + eggs + fruit': {
        'description': 'A vibrant morning plate of golden dosas, hearty lentil sambar, protein-packed eggs, and fresh seasonal fruit slices.',
        'calories': 500,
        'protein': '24 g',
        'carbs': '68 g',
        'fat': '14 g',
        'fiber': '8 g',
        'ingredients': [
            '2 thin crispy dosas',
            '1 bowl vegetable-packed sambar',
            '2 whole eggs (scrambled or boiled)',
            '1 serving fresh seasonal fruit (papaya, apple, or orange slices)',
            '1 tsp cooking oil'
        ],
        'preparation_steps': [
            'Pour and spread dosa batter on a hot greased griddle until thin and crispy.',
            'Warm the prepared sambar packed with nutritious vegetables.',
            'Prepare 2 eggs scrambled with mild herbs or boiled.',
            'Wash, peel, and slice fresh seasonal fruit and arrange alongside the hot breakfast.'
        ],
        'why_this_meal': 'Provides an excellent blend of complex carbs, clean protein, and antioxidant vitamin C from fresh fruit to boost morning immunity.',
        'goal_benefits': {
            'bulk': 'Clean carbohydrate surplus from rice, lentils, and fresh fruits powers heavy daytime training.',
            'cut': 'The natural fiber from sambar vegetables and fruit slows digestion for extended fullness.',
            'maintain': 'Delivers balanced micronutrients, antioxidants, and macronutrients for sustained wellness.',
            'strength': 'Supports muscular energy with immediate and sustained glucose and complete amino acid profiles.',
            'fitness': 'Promotes all-around athletic stamina, cardiovascular health, and vital micronutrient intake.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Sprouted moong salad or paneer'},
            {'original': 'Seasonal fruit', 'alternative': 'Berries, kiwi, or sliced guava'},
            {'original': 'Rice dosa', 'alternative': 'Multigrain dosa'}
        ],
        'nutrition_tip': 'Eat fruit first or with the meal to maximize vitamin C absorption which aids non-heme iron uptake from lentils.'
    },

    'eggs + whole-grain toast + fruit': {
        'description': 'A classic fitness breakfast comprising cooked eggs, hearty whole-grain toast, and refreshing seasonal fruit.',
        'calories': 440,
        'protein': '22 g',
        'carbs': '50 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '2 whole eggs + 1 egg white',
            '2 slices 100% whole-grain bread',
            '1 cup sliced fresh fruit (apple, berries, or papaya)',
            '1 tsp extra virgin olive oil',
            'Pinch of black pepper and sea salt'
        ],
        'preparation_steps': [
            'Heat a pan with a small drizzle of olive oil over medium flame.',
            'Cook eggs as an omelette, sunny-side up, or scrambled with fresh herbs and pepper.',
            'Toast whole-grain bread slices until evenly browned and crisp.',
            'Slice fresh seasonal fruit and serve immediately with the warm toast and eggs.'
        ],
        'why_this_meal': 'Delivers high-biological-value protein and slow-digesting carbohydrates with rich phytonutrients from fresh fruits.',
        'goal_benefits': {
            'bulk': 'Provides essential amino acids and healthy fats for cellular recovery and testosterone support.',
            'cut': 'High satiety index helps manage appetite through the morning without excess calorie density.',
            'maintain': 'Perfect balance of macronutrients for steady energy levels and metabolic equilibrium.',
            'strength': 'Supplies essential choline and vitamin D from egg yolks for neuromuscular coordination.',
            'fitness': 'A clean, whole-food foundation that supports daily fitness sessions and active lifestyles.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu scramble with turmeric and nutritional yeast'},
            {'original': 'Whole-grain toast', 'alternative': 'Rye bread, sourdough, or oats porridge'},
            {'original': 'Seasonal fruit', 'alternative': 'Orange wedges or mixed berries'}
        ],
        'nutrition_tip': 'Select 100% whole grain bread with at least 3g of fiber per slice and no added high fructose corn syrup.'
    },

    'idli + sambar + 3 eggs + fruit': {
        'description': 'Steamed fluffy rice-lentil idlis with vegetable sambar, three eggs, and fresh seasonal fruit for high-energy mornings.',
        'calories': 530,
        'protein': '28 g',
        'carbs': '68 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '3 medium steamed idlis',
            '1 cup piping hot vegetable sambar',
            '3 eggs (2 whole + 1 white or 3 whole)',
            '1 small bowl freshly sliced seasonal fruit',
            'Chopped fresh coriander leaves'
        ],
        'preparation_steps': [
            'Grease idli plates lightly, pour fermented batter, and steam for 10–12 minutes until fluffy.',
            'Boil or poach 3 eggs, peel, and season with black pepper and a pinch of cumin.',
            'Heat sambar infused with lentils, tomatoes, and vegetables.',
            'Plate the warm idlis, pour hot sambar over or aside, and serve with eggs and fresh fruit.'
        ],
        'why_this_meal': 'Steamed cooking keeps fat low while fermentation enhances digestibility and provides a strong amino acid delivery.',
        'goal_benefits': {
            'bulk': 'High protein and clean carbohydrates supply optimal fuel for muscle hypertrophy.',
            'cut': 'High volume, low fat content, and substantial fiber keep you full during calorie deficits.',
            'maintain': 'Wholesome combination that preserves muscle mass and supplies steady energy.',
            'strength': 'Provides essential B-vitamins and magnesium to support heavy strength training.',
            'fitness': 'Optimal light-on-stomach fuel for morning cardiovascular and functional endurance workouts.'
        },
        'substitutions': [
            {'original': '3 eggs', 'alternative': '150g grilled paneer or tofu'},
            {'original': 'Rice idli', 'alternative': 'Ragi idli or oats idli'},
            {'original': 'Fruit', 'alternative': 'Fresh pomegranate or sliced kiwi'}
        ],
        'nutrition_tip': 'Idli is completely oil-free when steamed, making it one of the cleanest carbohydrate sources available.'
    },

    'idli + sambar + curd': {
        'description': 'A gentle, gut-friendly South Indian breakfast of steamed idlis, spiced lentil sambar, and cool probiotic curd.',
        'calories': 410,
        'protein': '18 g',
        'carbs': '65 g',
        'fat': '8 g',
        'fiber': '7 g',
        'ingredients': [
            '3 soft steamed idlis',
            '1 cup vegetable sambar',
            '1/2 cup fresh plain probiotic curd',
            'Curry leaves and mustard seeds for aroma'
        ],
        'preparation_steps': [
            'Steam the idlis in an idli steamer until soft, light, and fully cooked.',
            'Prepare or reheat aromatic vegetable sambar containing lentils and gourds.',
            'Whisk fresh plain curd lightly with a pinch of roasted cumin powder if desired.',
            'Serve the warm idlis with the sambar and a soothing bowl of fresh curd.'
        ],
        'why_this_meal': 'Extremely gentle on digestion, rich in gut-healthy probiotics and prebiotics with low dietary fat.',
        'goal_benefits': {
            'bulk': 'Easily digestible carbohydrates allow for rapid glycogen replenishment without sluggishness.',
            'cut': 'Low-fat, nutrient-dense profile helps stay well within cutting targets while staying energized.',
            'maintain': 'Maintains healthy digestive flora and balanced blood sugar for everyday vitality.',
            'strength': 'Provides quick, clean glycogen to restore depleted muscle stores after workouts.',
            'fitness': 'Promotes gut microbiome health and continuous energy for active individuals.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Unsweetened Greek yogurt or almond milk curd'},
            {'original': 'White idli', 'alternative': 'Multigrain or brown rice idli'},
            {'original': 'Sambar', 'alternative': 'Vegetable dal soup'}
        ],
        'nutrition_tip': 'Pairing curd with fermented foods creates a powerful symbiotic effect that improves gut microbiome diversity.'
    },

    'idli + sambar + curd + fruit': {
        'description': 'A wholesome breakfast platter of steamed idlis, vegetable sambar, refreshing curd, and antioxidant-rich fresh fruit.',
        'calories': 460,
        'protein': '19 g',
        'carbs': '76 g',
        'fat': '8 g',
        'fiber': '9 g',
        'ingredients': [
            '3 steamed idlis',
            '1 cup vegetable sambar',
            '1/2 cup fresh curd',
            '1 cup diced seasonal fresh fruit (papaya, apple, or pomegranate)',
            'Pinch of roasted cumin powder'
        ],
        'preparation_steps': [
            'Steam the idlis until spongy and cooked through.',
            'Simmer sambar loaded with carrots, drumsticks, and yellow lentils.',
            'Portion fresh cool curd into a small bowl.',
            'Wash, dice, and arrange fresh seasonal fruit to complete the wholesome plate.'
        ],
        'why_this_meal': 'Supplies a rich spectrum of vitamins, live probiotics, natural digestive enzymes, and steady-releasing carbohydrates.',
        'goal_benefits': {
            'bulk': 'Provides clean energy and easily absorbable nutrients to power high training volume.',
            'cut': 'High volume and fiber ensure long satiety while remaining naturally low in saturated fats.',
            'maintain': 'Balanced blend of complex carbs, protein, and micronutrients for daily vitality.',
            'strength': 'Restores muscle glycogen quickly while providing electrolytes from fruits and sambar.',
            'fitness': 'Boosts morning hydration, digestive efficiency, and cellular energy.'
        },
        'substitutions': [
            {'original': 'Regular idli', 'alternative': 'Oats or ragi idli for additional dietary fiber'},
            {'original': 'Curd', 'alternative': 'Greek yogurt for higher protein density'},
            {'original': 'Seasonal fruit', 'alternative': 'Mixed berries or sliced guava'}
        ],
        'nutrition_tip': 'Eat the fruit at the beginning of the meal to take full advantage of its natural digestive enzymes.'
    },

    'idli + sambar + eggs + fruit': {
        'description': 'Fluffy steamed idlis served with vegetable-rich sambar, whole eggs, and sliced seasonal fruit.',
        'calories': 480,
        'protein': '24 g',
        'carbs': '65 g',
        'fat': '13 g',
        'fiber': '8 g',
        'ingredients': [
            '2–3 steamed idlis',
            '1 cup vegetable sambar with toor dal',
            '2 whole eggs (boiled or poached)',
            '1 bowl seasonal fruit slices',
            'Pinch of black pepper'
        ],
        'preparation_steps': [
            'Steam idlis until light and fluffy.',
            'Boil or poach eggs for 6–7 minutes and season with pepper.',
            'Reheat hot vegetable sambar with aromatic spices.',
            'Plate idlis with sambar, sliced eggs, and fresh seasonal fruit.'
        ],
        'why_this_meal': 'Fermented carbs and high-biological value egg protein deliver sustained energy and support muscle tissue repair.',
        'goal_benefits': {
            'bulk': 'Complete amino acid profile supports muscle repair alongside clean glycogen replenishment.',
            'cut': 'High protein and dietary fiber keep you full and energized during a calorie deficit.',
            'maintain': 'Balanced morning plate that maintains steady energy and body composition.',
            'strength': 'Delivers choline, iron, and potassium to support central nervous system performance.',
            'fitness': 'Wholesome real-food energy that fuels cardiovascular endurance and strength.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Paneer bhurji (120g) or tofu scramble'},
            {'original': 'White idli', 'alternative': 'Sprouted moong idli'},
            {'original': 'Fruit', 'alternative': 'Orange slices or fresh apple'}
        ],
        'nutrition_tip': 'Adding eggs to an idli-sambar meal dramatically improves the overall leucine content needed for muscle synthesis.'
    },

    'oats + milk + banana + peanut butter + eggs': {
        'description': 'A high-calorie powerhouse breakfast combining warm rolled oats cooked in milk, sliced banana, natural peanut butter, and eggs.',
        'calories': 620,
        'protein': '34 g',
        'carbs': '72 g',
        'fat': '22 g',
        'fiber': '9 g',
        'ingredients': [
            '1/2 cup rolled oats (50g)',
            '1 cup cow milk or soy milk (240ml)',
            '1 medium ripe banana',
            '1 tbsp natural peanut butter (15g)',
            '2 whole eggs (boiled or scrambled)',
            'Pinch of cinnamon'
        ],
        'preparation_steps': [
            'Add rolled oats and milk to a saucepan, bring to a gentle simmer, and cook for 4–5 minutes until creamy.',
            'Stir in natural peanut butter and a pinch of ground cinnamon until fully melted and combined.',
            'Transfer oats to a bowl and top with sliced ripe banana.',
            'Prepare 2 boiled or scrambled eggs on the side and serve together.'
        ],
        'why_this_meal': 'A caloric and nutritional giant loaded with beta-glucan fiber, monounsaturated fats, and multi-source proteins.',
        'goal_benefits': {
            'bulk': 'An exceptional bulking breakfast supplying calorie density, healthy fats, and high protein for rapid muscle mass gains.',
            'cut': 'Can be portioned into 1 egg + 1 tsp peanut butter for incredible long-lasting satiety.',
            'maintain': 'Provides sustained all-day energy and comprehensive micronutrients for active individuals.',
            'strength': 'Loaded with magnesium, zinc, potassium, and amino acids to support maximal strength development.',
            'fitness': 'Ideal pre-workout meal 2 hours before demanding endurance or high-intensity training.'
        },
        'substitutions': [
            {'original': 'Peanut butter', 'alternative': 'Almond butter or crushed roasted walnuts'},
            {'original': 'Eggs', 'alternative': '1 scoop whey or plant protein powder stirred into oats'},
            {'original': 'Cow milk', 'alternative': 'Soy milk or oat milk'}
        ],
        'nutrition_tip': 'Choose 100% natural peanut butter containing only roasted peanuts and salt without hydrogenated palm oils.'
    },

    'oats + milk + fruit + eggs': {
        'description': 'Nutrient-rich rolled oats cooked in milk, paired with fresh mixed fruit and protein-packed eggs.',
        'calories': 490,
        'protein': '26 g',
        'carbs': '60 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1 cup milk',
            '1/2 cup fresh mixed berries or diced apple',
            '2 whole eggs (boiled or poached)',
            'Pinch of cinnamon powder'
        ],
        'preparation_steps': [
            'Simmer rolled oats in milk over medium heat for 4–5 minutes until soft and thick.',
            'Stir in ground cinnamon and transfer porridge to a serving bowl.',
            'Top the warm oats with freshly washed mixed fruit or sliced apple.',
            'Boil or poach 2 eggs, season with pepper, and serve alongside the oats bowl.'
        ],
        'why_this_meal': 'Delivers soluble fiber (beta-glucan) for heart health, paired with complete egg protein and antioxidant-rich fruit.',
        'goal_benefits': {
            'bulk': 'Sustained energy and complete amino acids support muscle recovery without unnecessary sugar spikes.',
            'cut': 'High dietary fiber and protein keep appetite under control throughout the entire morning.',
            'maintain': 'Balances steady blood glucose with quality protein for everyday active wellness.',
            'strength': 'Provides essential glycogen and electrolytes for high-intensity training sessions.',
            'fitness': 'Fuel for cardiovascular health, endurance, and sustained physical vitality.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Greek yogurt or 1 scoop protein powder'},
            {'original': 'Cow milk', 'alternative': 'Unsweetened almond milk or soy milk'},
            {'original': 'Mixed fruit', 'alternative': 'Banana or seasonal pomegranate'}
        ],
        'nutrition_tip': 'Cinnamon naturally helps enhance insulin sensitivity, improving how your muscle cells utilize carbohydrates.'
    },

    'oats with milk + banana + 3 eggs': {
        'description': 'A robust strength-building breakfast featuring warm milk oats, potassium-rich banana, and 3 whole eggs.',
        'calories': 580,
        'protein': '32 g',
        'carbs': '65 g',
        'fat': '20 g',
        'fiber': '7 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1 cup warm milk',
            '1 medium banana sliced',
            '3 whole eggs',
            'Pinch of sea salt and pepper'
        ],
        'preparation_steps': [
            'Cook rolled oats in milk until creamy and thick (approx 4–5 minutes).',
            'Slice the banana and gently fold into or arrange on top of the warm oatmeal.',
            'Boil, scramble, or fry 3 eggs with minimal oil in a non-stick pan.',
            'Season eggs with sea salt and black pepper, and serve immediately.'
        ],
        'why_this_meal': 'High protein density coupled with potassium and slow-release carbohydrates supports muscular power and quick glycogen replenishment.',
        'goal_benefits': {
            'bulk': 'Supplies a substantial protein surplus and quality complex carbohydrates for lean mass expansion.',
            'cut': 'Remarkable satiety index that prevents afternoon snacking cravings while preserving muscle.',
            'maintain': 'Provides strong sustained fuel for athletic individuals requiring stable daily energy.',
            'strength': 'Supplies the amino acids, creatine precursors, and potassium required for heavy resistance training.',
            'fitness': 'Builds physical stamina and supports rapid recovery after morning training.'
        },
        'substitutions': [
            {'original': '3 eggs', 'alternative': '150g grilled paneer or tofu'},
            {'original': 'Cow milk', 'alternative': 'Soy milk for high plant protein'},
            {'original': 'Banana', 'alternative': 'Diced apple with cinnamon'}
        ],
        'nutrition_tip': 'Eating whole eggs provides dietary cholesterol, a vital precursor for natural anabolic hormone production.'
    },

    'oats with milk + banana + almonds': {
        'description': 'A wholesome, antioxidant-packed bowl of oats simmered in milk, topped with sliced banana and crunchy crushed almonds.',
        'calories': 470,
        'protein': '17 g',
        'carbs': '68 g',
        'fat': '16 g',
        'fiber': '9 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1 cup low-fat or whole milk',
            '1 medium ripe banana',
            '10–12 raw almonds (chopped)',
            'Pinch of cardamom or cinnamon'
        ],
        'preparation_steps': [
            'Combine rolled oats and milk in a saucepan and cook over medium flame until thick and creamy.',
            'Transfer cooked oatmeal into a breakfast bowl and stir in a pinch of cardamom powder.',
            'Slice the banana into rounds and arrange across the top of the bowl.',
            'Scatter chopped raw almonds over the porridge for a rich, satisfying crunch.'
        ],
        'why_this_meal': 'Rich in vitamin E, magnesium, heart-healthy monounsaturated fats, and prebiotic fibers that nourish beneficial gut bacteria.',
        'goal_benefits': {
            'bulk': 'Dense source of clean carbohydrates and healthy fats that support daily caloric requirements.',
            'cut': 'High fiber and healthy fats slow gastric emptying, keeping you feeling full for hours.',
            'maintain': 'Provides balanced, steady energy release and cardiovascular support.',
            'strength': 'Delivers magnesium and zinc from almonds to optimize muscle contraction and recovery.',
            'fitness': 'An excellent clean-fuel breakfast for running, cycling, or general fitness conditioning.'
        },
        'substitutions': [
            {'original': 'Almonds', 'alternative': 'Walnuts, pumpkin seeds, or chia seeds'},
            {'original': 'Cow milk', 'alternative': 'Almond milk or soy milk'},
            {'original': 'Banana', 'alternative': 'Fresh blueberries or grated apple'}
        ],
        'nutrition_tip': 'Soak almonds overnight and peel if preferred to enhance digestive comfort and mineral absorption.'
    },

    'oats with milk + banana + nuts': {
        'description': 'Warm creamy oatmeal cooked with milk, topped with fresh banana slices and a medley of mixed crunchy nuts.',
        'calories': 480,
        'protein': '18 g',
        'carbs': '66 g',
        'fat': '17 g',
        'fiber': '9 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1 cup milk',
            '1 ripe banana',
            '15g mixed raw nuts (almonds, walnuts, cashews)',
            'Pinch of cinnamon'
        ],
        'preparation_steps': [
            'Cook rolled oats in milk for 4–5 minutes until smooth and thickened.',
            'Stir in a dash of ground cinnamon for natural warmth and flavor.',
            'Top with freshly sliced banana rounds.',
            'Chop the mixed nuts and sprinkle generously over the bowl before serving.'
        ],
        'why_this_meal': 'Supplies omega-3 fatty acids from walnuts, vitamin E from almonds, and sustained carbohydrates from whole rolled oats.',
        'goal_benefits': {
            'bulk': 'Clean calorie-dense mix that aids progressive weight gain without refined sugars.',
            'cut': 'High fiber content regulates blood sugar and controls hunger hormones efficiently.',
            'maintain': 'Balanced everyday breakfast supporting sharp mental focus and sustained stamina.',
            'strength': 'Provides essential fatty acids and minerals that reduce systemic exercise-induced inflammation.',
            'fitness': 'Fuels aerobic capacity and provides sustained morning energy.'
        },
        'substitutions': [
            {'original': 'Mixed nuts', 'alternative': 'Sunflower seeds and pumpkin seeds'},
            {'original': 'Cow milk', 'alternative': 'Oat milk or soy milk'},
            {'original': 'Banana', 'alternative': 'Seasonal pear or apple'}
        ],
        'nutrition_tip': 'Including walnuts provides plant-based ALA omega-3s which help reduce joint soreness after intense workouts.'
    },

    'oats with milk, banana + 2-3 eggs': {
        'description': 'A balanced fitness breakfast combining creamy milk oatmeal, sliced banana, and whole eggs for optimal morning nutrition.',
        'calories': 530,
        'protein': '28 g',
        'carbs': '62 g',
        'fat': '18 g',
        'fiber': '7 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1 cup milk',
            '1 medium banana',
            '2–3 eggs (boiled or scrambled)',
            'Pinch of black pepper and cinnamon'
        ],
        'preparation_steps': [
            'Simmer oats in milk with a dash of cinnamon until creamy (4–5 mins).',
            'Slice the banana and layer over the prepared oatmeal.',
            'Cook 2–3 eggs in a pan or boil to soft/hard perfection and season with pepper.',
            'Serve the oatmeal bowl alongside the hot seasoned eggs.'
        ],
        'why_this_meal': 'Provides complete protein for muscle protein synthesis combined with slow-burning complex carbohydrates.',
        'goal_benefits': {
            'bulk': 'Supports muscle hypertrophy with 28g+ of bioavailable protein and clean carbohydrates.',
            'cut': 'High protein-to-calorie ratio supports fat loss while preserving metabolic rate.',
            'maintain': 'Maintains lean body mass and sustained energy throughout active mornings.',
            'strength': 'Supplies essential branched-chain amino acids (BCAAs) for fast muscle repair.',
            'fitness': 'Optimal fuel for all-round athletic performance and recovery.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '100g low-fat paneer or tofu'},
            {'original': 'Cow milk', 'alternative': 'Soy milk or almond milk'},
            {'original': 'Banana', 'alternative': 'Fresh strawberries or apple'}
        ],
        'nutrition_tip': 'Pairing complex carbs with complete proteins lowers the glycemic impact of the meal, preventing energy crashes.'
    },

    'poha with peanuts + eggs + curd': {
        'description': 'Savory flattened rice tempered with mustard seeds, crunchy roasted peanuts, paired with eggs and cool curd.',
        'calories': 510,
        'protein': '25 g',
        'carbs': '58 g',
        'fat': '20 g',
        'fiber': '6 g',
        'ingredients': [
            '1 cup thick poha (flattened rice, rinsed)',
            '2 tbsp roasted peanuts',
            '1 medium onion and green chili (finely chopped)',
            '1/2 tsp turmeric and mustard seeds',
            '2 whole eggs (boiled or scrambled)',
            '1/2 cup fresh plain curd',
            '1 tsp oil and fresh lemon juice'
        ],
        'preparation_steps': [
            'Rinse poha in a colander and drain thoroughly so it stays fluffy.',
            'Heat 1 tsp oil, splutter mustard seeds, curry leaves, and sauté onions with roasted peanuts and turmeric.',
            'Gently toss in the softened poha, season with salt, and finish with fresh lemon juice and coriander.',
            'Boil or scramble 2 eggs, and serve with the warm poha and a side of fresh curd.'
        ],
        'why_this_meal': 'Flattened rice is an easily digestible iron-rich carb source, while peanuts, eggs, and curd provide diverse protein and healthy fats.',
        'goal_benefits': {
            'bulk': 'Supplies healthy fats and calorie-dense carbs to support muscle building effortlessly.',
            'cut': 'The combination of protein and fiber promotes fullness while keeping refined sugars at zero.',
            'maintain': 'A balanced traditional Indian breakfast that provides sustained daily energy.',
            'strength': 'Supplies iron for oxygen transport and quality protein for muscular recovery.',
            'fitness': 'Light on the stomach yet energizing for daily workouts and athletic routines.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Paneer cubes (100g) tossed into the poha'},
            {'original': 'Poha', 'alternative': 'Red rice poha or quinoa poha'},
            {'original': 'Curd', 'alternative': 'Greek yogurt'}
        ],
        'nutrition_tip': 'Squeezing fresh lemon juice over poha provides vitamin C, which multiplies non-heme iron absorption from the flattened rice.'
    },

    'poha with peanuts + eggs + fruit': {
        'description': 'A flavorful breakfast of spiced flattened rice with crunchy peanuts, served with eggs and refreshing fresh fruit.',
        'calories': 500,
        'protein': '23 g',
        'carbs': '64 g',
        'fat': '18 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup flattened rice (poha)',
            '2 tbsp peanuts',
            '1 chopped onion, curry leaves, green chili',
            '1/2 tsp turmeric powder',
            '2 whole eggs',
            '1 cup fresh seasonal fruit slices (orange or papaya)',
            '1 tsp oil and lemon juice'
        ],
        'preparation_steps': [
            'Wash and drain poha; let it sit to soften for 5 minutes.',
            'Heat oil in a pan, fry peanuts until crunchy, then sauté onions, green chilies, and curry leaves with turmeric.',
            'Add the soaked poha and salt, gently fold, and steam covered on low heat for 2 minutes before adding lemon juice.',
            'Serve with 2 cooked eggs and a side of chilled seasonal fruit.'
        ],
        'why_this_meal': 'Combines bioavailable iron, complete proteins, healthy monounsaturated fats from peanuts, and vitamin C from fresh fruits.',
        'goal_benefits': {
            'bulk': 'Provides clean carbohydrates and dense healthy fats for optimal recovery and mass gain.',
            'cut': 'Fiber from peanuts and fruit enhances satiety and maintains stable energy during caloric deficits.',
            'maintain': 'Provides a wholesome macronutrient profile for steady vitality and body weight maintenance.',
            'strength': 'Iron and protein support oxygenation of muscle tissues during heavy lifting.',
            'fitness': 'Ideal morning fuel that provides sustained stamina without causing digestive sluggishness.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu cubes (120g) sautéed with spices'},
            {'original': 'Peanuts', 'alternative': 'Roasted almonds or sunflower seeds'},
            {'original': 'White poha', 'alternative': 'Brown rice poha'}
        ],
        'nutrition_tip': 'Peanuts provide resveratrol and arginine, which help improve nitric oxide production and blood flow.'
    },

    'poha with vegetables + eggs': {
        'description': 'Nutrient-dense flattened rice loaded with green peas, carrots, and beans, served with protein-rich eggs.',
        'calories': 440,
        'protein': '22 g',
        'carbs': '54 g',
        'fat': '15 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup flattened rice (poha)',
            '1/2 cup finely diced mixed vegetables (carrots, green peas, beans)',
            '1 chopped onion, mustard seeds, curry leaves, turmeric',
            '2 whole eggs',
            '1 tsp oil, lemon juice, fresh coriander'
        ],
        'preparation_steps': [
            'Rinse poha and drain thoroughly.',
            'Heat 1 tsp oil, temper mustard seeds and curry leaves, then sauté onions and mixed vegetables until tender-crisp.',
            'Add turmeric, salt, and drained poha; toss gently until hot and fragrant, then drizzle lemon juice.',
            'Prepare 2 boiled or sunny-side-up eggs and plate alongside the vegetable poha.'
        ],
        'why_this_meal': 'Adding mixed vegetables triples the micronutrient and fiber density of traditional poha while eggs provide complete protein.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding while flooding the body with vital phytonutrients.',
            'cut': 'High volume and low calorie density make this an exceptional cutting breakfast.',
            'maintain': 'Supports lean body mass and long-lasting metabolic energy.',
            'strength': 'Delivers B-vitamins and trace minerals necessary for power output and recovery.',
            'fitness': 'Rich in antioxidants and clean carbohydrates for endurance and cardiovascular health.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Paneer bhurji or sprouted moong'},
            {'original': 'White poha', 'alternative': 'Red poha or broken wheat upma'},
            {'original': 'Vegetables', 'alternative': 'Spinach and bell peppers'}
        ],
        'nutrition_tip': 'Use colorful vegetables like carrots and green peas to supply carotenoids that protect cells from exercise-induced oxidative stress.'
    },

    'vegetable dosa + sambar + 2 eggs': {
        'description': 'Crisp fermented dosa studded with finely chopped vegetables, served with hearty lentil sambar and 2 eggs.',
        'calories': 480,
        'protein': '24 g',
        'carbs': '60 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '2 vegetable dosas (batter topped with grated carrots, onions, cilantro)',
            '1 cup vegetable sambar with toor dal',
            '2 whole eggs (boiled or poached)',
            '1 tsp sesame oil or ghee'
        ],
        'preparation_steps': [
            'Spread fermented batter on a hot griddle, top with finely diced onions, carrots, and coriander, and press lightly.',
            'Drizzle minimal oil and flip when bottom is golden crisp.',
            'Warm the lentil sambar loaded with garden vegetables.',
            'Serve hot with 2 boiled or poached eggs seasoned with freshly ground black pepper.'
        ],
        'why_this_meal': 'Fermented batter and vegetables support gut microbiome health, while lentils and eggs deliver all essential amino acids.',
        'goal_benefits': {
            'bulk': 'Provides easily utilized glycogen and quality protein to sustain intensive hypertrophy training.',
            'cut': 'Generous dietary fiber from lentils and vegetables suppresses hunger during a cut.',
            'maintain': 'Wholesome everyday breakfast with balanced macros and micronutrients.',
            'strength': 'Delivers potassium, magnesium, and protein to support heavy neuromuscular efforts.',
            'fitness': 'Promotes gut health, lean muscle maintenance, and steady morning endurance.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '100g sautéed paneer or tofu'},
            {'original': 'White dosa batter', 'alternative': 'Ragi or oats dosa batter'},
            {'original': 'Sambar', 'alternative': 'Sprouted moong stew'}
        ],
        'nutrition_tip': 'Fermentation increases the bioavailability of zinc and B-vitamins in the rice and lentil batter.'
    },

    'vegetable dosa + sambar + eggs': {
        'description': 'Crispy vegetable-topped dosa accompanied by aromatic lentil-vegetable sambar and cooked eggs.',
        'calories': 470,
        'protein': '23 g',
        'carbs': '58 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '2 vegetable dosas',
            '1 cup hot vegetable sambar',
            '2 eggs (boiled or scrambled)',
            '1 tsp cooking oil'
        ],
        'preparation_steps': [
            'Pour batter on hot tawa, sprinkle chopped veggies on top, and cook until bottom is golden and crisp.',
            'Simmer sambar packed with nutritious vegetables and dal.',
            'Cook eggs to preference (boiled or soft scrambled) with a pinch of pepper.',
            'Plate the hot dosa with sambar and eggs and serve immediately.'
        ],
        'why_this_meal': 'Fermented rice-lentil blend promotes digestive wellness while eggs and lentils supply complete protein.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and amino acids to support lean muscle building.',
            'cut': 'High fiber and protein keep appetite satiated for hours.',
            'maintain': 'Maintains steady blood glucose and lean body composition.',
            'strength': 'Replenishes glycogen and provides leucine for muscle protein synthesis.',
            'fitness': 'Optimal light-on-stomach fuel for active morning workouts.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu scramble or paneer'},
            {'original': 'Rice dosa', 'alternative': 'Moong dal chilla'},
            {'original': 'Sambar', 'alternative': 'Mixed vegetable stew'}
        ],
        'nutrition_tip': 'Adding grated carrots and onions directly into the dosa batter increases moisture and dietary fiber naturally.'
    },

    'vegetable oats + curd': {
        'description': 'Savory masala oats cooked with mixed diced vegetables, paired with a soothing bowl of fresh probiotic curd.',
        'calories': 380,
        'protein': '16 g',
        'carbs': '56 g',
        'fat': '9 g',
        'fiber': '8 g',
        'ingredients': [
            '1/2 cup rolled oats (50g)',
            '1/2 cup mixed diced vegetables (carrots, beans, peas, bell peppers)',
            '1/2 tsp cumin, mustard seeds, turmeric, and ginger',
            '1/2 cup fresh plain curd (unsweetened)',
            '1 tsp oil and fresh coriander'
        ],
        'preparation_steps': [
            'Heat 1 tsp oil in a pan, sauté cumin, mustard seeds, ginger, and diced vegetables for 3 minutes.',
            'Add turmeric, salt, and 1.5 cups of water; bring to a boil.',
            'Stir in rolled oats and simmer for 4–5 minutes until thick and savory.',
            'Garnish with fresh coriander and serve warm alongside cool fresh curd.'
        ],
        'why_this_meal': 'High in beta-glucan soluble fiber to regulate cholesterol and blood sugar, paired with live probiotics for digestive balance.',
        'goal_benefits': {
            'bulk': 'Easily digestible carbohydrates and gut-healthy probiotics aid overall nutrient absorption.',
            'cut': 'Exceptionally low in calories while exceptionally high in filling fiber and volume.',
            'maintain': 'Promotes gut wellness, stable insulin levels, and sustained mental focus.',
            'strength': 'Supplies magnesium and complex carbs to fuel sustained workouts.',
            'fitness': 'Great heart-healthy breakfast that keeps digestive load light.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt (adds 8g extra protein)'},
            {'original': 'Rolled oats', 'alternative': 'Broken wheat (daliya) or quinoa'},
            {'original': 'Vegetables', 'alternative': 'Spinach, mushrooms, and zucchini'}
        ],
        'nutrition_tip': 'Savory masala oats are an easy way to enjoy the heart-health benefits of oats without added sugars or sweet syrups.'
    },

    'vegetable oats + eggs + curd': {
        'description': 'Savory vegetable-loaded oats combined with cooked eggs and probiotic curd for a balanced high-protein start.',
        'calories': 470,
        'protein': '26 g',
        'carbs': '54 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1/2 cup rolled oats',
            '1/2 cup finely chopped mixed vegetables',
            '2 whole eggs (boiled or poached)',
            '1/2 cup fresh plain curd',
            '1 tsp oil, cumin seeds, turmeric, and black pepper'
        ],
        'preparation_steps': [
            'Sauté cumin seeds and mixed vegetables in 1 tsp oil until fragrant and slightly tender.',
            'Add 1.5 cups water, salt, and turmeric, bring to a boil, then stir in oats and cook for 4 minutes.',
            'Poach or boil 2 eggs and season with freshly ground black pepper.',
            'Serve the savory vegetable oats hot with the seasoned eggs and cool curd on the side.'
        ],
        'why_this_meal': 'Provides a triple nutritional win: beta-glucan fiber, complete protein from eggs, and digestive probiotics from curd.',
        'goal_benefits': {
            'bulk': 'Clean fuel and high protein stimulate muscle protein synthesis without bloating.',
            'cut': 'High protein and high fiber maximize thermogenesis and suppress appetite through the morning.',
            'maintain': 'Maintains lean tissue while keeping daily digestion running smoothly.',
            'strength': 'Delivers essential choline, zinc, and sustained carbohydrates for lifting power.',
            'fitness': 'Supports cardiovascular fitness, muscular endurance, and digestive wellness.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '120g grilled paneer or seasoned tofu'},
            {'original': 'Curd', 'alternative': 'Unsweetened Greek yogurt'},
            {'original': 'Rolled oats', 'alternative': 'Steel cut oats or quinoa'}
        ],
        'nutrition_tip': 'Combining eggs with oats provides both soluble fiber and high biological value protein for optimal satiety.'
    },

    'vegetable omelette + whole-grain toast + fruit': {
        'description': 'Fluffy vegetable omelette packed with colorful produce, served with whole-grain toast and fresh seasonal fruit.',
        'calories': 460,
        'protein': '24 g',
        'carbs': '50 g',
        'fat': '17 g',
        'fiber': '7 g',
        'ingredients': [
            '2 whole eggs + 1 egg white',
            '1/2 cup finely chopped bell peppers, onions, spinach, and tomatoes',
            '2 slices 100% whole-grain bread',
            '1 cup fresh seasonal fruit (apple or papaya)',
            '1 tsp olive oil, salt, and black pepper'
        ],
        'preparation_steps': [
            'Whisk eggs in a bowl with chopped vegetables, a pinch of salt, and black pepper.',
            'Heat olive oil in a non-stick skillet and pour the egg-vegetable mixture, cooking on medium heat until set and golden.',
            'Toast whole-grain bread slices until crisp and golden.',
            'Serve the hot omelette with toasted bread and a refreshing side of sliced fruit.'
        ],
        'why_this_meal': 'Delivers complete protein, rich lutein, bioflavonoids, complex carbohydrates, and vitamin C for full-body revitalization.',
        'goal_benefits': {
            'bulk': 'Provides high-quality amino acids and clean carbohydrates to fuel muscle growth.',
            'cut': 'High volume and fiber provide intense satiety for very controlled calories.',
            'maintain': 'A gold-standard fitness breakfast that sustains energy and body composition.',
            'strength': 'Supplies choline, healthy fats, and potassium for optimal neuromuscular firing.',
            'fitness': 'A nutrient-dense foundation for morning workouts and active lifestyle demands.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu and chickpea flour vegetable scramble'},
            {'original': 'Whole-grain toast', 'alternative': 'Multigrain chapati or oats'},
            {'original': 'Fruit', 'alternative': 'Grapefruit or fresh berries'}
        ],
        'nutrition_tip': 'Adding spinach and bell peppers to your omelette boosts dietary vitamin C, iron, and magnesium.'
    },

    'vegetable poha + 2 eggs + fruit': {
        'description': 'Savory vegetable-loaded flattened rice paired with two cooked eggs and a portion of fresh seasonal fruit.',
        'calories': 470,
        'protein': '22 g',
        'carbs': '62 g',
        'fat': '14 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup flattened rice (poha, rinsed)',
            '1/2 cup diced carrots, green peas, and onions',
            '2 whole eggs (boiled or scrambled)',
            '1 cup fresh seasonal fruit slices (orange or apple)',
            '1 tsp oil, mustard seeds, curry leaves, turmeric, and lemon'
        ],
        'preparation_steps': [
            'Rinse poha gently in a sieve and set aside to soften.',
            'Sauté mustard seeds, curry leaves, onions, and vegetables in 1 tsp oil with turmeric and salt until tender.',
            'Add the softened poha, toss gently over low heat, and finish with a squeeze of fresh lemon juice.',
            'Prepare 2 eggs to your liking and serve with the warm poha and freshly sliced fruit.'
        ],
        'why_this_meal': 'Provides an ideal balance of easily digested carbohydrates, complete egg proteins, and antioxidant-rich produce.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy to restore glycogen alongside muscle-building amino acids.',
            'cut': 'High volume, rich fiber, and moderate calories keep you full during cutting.',
            'maintain': 'Maintains steady blood glucose and energy levels throughout the morning.',
            'strength': 'Provides essential iron and B-vitamins to support physical power output.',
            'fitness': 'Light, digestible, and energizing fuel for everyday fitness conditioning.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '100g paneer cubes or scrambled tofu'},
            {'original': 'White poha', 'alternative': 'Red poha for higher mineral density'},
            {'original': 'Fruit', 'alternative': 'Pomegranate seeds or guava'}
        ],
        'nutrition_tip': 'Cook poha with turmeric to utilize curcumin, a powerful natural anti-inflammatory agent.'
    },

    'vegetable upma + 2 eggs': {
        'description': 'Traditional savory semolina or broken wheat upma cooked with vegetables, served with 2 protein-rich eggs.',
        'calories': 430,
        'protein': '21 g',
        'carbs': '50 g',
        'fat': '15 g',
        'fiber': '6 g',
        'ingredients': [
            '1/2 cup roasted semolina (sooji) or roasted broken wheat (daliya)',
            '1/2 cup mixed vegetables (carrots, green peas, green beans)',
            '1 chopped onion, green chili, ginger, mustard seeds, curry leaves',
            '2 whole eggs (boiled or sunny-side up)',
            '1 tsp oil and fresh coriander'
        ],
        'preparation_steps': [
            'Heat 1 tsp oil, splutter mustard seeds, curry leaves, ginger, and sauté onions with mixed vegetables for 3 mins.',
            'Pour in 1.25 cups water and salt; bring to a rolling boil.',
            'Gradually pour roasted semolina while stirring continuously to prevent lumps, cover and cook on low for 2 minutes.',
            'Cook 2 eggs and serve hot alongside the aromatic vegetable upma.'
        ],
        'why_this_meal': 'Supplies sustained complex carbohydrates from roasted wheat, paired with complete egg protein and dietary vegetable fiber.',
        'goal_benefits': {
            'bulk': 'Provides clean carbohydrates and quality amino acids for efficient muscle building.',
            'cut': 'Low-fat preparation with high volume keeps caloric intake tightly controlled.',
            'maintain': 'Provides balanced, sustained morning energy and steady blood sugar.',
            'strength': 'Fuels intensive workouts with readily available glycogen and muscle repair nutrients.',
            'fitness': 'A light, easily digestible meal that fuels morning workouts and athletic routines.'
        },
        'substitutions': [
            {'original': 'Semolina upma', 'alternative': 'Broken wheat (daliya) upma or oats upma for higher fiber'},
            {'original': 'Eggs', 'alternative': '100g sautéed paneer or tofu'},
            {'original': 'Vegetables', 'alternative': 'Finely chopped spinach and bell peppers'}
        ],
        'nutrition_tip': 'Roast semolina beforehand without oil until aromatic to make it light, fluffy, and easier to digest.'
    },

    'vegetable upma + 2 eggs + curd': {
        'description': 'Savory roasted semolina and vegetable upma served with 2 cooked eggs and refreshing probiotic curd.',
        'calories': 490,
        'protein': '25 g',
        'carbs': '54 g',
        'fat': '17 g',
        'fiber': '6 g',
        'ingredients': [
            '1/2 cup roasted semolina or daliya',
            '1/2 cup mixed diced vegetables',
            '2 whole eggs (boiled or scrambled)',
            '1/2 cup fresh plain curd',
            '1 tsp oil, mustard seeds, curry leaves, ginger, and coriander'
        ],
        'preparation_steps': [
            'Sauté mustard seeds, curry leaves, ginger, onions, and vegetables in 1 tsp oil until tender.',
            'Add 1.25 cups water and salt, bring to a boil, then slowly whisk in roasted semolina.',
            'Cover and let steam on low heat for 2 minutes until fluffy.',
            'Boil or scramble 2 eggs, season with pepper, and plate with hot upma and cool curd.'
        ],
        'why_this_meal': 'A complete macronutrient profile combining complex grains, dual protein sources (egg + curd), and live probiotics.',
        'goal_benefits': {
            'bulk': 'Multi-protein blend provides rapid and sustained amino acid delivery to repairing muscles.',
            'cut': 'High protein and dietary fiber prevent hunger cravings while maintaining muscle mass.',
            'maintain': 'Provides steady metabolic energy and digestive support.',
            'strength': 'Supplies calcium, potassium, and amino acids for muscle contraction and power.',
            'fitness': 'Promotes gut microbiome health and sustained workout endurance.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '120g grilled paneer cubes'},
            {'original': 'Curd', 'alternative': 'Greek yogurt for higher protein'},
            {'original': 'Sooji upma', 'alternative': 'Quinoa upma'}
        ],
        'nutrition_tip': 'Fresh curd helps soothe the digestive tract and enhances calcium and mineral absorption.'
    },

    'vegetable upma + eggs + curd': {
        'description': 'A nutritious breakfast plate of vegetable-loaded upma, cooked eggs, and cool probiotic curd.',
        'calories': 480,
        'protein': '24 g',
        'carbs': '52 g',
        'fat': '16 g',
        'fiber': '6 g',
        'ingredients': [
            '1/2 cup roasted semolina (sooji)',
            '1/2 cup diced carrots, peas, and green beans',
            '2 whole eggs',
            '1/2 cup plain curd',
            '1 tsp oil, ginger, mustard seeds, curry leaves'
        ],
        'preparation_steps': [
            'Sauté ginger, mustard seeds, curry leaves, and vegetables in oil for 3 minutes.',
            'Add water and salt, bring to a boil, and stir in roasted semolina until cooked and fluffy.',
            'Prepare eggs to preference (boiled or poached) with black pepper.',
            'Serve the hot upma with the eggs and a bowl of fresh curd.'
        ],
        'why_this_meal': 'Combines wholesome carbohydrates, complete protein, and probiotic cultures for optimal digestion and sustained energy.',
        'goal_benefits': {
            'bulk': 'Quality fuel that supports glycogen recovery and muscle protein synthesis.',
            'cut': 'Promotes prolonged satiety while keeping total calories moderate.',
            'maintain': 'Maintains energy balance and metabolic health throughout the day.',
            'strength': 'Supplies essential B-vitamins and electrolytes to power resistance training.',
            'fitness': 'Light, wholesome, and energizing for daily physical activity.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Tofu scramble or paneer'},
            {'original': 'Curd', 'alternative': 'Unsweetened plant yogurt'},
            {'original': 'Sooji', 'alternative': 'Millet upma or oats upma'}
        ],
        'nutrition_tip': 'Include fresh ginger in the upma seasoning to stimulate digestive enzymes and reduce inflammation.'
    },

    'vegetable upma + eggs + curd + fruit': {
        'description': 'A vibrant and complete breakfast feast of vegetable upma, cooked eggs, probiotic curd, and fresh seasonal fruit.',
        'calories': 530,
        'protein': '25 g',
        'carbs': '66 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1/2 cup roasted semolina or daliya',
            '1/2 cup mixed vegetables',
            '2 whole eggs (boiled or poached)',
            '1/2 cup fresh curd',
            '1 cup fresh seasonal fruit slices (papaya, apple, or berries)',
            '1 tsp oil, mustard seeds, curry leaves, ginger'
        ],
        'preparation_steps': [
            'Cook vegetable upma by sautéing aromatics and veggies, adding water, and stirring in roasted semolina until fluffy.',
            'Boil or poach 2 eggs, then sprinkle with black pepper.',
            'Wash, slice, and prepare the fresh seasonal fruit.',
            'Plate the hot upma, fresh curd, cooked eggs, and fruit together for a complete breakfast.'
        ],
        'why_this_meal': 'An all-inclusive morning meal delivering complex carbs, dual proteins, probiotics, and rich fruit antioxidants.',
        'goal_benefits': {
            'bulk': 'Provides clean carbohydrates and micronutrients to power muscle building and heavy training sessions.',
            'cut': 'High volume and fiber ensure you stay full for hours while meeting all micronutrient requirements.',
            'maintain': 'A balanced, wholesome meal supporting sustained everyday energy and wellbeing.',
            'strength': 'Provides essential electrolytes, choline, and amino acids for peak strength recovery.',
            'fitness': 'Optimal full-spectrum nutrition for endurance, strength, and immune defense.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': '120g grilled tofu or paneer'},
            {'original': 'Semolina', 'alternative': 'Oats or broken wheat upma'},
            {'original': 'Fruit', 'alternative': 'Kiwi or orange wedges'}
        ],
        'nutrition_tip': 'Eating fresh fruit alongside fermented curd provides both prebiotic fiber and live probiotic bacteria for synergistic gut health.'
    },

    'whole-grain toast + vegetable omelette + fruit': {
        'description': 'A modern fitness breakfast featuring a fluffy vegetable omelette, hearty whole-grain toast, and fresh sliced fruit.',
        'calories': 450,
        'protein': '22 g',
        'carbs': '50 g',
        'fat': '18 g',
        'fiber': '7 g',
        'ingredients': [
            '2 slices whole-grain bread',
            '2 whole eggs + 1 egg white',
            '1/2 cup mixed vegetables (bell peppers, onions, spinach, mushrooms)',
            '1 cup seasonal fresh fruit (berries, apple, or papaya)',
            '1 tsp olive oil, salt, and black pepper'
        ],
        'preparation_steps': [
            'Whisk eggs with a pinch of salt, pepper, and finely chopped vegetables in a bowl.',
            'Heat olive oil in a non-stick pan and cook the omelette until fluffy, golden, and fully set.',
            'Toast the whole-grain bread slices until golden brown and crisp.',
            'Serve the warm omelette with crisp toast and freshly sliced seasonal fruit.'
        ],
        'why_this_meal': 'Combines high-biological-value protein with slow-burning complex carbohydrates and rich antioxidant vitamins.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Eggs', 'alternative': 'Paneer scramble (120g) or tofu scramble'},
            {'original': 'Whole-grain toast', 'alternative': 'Multigrain roti or rolled oats'},
            {'original': 'Seasonal fruit', 'alternative': 'Apple, banana, or guava'}
        ],
        'nutrition_tip': 'Keep added oil moderate when preparing the omelette to maintain clean nutritional quality.'
    },

    # -------------------------------------------------------------
    # MORNING & EVENING SNACKS (FRUIT, NUTS, YOGURT, CHANA, ETC.)
    # -------------------------------------------------------------
    'apple + greek yogurt': {
        'description': 'Crisp freshly sliced apple paired with thick, creamy, protein-dense Greek yogurt.',
        'calories': 220,
        'protein': '15 g',
        'carbs': '28 g',
        'fat': '3 g',
        'fiber': '4 g',
        'ingredients': [
            '1 medium crisp apple (sliced)',
            '150g plain unsweetened Greek yogurt',
            'Pinch of ground cinnamon'
        ],
        'preparation_steps': [
            'Wash, core, and slice a fresh crisp apple into wedges.',
            'Spoon chilled Greek yogurt into a snack bowl.',
            'Dust with a pinch of aromatic ground cinnamon.',
            'Dip apple slices into the yogurt or mix together and enjoy fresh.'
        ],
        'why_this_meal': 'Combines casein and whey proteins with pectin fiber from apple, offering high satiety with minimal calories.',
        'goal_benefits': {
            'bulk': 'Convenient clean protein boost between main meals to sustain muscle protein synthesis.',
            'cut': 'High protein density and fiber conquer hunger cravings during a calorie deficit.',
            'maintain': 'Provides steady midday energy without creating glucose spikes.',
            'strength': 'Supplies amino acids and calcium to support bone density and muscle contraction.',
            'fitness': 'Light, refreshing snack that supports metabolic rate and lean muscle tone.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Plain thick curd or cottage cheese'},
            {'original': 'Apple', 'alternative': 'Fresh pear or sliced strawberries'}
        ],
        'nutrition_tip': 'Keep the apple skin on to retain insoluble fiber and quercetin, a potent antioxidant.'
    },

    'apple + a small handful of almonds': {
        'description': 'Crisp juicy apple paired with nutrient-dense raw almonds for balanced energy.',
        'calories': 210,
        'protein': '5 g',
        'carbs': '25 g',
        'fat': '10 g',
        'fiber': '6 g',
        'ingredients': [
            '1 medium apple',
            '12–15 raw almonds (approx 15g)',
            'Pinch of cinnamon (optional)'
        ],
        'preparation_steps': [
            'Wash and slice the fresh apple into bite-sized pieces.',
            'Count a small handful (12–15) of raw almonds.',
            'Pair them together in a snack bowl and serve immediately.'
        ],
        'why_this_meal': 'The soluble fiber in apple slows down carbohydrate absorption while healthy fats in almonds stabilize blood sugar.',
        'goal_benefits': {
            'bulk': 'Provides clean calories and essential monounsaturated fats to support surplus energy.',
            'cut': 'Extremely filling snack that curbs sugar cravings with natural fruit sweetness and fiber.',
            'maintain': 'Maintains energy balance and healthy lipid profiles.',
            'strength': 'Supplies magnesium and vitamin E to aid muscle relaxation and reduce cellular stress.',
            'fitness': 'A portable, clean snack for active on-the-go lifestyles.'
        },
        'substitutions': [
            {'original': 'Almonds', 'alternative': 'Walnuts, pistachios, or roasted pumpkin seeds'},
            {'original': 'Apple', 'alternative': 'Guava, orange, or pear'}
        ],
        'nutrition_tip': 'Chewing almonds slowly increases nutrient release and promotes satiety signaling to the brain.'
    },

    'apple + almonds': {
        'description': 'A classic combination of fresh crisp apple and crunchy raw almonds.',
        'calories': 210,
        'protein': '5 g',
        'carbs': '25 g',
        'fat': '10 g',
        'fiber': '6 g',
        'ingredients': [
            '1 medium fresh apple',
            '15g raw almonds (about 12–15 nuts)'
        ],
        'preparation_steps': [
            'Rinse the apple thoroughly and slice into wedges.',
            'Portion out raw almonds.',
            'Enjoy as a crisp, crunchy, and energizing mid-meal snack.'
        ],
        'why_this_meal': 'Delivers natural energy from fruit paired with healthy fats and vitamin E from almonds.',
        'goal_benefits': {
            'bulk': 'Supplies micronutrients and healthy fats that support metabolic function.',
            'cut': 'Low calorie density and high fiber prevent between-meal overeating.',
            'maintain': 'Keeps blood sugar stable and satisfies sweet cravings naturally.',
            'strength': 'Magnesium content in almonds supports muscle recovery and nerve signaling.',
            'fitness': 'Wholesome whole-food snack that fuels daily physical activity.'
        },
        'substitutions': [
            {'original': 'Almonds', 'alternative': 'Walnuts or sunflower seeds'},
            {'original': 'Apple', 'alternative': 'Pear or seasonal berries'}
        ],
        'nutrition_tip': 'Pairing fruit with nuts lowers the overall glycemic response of the snack.'
    },

    'apple + curd': {
        'description': 'Crisp sliced apple paired with a bowl of cooling, probiotic-rich fresh curd.',
        'calories': 180,
        'protein': '7 g',
        'carbs': '26 g',
        'fat': '4 g',
        'fiber': '4 g',
        'ingredients': [
            '1 medium apple (diced)',
            '150g fresh plain curd',
            'Pinch of roasted cumin or cinnamon'
        ],
        'preparation_steps': [
            'Wash and dice the apple into small bite-sized pieces.',
            'Pour fresh cool curd into a bowl and lightly whisk.',
            'Top the curd with the diced apple and dust with cinnamon or roasted cumin.'
        ],
        'why_this_meal': 'Supplies digestive enzymes and prebiotic fibers from apple alongside live active probiotics from curd.',
        'goal_benefits': {
            'bulk': 'Digestive enzymes and probiotics improve overall meal assimilation.',
            'cut': 'Low-calorie, highly filling snack that supports a healthy gut during a caloric deficit.',
            'maintain': 'Promotes gut harmony and steady energy.',
            'strength': 'Supplies calcium and easy-to-absorb whey/casein proteins.',
            'fitness': 'Hydrating, gut-friendly snack that boosts digestive health.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt or kefir'},
            {'original': 'Apple', 'alternative': 'Pomegranate seeds or sliced banana'}
        ],
        'nutrition_tip': 'Avoid adding sugar; let the natural sweetness of the ripe apple flavor the curd.'
    },

    'apple + small handful of nuts': {
        'description': 'A crisp fresh apple served with a balanced portion of mixed raw nuts.',
        'calories': 220,
        'protein': '5 g',
        'carbs': '25 g',
        'fat': '12 g',
        'fiber': '6 g',
        'ingredients': [
            '1 fresh apple',
            '15g mixed raw nuts (walnuts, almonds, cashews)'
        ],
        'preparation_steps': [
            'Slice the apple into thin wedges.',
            'Measure a small handful of mixed nuts.',
            'Serve together for a balanced, crunchy snack.'
        ],
        'why_this_meal': 'Provides a broad spectrum of fatty acids (omega-3s and monounsaturated fats) and fiber.',
        'goal_benefits': {
            'bulk': 'Calorie-dense healthy fats support sustained energy.',
            'cut': 'High satiety helps suppress appetite between main meals.',
            'maintain': 'Maintains cardiovascular health and steady energy.',
            'strength': 'Anti-inflammatory fats aid joint and tissue recovery.',
            'fitness': 'Clean whole-food energy on the go.'
        },
        'substitutions': [
            {'original': 'Mixed nuts', 'alternative': 'Pumpkin seeds or roasted chana'},
            {'original': 'Apple', 'alternative': 'Guava or orange'}
        ],
        'nutrition_tip': 'Opt for unroasted, unsalted nuts to avoid excess sodium and oxidized oils.'
    },

    'banana + greek yogurt + walnuts': {
        'description': 'Creamy Greek yogurt topped with naturally sweet banana slices and omega-3 rich crunchy walnuts.',
        'calories': 310,
        'protein': '18 g',
        'carbs': '38 g',
        'fat': '11 g',
        'fiber': '4 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '1 medium ripe banana (sliced)',
            '15g raw walnut halves (crushed)',
            'Pinch of cinnamon'
        ],
        'preparation_steps': [
            'Spoon creamy Greek yogurt into a bowl.',
            'Slice the banana into rounds and arrange over the yogurt.',
            'Roughly chop walnuts and sprinkle on top with a dash of cinnamon.',
            'Serve immediately as an energizing snack.'
        ],
        'why_this_meal': 'Supplies high-quality protein, potassium for muscle recovery, and anti-inflammatory plant omega-3 fatty acids.',
        'goal_benefits': {
            'bulk': 'An ideal calorie-dense, protein-rich snack that accelerates recovery between workouts.',
            'cut': 'High protein and healthy fats provide deep satiety, preventing overeating at dinner.',
            'maintain': 'Balanced macronutrients that support brain function and athletic vitality.',
            'strength': 'Walnuts and Greek yogurt provide essential minerals for joint and muscle recovery.',
            'fitness': 'Optimal post-workout snack providing immediate glycogen reload and protein synthesis.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Thick hung curd or cottage cheese'},
            {'original': 'Walnuts', 'alternative': 'Almonds or chia seeds'},
            {'original': 'Banana', 'alternative': 'Fresh blueberries or mango slices'}
        ],
        'nutrition_tip': 'Walnuts are one of the richest plant sources of ALA omega-3, which aids in reducing exercise-induced inflammation.'
    },

    'banana + curd': {
        'description': 'A simple, soothing combination of sweet sliced banana and cool fresh probiotic curd.',
        'calories': 200,
        'protein': '7 g',
        'carbs': '35 g',
        'fat': '4 g',
        'fiber': '3 g',
        'ingredients': [
            '1 medium ripe banana',
            '150g fresh plain curd',
            'Pinch of ground cardamom'
        ],
        'preparation_steps': [
            'Peel and slice a ripe banana into a bowl.',
            'Pour fresh plain curd over the banana slices.',
            'Add a subtle pinch of cardamom powder for flavor and mix gently.'
        ],
        'why_this_meal': 'Banana acts as a prebiotic providing inulin and resistant starch that feeds the live probiotics in curd.',
        'goal_benefits': {
            'bulk': 'Clean, easily digested calories that help meet surplus requirements effortlessly.',
            'cut': 'Satisfies sweet cravings naturally while supplying gut-healthy probiotics.',
            'maintain': 'Provides quick, steady energy and digestive comfort.',
            'strength': 'Potassium in banana prevents muscle cramps during intensive training.',
            'fitness': 'Great pre-workout snack 45 minutes prior to training.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt for double the protein'},
            {'original': 'Banana', 'alternative': 'Papaya or mango cubes'}
        ],
        'nutrition_tip': 'Eat slightly under-ripe bananas if you want more resistant starch for gut health and lower glycemic impact.'
    },

    'banana + curd + a few nuts': {
        'description': 'Fresh sliced banana and cool curd topped with a crunchy garnish of raw chopped nuts.',
        'calories': 250,
        'protein': '8 g',
        'carbs': '36 g',
        'fat': '8 g',
        'fiber': '4 g',
        'ingredients': [
            '1 ripe banana',
            '150g fresh curd',
            '10g chopped almonds and walnuts'
        ],
        'preparation_steps': [
            'Slice the banana into a bowl of fresh curd.',
            'Chop nuts finely and scatter over the top.',
            'Serve chilled.'
        ],
        'why_this_meal': 'Combines prebiotics, probiotics, healthy fats, and potassium for optimal cellular hydration and gut flora.',
        'goal_benefits': {
            'bulk': 'A dense snack that fuels high-energy demands and muscle repair.',
            'cut': 'Healthy fats and protein extend satiety from the fruit.',
            'maintain': 'Maintains energy balance and cognitive focus throughout the afternoon.',
            'strength': 'Electrolytes and healthy fats support nervous system endurance.',
            'fitness': 'Wholesome natural snack that supports training readiness.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt'},
            {'original': 'Nuts', 'alternative': 'Pumpkin seeds or chia seeds'}
        ],
        'nutrition_tip': 'Cardamom or cinnamon added to this snack improves digestive fire and aroma.'
    },

    'banana + peanut butter': {
        'description': 'Thick creamy natural peanut butter paired with sliced ripe banana for quick energy.',
        'calories': 280,
        'protein': '8 g',
        'carbs': '34 g',
        'fat': '14 g',
        'fiber': '5 g',
        'ingredients': [
            '1 medium ripe banana',
            '1.5 tbsp natural peanut butter (approx 25g)'
        ],
        'preparation_steps': [
            'Peel and slice the banana in half lengthwise or into discs.',
            'Spread or dip with creamy natural peanut butter.',
            'Enjoy immediately before or after training.'
        ],
        'why_this_meal': 'Fast-acting potassium and carbs from banana combine with sustained fats and plant protein from peanuts.',
        'goal_benefits': {
            'bulk': 'An exceptional high-calorie snack to hit calorie surplus targets cleanly.',
            'cut': 'Portion-control the peanut butter (1 tbsp) for a deeply satisfying treat that kills cravings.',
            'maintain': 'Provides sustained physical energy without refined sugar crashes.',
            'strength': 'Great pre-workout fuel for heavy lifting sessions.',
            'fitness': 'Quick, portable snack for athletes and active individuals.'
        },
        'substitutions': [
            {'original': 'Peanut butter', 'alternative': 'Almond butter or sunflower seed butter'},
            {'original': 'Banana', 'alternative': 'Apple slices or celery sticks'}
        ],
        'nutrition_tip': 'Choose peanut butter with single-ingredient labeling (peanuts only) without added hydrogenated oils.'
    },

    'banana + peanuts': {
        'description': 'A whole-food snack pairing a sweet ripe banana with a handful of crunchy roasted peanuts.',
        'calories': 260,
        'protein': '8 g',
        'carbs': '33 g',
        'fat': '12 g',
        'fiber': '5 g',
        'ingredients': [
            '1 ripe banana',
            '20g roasted unsalted peanuts'
        ],
        'preparation_steps': [
            'Peel a fresh ripe banana.',
            'Measure a handful of roasted peanuts.',
            'Enjoy together as an authentic, energizing snack.'
        ],
        'why_this_meal': 'Supplies quick glycogen replenishment from banana and sustained amino acids and fats from peanuts.',
        'goal_benefits': {
            'bulk': 'Easily portable clean calories that support daily energy surplus.',
            'cut': 'The chewing satisfaction of whole peanuts improves satiety compared to peanut butter.',
            'maintain': 'Maintains active stamina and blood sugar equilibrium.',
            'strength': 'Provides arginine and potassium for muscle pumps and recovery.',
            'fitness': 'Simple, natural whole foods that power workout performance.'
        },
        'substitutions': [
            {'original': 'Peanuts', 'alternative': 'Roasted almonds or walnuts'},
            {'original': 'Banana', 'alternative': 'Guava or apple'}
        ],
        'nutrition_tip': 'Roasted peanuts with skin on contain extra polyphenol antioxidants comparable to berries.'
    },

    'curd + almonds + seasonal fruit': {
        'description': 'Cool probiotic curd topped with sliced seasonal fruits and crunchy raw almonds.',
        'calories': 240,
        'protein': '9 g',
        'carbs': '28 g',
        'fat': '10 g',
        'fiber': '5 g',
        'ingredients': [
            '150g fresh plain curd',
            '1 cup diced seasonal fruit (pomegranate, papaya, or apple)',
            '10–12 raw almonds (sliced)'
        ],
        'preparation_steps': [
            'Spoon fresh curd into a serving bowl.',
            'Wash and dice seasonal fruit and layer over the curd.',
            'Chop raw almonds and sprinkle over the bowl for crunch.'
        ],
        'why_this_meal': 'Supplies a synergistic mix of live probiotics, prebiotic fruit fibers, and vitamin E-rich healthy fats.',
        'goal_benefits': {
            'bulk': 'Provides clean micronutrients and protein to support digestion and muscle building.',
            'cut': 'High volume and low calorie density make this an ideal fat-loss snack.',
            'maintain': 'Promotes gut health, cellular hydration, and steady energy.',
            'strength': 'Supplies calcium and magnesium to support muscular contractions.',
            'fitness': 'Refreshing, nutrient-dense snack that keeps energy high.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt'},
            {'original': 'Almonds', 'alternative': 'Walnuts or pistachios'},
            {'original': 'Seasonal fruit', 'alternative': 'Mixed berries or kiwi'}
        ],
        'nutrition_tip': 'Pomegranate seeds add punicalagins, which support vascular health and blood flow.'
    },

    'curd + fruit + almonds': {
        'description': 'A nutrient-rich bowl of probiotic curd, diced mixed fruit, and sliced raw almonds.',
        'calories': 240,
        'protein': '9 g',
        'carbs': '28 g',
        'fat': '10 g',
        'fiber': '5 g',
        'ingredients': [
            '150g fresh curd',
            '1 cup mixed fresh fruit',
            '15g raw almonds'
        ],
        'preparation_steps': [
            'Add fresh curd to a bowl.',
            'Dice mixed fruit and top the curd.',
            'Garnish with sliced raw almonds and serve.'
        ],
        'why_this_meal': 'Balances proteins, healthy fats, and carbohydrates while supporting the gut microbiome.',
        'goal_benefits': {
            'bulk': 'Nutrient-rich snack that aids meal assimilation and muscle recovery.',
            'cut': 'Controls appetite effectively while providing essential vitamins.',
            'maintain': 'Supports daily nutritional equilibrium and sustained energy.',
            'strength': 'Provides essential minerals that support skeletal and muscular health.',
            'fitness': 'Light, refreshing, and rich in natural antioxidants.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt'},
            {'original': 'Almonds', 'alternative': 'Pumpkin seeds or walnuts'}
        ],
        'nutrition_tip': 'Opt for homemade curd when possible for maximum live lactic acid bacteria.'
    },

    'curd + mixed nuts': {
        'description': 'A satisfying snack of thick probiotic curd garnished with an assortment of crunchy raw nuts.',
        'calories': 250,
        'protein': '10 g',
        'carbs': '14 g',
        'fat': '16 g',
        'fiber': '3 g',
        'ingredients': [
            '150g fresh plain curd',
            '20g mixed raw nuts (almonds, walnuts, pistachios)',
            'Pinch of roasted cumin powder'
        ],
        'preparation_steps': [
            'Whisk fresh curd in a bowl until smooth.',
            'Roughly chop the mixed nuts.',
            'Scatter nuts over the curd and dust with roasted cumin powder.'
        ],
        'why_this_meal': 'High in healthy monounsaturated and polyunsaturated fats, bioavailable calcium, and complete milk proteins.',
        'goal_benefits': {
            'bulk': 'Concentrated clean calories and healthy fats to support bulking.',
            'cut': 'Low carbohydrate content keeps insulin levels low and fat burning elevated.',
            'maintain': 'Provides stable, long-lasting energy without hunger spikes.',
            'strength': 'Supplies zinc, magnesium, and calcium for muscular and hormonal recovery.',
            'fitness': 'Promotes brain function, cardiovascular health, and lean body mass.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt or cottage cheese'},
            {'original': 'Mixed nuts', 'alternative': 'Hemp seeds, chia seeds, and sunflower seeds'}
        ],
        'nutrition_tip': 'This low-glycemic snack is ideal in the late afternoon to keep hunger suppressed until dinner.'
    },

    'fruit + curd': {
        'description': 'A refreshing bowl of seasonal diced fruit served in a pool of fresh probiotic curd.',
        'calories': 180,
        'protein': '7 g',
        'carbs': '30 g',
        'fat': '4 g',
        'fiber': '4 g',
        'ingredients': [
            '1.5 cups diced mixed fresh seasonal fruit (papaya, melon, apple)',
            '150g fresh plain curd'
        ],
        'preparation_steps': [
            'Chop fresh fruits into bite-sized pieces.',
            'Place into a bowl and pour fresh chilled curd on top.',
            'Mix gently and enjoy.'
        ],
        'why_this_meal': 'Supplies rapid hydration, natural fruit vitamins, and digestive probiotics in an easy-to-digest snack.',
        'goal_benefits': {
            'bulk': 'Hydrating, clean fuel that boosts digestive efficiency.',
            'cut': 'Very low calorie density allows for a large satisfying portion.',
            'maintain': 'Provides steady hydration, fiber, and vitamins.',
            'strength': 'Restores cellular electrolytes and glycogen post-workout.',
            'fitness': 'Promotes digestive lightness and sustained workout performance.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt'},
            {'original': 'Mixed fruit', 'alternative': 'Berries or pomegranate'}
        ],
        'nutrition_tip': 'Papaya contains papain, a natural enzyme that assists in breaking down protein from your meals.'
    },

    'fruit + a small handful of nuts': {
        'description': 'Fresh seasonal fruit accompanied by a controlled portion of raw crunchy nuts.',
        'calories': 220,
        'protein': '5 g',
        'carbs': '26 g',
        'fat': '12 g',
        'fiber': '5 g',
        'ingredients': [
            '1 medium piece of fruit (orange, apple, or guava)',
            '15g mixed raw nuts (almonds, walnuts)'
        ],
        'preparation_steps': [
            'Wash and peel or slice the fresh fruit.',
            'Count a small handful (15g) of raw nuts.',
            'Serve together for an afternoon energy boost.'
        ],
        'why_this_meal': 'The healthy fats from the nuts slow carbohydrate digestion, providing steady, long-lasting energy.',
        'goal_benefits': {
            'bulk': 'Clean healthy calories to keep metabolism fueled between workouts.',
            'cut': 'Prevents mid-afternoon energy crashes and binge eating.',
            'maintain': 'Maintains energy balance and cognitive vitality.',
            'strength': 'Supplies essential fatty acids and antioxidants for joint health.',
            'fitness': 'A whole-food snack that supports cardio and strength endurance.'
        },
        'substitutions': [
            {'original': 'Nuts', 'alternative': 'Roasted pumpkin seeds or roasted chana'},
            {'original': 'Fruit', 'alternative': 'Seasonal pear or berries'}
        ],
        'nutrition_tip': 'Pairing vitamin C-rich fruits with nuts boosts the antioxidant defense of cell membranes.'
    },

    'fruit + mixed nuts': {
        'description': 'An invigorating whole-food snack combining fresh seasonal fruit with assorted mixed nuts.',
        'calories': 230,
        'protein': '6 g',
        'carbs': '26 g',
        'fat': '13 g',
        'fiber': '5 g',
        'ingredients': [
            '1 cup fresh fruit',
            '20g mixed nuts (almonds, cashews, walnuts)'
        ],
        'preparation_steps': [
            'Prepare fresh fruit and place in a snack dish.',
            'Add the raw mixed nuts alongside.',
            'Enjoy fresh.'
        ],
        'why_this_meal': 'Supplies a diverse array of vitamins, minerals, phytonutrients, and healthy fats.',
        'goal_benefits': {
            'bulk': 'Clean fuel for muscle recovery and surplus energy.',
            'cut': 'Curbs hunger effectively with low glycemic impact.',
            'maintain': 'Supports daily cardiovascular and cognitive wellness.',
            'strength': 'Delivers magnesium and selenium for antioxidant enzyme activity.',
            'fitness': 'Natural, energizing snack for active lifestyles.'
        },
        'substitutions': [
            {'original': 'Mixed nuts', 'alternative': 'Sunflower and pumpkin seed mix'},
            {'original': 'Fruit', 'alternative': 'Banana or sliced guava'}
        ],
        'nutrition_tip': 'Vary the nuts you eat through the week to benefit from diverse trace minerals like selenium and copper.'
    },

    'fruit + small handful of peanuts': {
        'description': 'Juicy fresh seasonal fruit paired with a small handful of roasted peanuts.',
        'calories': 200,
        'protein': '6 g',
        'carbs': '24 g',
        'fat': '10 g',
        'fiber': '5 g',
        'ingredients': [
            '1 piece seasonal fruit (guava or apple)',
            '15g roasted unsalted peanuts'
        ],
        'preparation_steps': [
            'Slice the fruit into wedges.',
            'Portion out roasted peanuts.',
            'Serve together for a balanced snack.'
        ],
        'why_this_meal': 'Provides plant protein, resveratrol, and healthy fats to balance natural fruit sugars.',
        'goal_benefits': {
            'bulk': 'Nutrient-dense clean snack to support energy needs.',
            'cut': 'Very satisfying crunch and fiber with minimal calories.',
            'maintain': 'Keeps blood sugar stable and satisfies cravings.',
            'strength': 'Supplies arginine for nitric oxide and healthy blood flow.',
            'fitness': 'Light, portable snack for afternoon energy.'
        },
        'substitutions': [
            {'original': 'Peanuts', 'alternative': 'Roasted chana or almonds'},
            {'original': 'Fruit', 'alternative': 'Orange or papaya'}
        ],
        'nutrition_tip': 'Peanuts are a legume rather than a tree nut, making them especially rich in folate and plant protein.'
    },

    'greek yogurt + almonds': {
        'description': 'Thick high-protein Greek yogurt topped with crunchy whole raw almonds.',
        'calories': 230,
        'protein': '17 g',
        'carbs': '10 g',
        'fat': '13 g',
        'fiber': '3 g',
        'ingredients': [
            '150g plain unsweetened Greek yogurt',
            '15g raw almonds (chopped)',
            'Dash of vanilla extract or cinnamon'
        ],
        'preparation_steps': [
            'Spoon Greek yogurt into a small bowl.',
            'Roughly chop the raw almonds.',
            'Scatter over the yogurt with a sprinkle of cinnamon and enjoy.'
        ],
        'why_this_meal': 'Offers high-density protein with very low carbohydrate content and heart-healthy monounsaturated fats.',
        'goal_benefits': {
            'bulk': 'Sustains muscle protein synthesis between major meals.',
            'cut': 'High protein-to-calorie ratio keeps you in a fat-burning state while maintaining fullness.',
            'maintain': 'Maintains lean body mass and steady insulin levels.',
            'strength': 'Supplies slow-release casein protein to support overnight or long-interval recovery.',
            'fitness': 'Promotes lean muscle tone and healthy metabolism.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Low-fat cottage cheese (paneer) or hung curd'},
            {'original': 'Almonds', 'alternative': 'Walnuts or pistachios'}
        ],
        'nutrition_tip': 'Greek yogurt contains nearly double the protein of standard yogurt due to the whey-straining process.'
    },

    'greek yogurt + banana': {
        'description': 'Creamy protein-dense Greek yogurt served with sliced ripe banana.',
        'calories': 230,
        'protein': '16 g',
        'carbs': '35 g',
        'fat': '3 g',
        'fiber': '3 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '1 medium ripe banana (sliced)',
            'Pinch of cinnamon'
        ],
        'preparation_steps': [
            'Place Greek yogurt in a bowl.',
            'Slice the banana into rounds and arrange on top.',
            'Dust with cinnamon and serve chilled.'
        ],
        'why_this_meal': 'Supplies fast-acting carbohydrates and high-quality protein for post-workout muscle glycogen and repair.',
        'goal_benefits': {
            'bulk': 'Accelerates recovery and glycogen reloading after heavy workouts.',
            'cut': 'Satisfies sweet tooth naturally while hitting high protein targets.',
            'maintain': 'Provides sustained afternoon energy and muscle support.',
            'strength': 'Potassium in banana supports muscle recovery and prevents cramping.',
            'fitness': 'Optimal post-training snack for muscular recovery and energy.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Thick fresh curd'},
            {'original': 'Banana', 'alternative': 'Fresh blueberries or mango cubes'}
        ],
        'nutrition_tip': 'Greek yogurt and banana create an ideal 2:1 carb-to-protein ratio for rapid post-workout recovery.'
    },

    'greek yogurt + banana + nuts': {
        'description': 'A high-protein bowl of thick Greek yogurt, sweet sliced banana, and crunchy mixed nuts.',
        'calories': 300,
        'protein': '18 g',
        'carbs': '36 g',
        'fat': '10 g',
        'fiber': '4 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '1 medium banana',
            '15g mixed raw nuts (almonds, walnuts)'
        ],
        'preparation_steps': [
            'Transfer Greek yogurt to a bowl.',
            'Slice banana on top.',
            'Chop nuts and sprinkle over the bowl before serving.'
        ],
        'why_this_meal': 'Combines premium dairy protein, electrolyte-rich fruit, and anti-inflammatory healthy fats.',
        'goal_benefits': {
            'bulk': 'Calorie-dense, high-protein snack that drives muscle growth and recovery.',
            'cut': 'High satiety index keeps appetite completely satisfied for hours.',
            'maintain': 'Supports lean body mass and cognitive sharpness.',
            'strength': 'Provides essential amino acids and minerals for power development.',
            'fitness': 'Complete whole-food fuel for athletic conditioning.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Hung curd or cottage cheese'},
            {'original': 'Mixed nuts', 'alternative': 'Pumpkin seeds or chia seeds'}
        ],
        'nutrition_tip': 'Sprinkle a pinch of chia seeds for an added boost of soluble fiber and plant omega-3s.'
    },

    'greek yogurt + banana + walnuts': {
        'description': 'Creamy Greek yogurt topped with ripe banana slices and crunchy omega-3 rich walnuts.',
        'calories': 310,
        'protein': '18 g',
        'carbs': '38 g',
        'fat': '11 g',
        'fiber': '4 g',
        'ingredients': [
            '150g Greek yogurt',
            '1 banana',
            '15g raw walnut halves'
        ],
        'preparation_steps': [
            'Spoon Greek yogurt into a bowl.',
            'Layer with sliced banana and crushed walnuts.',
            'Dust with cinnamon and serve.'
        ],
        'why_this_meal': 'Rich in complete proteins, potassium, and neuroprotective alpha-linolenic acid (ALA).',
        'goal_benefits': {
            'bulk': 'An exceptional bulking snack that supports muscle recovery without refined sugar.',
            'cut': 'Provides long-lasting fullness and controls evening cravings.',
            'maintain': 'Maintains cardiovascular and muscular health.',
            'strength': 'Supplies essential fatty acids that reduce joint stiffness and soreness.',
            'fitness': 'Optimal fuel for endurance recovery and lean muscle preservation.'
        },
        'substitutions': [
            {'original': 'Walnuts', 'alternative': 'Pecans, almonds, or flaxseeds'},
            {'original': 'Greek yogurt', 'alternative': 'Thick plain curd'}
        ],
        'nutrition_tip': 'Walnuts contain the highest antioxidant activity of any common nut, aiding post-workout recovery.'
    },

    'greek yogurt + fruit': {
        'description': 'Thick Greek yogurt paired with colorful fresh seasonal fruit.',
        'calories': 200,
        'protein': '15 g',
        'carbs': '26 g',
        'fat': '3 g',
        'fiber': '4 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '1 cup fresh mixed fruit (berries, apple, or papaya)'
        ],
        'preparation_steps': [
            'Add Greek yogurt to a snack dish.',
            'Top with freshly washed and diced fruit.',
            'Serve chilled.'
        ],
        'why_this_meal': 'High protein density coupled with antioxidant vitamins and prebiotic fibers.',
        'goal_benefits': {
            'bulk': 'Light, refreshing protein boost between main training meals.',
            'cut': 'High satiety with minimal calorie impact; perfect for cutting.',
            'maintain': 'Provides steady daily vitality and digestive balance.',
            'strength': 'Delivers calcium and amino acids for muscle tissue preservation.',
            'fitness': 'Supports lean body composition and cellular immunity.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Thick curd or kefir'},
            {'original': 'Fruit', 'alternative': 'Blueberries, strawberries, or kiwi'}
        ],
        'nutrition_tip': 'Choose unflavored Greek yogurt to avoid the 15–20g of added refined sugars found in fruit-flavored yogurts.'
    },

    'greek yogurt + mixed fruit': {
        'description': 'A vibrant parfait of thick Greek yogurt layered with an assortment of fresh diced fruits.',
        'calories': 210,
        'protein': '15 g',
        'carbs': '28 g',
        'fat': '3 g',
        'fiber': '4 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '1 cup mixed diced fruits (kiwi, berries, pomegranate, apple)'
        ],
        'preparation_steps': [
            'Spoon half the Greek yogurt into a glass or bowl.',
            'Layer with half the mixed fruit.',
            'Add remaining yogurt and top with remaining fresh fruit.'
        ],
        'why_this_meal': 'Supplies a spectrum of antioxidants, vitamin C, and complete bioavailable dairy protein.',
        'goal_benefits': {
            'bulk': 'Provides vital micronutrients that support high-intensity workout performance.',
            'cut': 'High volume and high protein make it a top-tier cutting snack.',
            'maintain': 'Maintains metabolic health and radiant energy.',
            'strength': 'Supports immune health during periods of heavy training stress.',
            'fitness': 'Hydrating, protein-rich snack that fuels daily active routines.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Thick curd or quark'},
            {'original': 'Mixed fruit', 'alternative': 'Papaya and pineapple cubes'}
        ],
        'nutrition_tip': 'Adding pomegranate seeds adds anthocyanins, which improve blood flow and vascular elasticity.'
    },

    'greek yogurt + nuts': {
        'description': 'Thick protein-packed Greek yogurt topped with a blend of raw crunchy nuts.',
        'calories': 250,
        'protein': '17 g',
        'carbs': '12 g',
        'fat': '15 g',
        'fiber': '3 g',
        'ingredients': [
            '150g plain Greek yogurt',
            '20g mixed raw nuts (almonds, walnuts, pistachios)'
        ],
        'preparation_steps': [
            'Portion Greek yogurt into a bowl.',
            'Chop nuts and scatter over the top.',
            'Serve immediately.'
        ],
        'why_this_meal': 'High in healthy monounsaturated and polyunsaturated fats, low in carbohydrates, and rich in protein.',
        'goal_benefits': {
            'bulk': 'Clean calorie density that supports muscle growth without bloating.',
            'cut': 'Extremely low glycemic response supports continuous fat oxidation.',
            'maintain': 'Maintains energy balance and sharp cognitive performance.',
            'strength': 'Provides essential minerals (zinc, magnesium) to support recovery.',
            'fitness': 'Supports lean muscle tone and cardiovascular wellness.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Cottage cheese or hung curd'},
            {'original': 'Nuts', 'alternative': 'Pumpkin and sunflower seeds'}
        ],
        'nutrition_tip': 'Eat this snack before bedtime if you want a steady release of amino acids during sleep.'
    },

    'greek yogurt + seasonal fruit': {
        'description': 'Cool Greek yogurt paired with the best seasonal fresh fruits of the day.',
        'calories': 200,
        'protein': '15 g',
        'carbs': '26 g',
        'fat': '3 g',
        'fiber': '4 g',
        'ingredients': [
            '150g Greek yogurt',
            '1 cup fresh seasonal fruit slices'
        ],
        'preparation_steps': [
            'Place Greek yogurt in a bowl.',
            'Top with seasonal fresh fruit.',
            'Serve chilled.'
        ],
        'why_this_meal': 'Delivers quality protein, live cultures, and peak-freshness seasonal antioxidants.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and amino acids to support lean muscle building.',
            'cut': 'High protein and dietary fiber keep you full and satisfied.',
            'maintain': 'Maintains steady blood glucose and lean body composition.',
            'strength': 'Replenishes glycogen and provides leucine for muscle protein synthesis.',
            'fitness': 'Promotes all-around wellness, stamina, and workout recovery.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Plain thick curd'},
            {'original': 'Seasonal fruit', 'alternative': 'Berries, apple, or papaya'}
        ],
        'nutrition_tip': 'Eating seasonal fruits guarantees higher vitamin C and polyphenol levels than out-of-season produce.'
    },

    'guava + greek yogurt': {
        'description': 'Vitamin C-rich fresh guava slices paired with thick high-protein Greek yogurt.',
        'calories': 200,
        'protein': '16 g',
        'carbs': '24 g',
        'fat': '3 g',
        'fiber': '6 g',
        'ingredients': [
            '1 medium ripe guava (sliced)',
            '150g plain Greek yogurt',
            'Pinch of rock salt and black pepper or cinnamon'
        ],
        'preparation_steps': [
            'Wash and slice the guava into thin wedges.',
            'Serve alongside a bowl of thick Greek yogurt.',
            'Sprinkle lightly with a pinch of rock salt and pepper or cinnamon.'
        ],
        'why_this_meal': 'Guava has more than 4 times the vitamin C of oranges and exceptionally high fiber, complementing Greek yogurt perfectly.',
        'goal_benefits': {
            'bulk': 'High antioxidant intake reduces exercise-induced muscle damage and speeds recovery.',
            'cut': 'Extraordinary fiber content (6g) makes this one of the most satiating low-calorie snacks available.',
            'maintain': 'Supports peak immune function and digestive regularity.',
            'strength': 'Vitamin C aids collagen synthesis for strong tendons and ligaments.',
            'fitness': 'Boosts cardiovascular health, immune defense, and lean muscle maintenance.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Thick plain curd'},
            {'original': 'Guava', 'alternative': 'Kiwi or green apple'}
        ],
        'nutrition_tip': 'Guava is one of the highest fiber fruits in existence, with over 5g of fiber per 100g serving.'
    },

    'guava + a small handful of almonds': {
        'description': 'Fresh guava wedges served with raw crunchy almonds.',
        'calories': 190,
        'protein': '5 g',
        'carbs': '20 g',
        'fat': '10 g',
        'fiber': '8 g',
        'ingredients': [
            '1 medium fresh guava',
            '12–15 raw almonds (15g)',
            'Pinch of chaat masala (optional)'
        ],
        'preparation_steps': [
            'Slice guava into wedges.',
            'Portion out raw almonds.',
            'Dust guava with a touch of chaat masala if desired and serve.'
        ],
        'why_this_meal': 'A fiber powerhouse delivering 8g of total dietary fiber, vitamin C, and healthy monounsaturated fats.',
        'goal_benefits': {
            'bulk': 'Supplies micronutrients and healthy fats to support active metabolism.',
            'cut': 'Incredible satiety-to-calorie ratio suppresses hunger for hours.',
            'maintain': 'Maintains healthy digestion and balanced cholesterol levels.',
            'strength': 'Protects connective tissues with collagen-boosting vitamin C and zinc.',
            'fitness': 'Light, super-clean snack for endurance and energy.'
        },
        'substitutions': [
            {'original': 'Almonds', 'alternative': 'Walnuts or roasted peanuts'},
            {'original': 'Guava', 'alternative': 'Apple or pear'}
        ],
        'nutrition_tip': 'Eat the edible soft seeds of the guava for maximum insoluble dietary fiber.'
    },

    'guava + a small handful of peanuts': {
        'description': 'Juicy fresh guava wedges paired with crunchy roasted peanuts.',
        'calories': 180,
        'protein': '6 g',
        'carbs': '18 g',
        'fat': '10 g',
        'fiber': '7 g',
        'ingredients': [
            '1 medium guava',
            '15g roasted peanuts'
        ],
        'preparation_steps': [
            'Slice the fresh guava.',
            'Serve with roasted peanuts.',
            'Enjoy fresh.'
        ],
        'why_this_meal': 'Combines massive vitamin C and fiber with plant protein and healthy fats.',
        'goal_benefits': {
            'bulk': 'Clean micronutrient-dense snack between training sessions.',
            'cut': 'Exceptional satiety prevents between-meal snacking on cutting diets.',
            'maintain': 'Supports digestive health and blood sugar stability.',
            'strength': 'Supplies arginine and vitamin C for tissue repair.',
            'fitness': 'Natural whole-food nutrition for athletic stamina.'
        },
        'substitutions': [
            {'original': 'Peanuts', 'alternative': 'Roasted chana or almonds'},
            {'original': 'Guava', 'alternative': 'Orange or apple'}
        ],
        'nutrition_tip': 'A single medium guava provides over 200% of your daily recommended vitamin C intake.'
    },

    'guava + curd': {
        'description': 'Sliced fresh guava served with a refreshing bowl of cool probiotic curd.',
        'calories': 170,
        'protein': '7 g',
        'carbs': '22 g',
        'fat': '4 g',
        'fiber': '6 g',
        'ingredients': [
            '1 medium guava (chopped)',
            '150g fresh plain curd',
            'Pinch of black salt'
        ],
        'preparation_steps': [
            'Chop the guava into small cubes.',
            'Add to a bowl of fresh curd.',
            'Garnish with a pinch of black salt (kala namak) and serve.'
        ],
        'why_this_meal': 'High prebiotic fiber feeds the probiotic cultures in curd, maximizing digestive health.',
        'goal_benefits': {
            'bulk': 'Aids gut absorption of nutrients from heavy meals.',
            'cut': 'Ultra low-calorie, high-fiber, and filling snack for weight loss.',
            'maintain': 'Maintains healthy digestion and gut microbiome balance.',
            'strength': 'Supplies calcium and vitamin C for bone and joint health.',
            'fitness': 'Light, hydrating, and gut-friendly snack.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt'},
            {'original': 'Guava', 'alternative': 'Papaya or apple'}
        ],
        'nutrition_tip': 'Black salt adds sulfurous minerals and enhances digestive enzymes when paired with curd.'
    },

    'guava + peanuts': {
        'description': 'Crisp fresh guava paired with a handful of roasted peanuts.',
        'calories': 190,
        'protein': '6 g',
        'carbs': '19 g',
        'fat': '10 g',
        'fiber': '7 g',
        'ingredients': [
            '1 medium guava',
            '20g roasted peanuts'
        ],
        'preparation_steps': [
            'Slice guava into bite-sized wedges.',
            'Serve with roasted peanuts.',
            'Enjoy as an afternoon snack.'
        ],
        'why_this_meal': 'High fiber, high vitamin C, and quality plant fats for sustained energy.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and micronutrients.',
            'cut': 'High volume and crunch suppress appetite naturally.',
            'maintain': 'Maintains energy balance and stable glucose.',
            'strength': 'Antioxidants protect muscle cells during heavy workouts.',
            'fitness': 'Great clean energy boost for fitness enthusiasts.'
        },
        'substitutions': [
            {'original': 'Peanuts', 'alternative': 'Almonds or roasted chana'},
            {'original': 'Guava', 'alternative': 'Apple or pear'}
        ],
        'nutrition_tip': 'Guava has a very low glycemic index of 12–24, making it ideal for maintaining steady blood sugar.'
    },

    'milk + banana + almonds': {
        'description': 'A glass of fresh milk paired with a ripe banana and a handful of crunchy almonds.',
        'calories': 320,
        'protein': '12 g',
        'carbs': '42 g',
        'fat': '13 g',
        'fiber': '5 g',
        'ingredients': [
            '1 glass milk (250ml)',
            '1 medium ripe banana',
            '10–12 raw almonds (15g)'
        ],
        'preparation_steps': [
            'Warm or chill a glass of milk to your preference.',
            'Peel and slice a fresh banana.',
            'Count out raw almonds and serve together.'
        ],
        'why_this_meal': 'Provides complete dairy protein, potassium, and magnesium to support muscular relaxation and energy restoration.',
        'goal_benefits': {
            'bulk': 'An easy, nutrient-dense way to add high-quality surplus calories.',
            'cut': 'Portion with skim milk for a satisfying meal replacement during tight schedules.',
            'maintain': 'Supplies balanced energy and essential minerals.',
            'strength': 'Supplies bioavailable calcium and electrolytes for heavy lifting.',
            'fitness': 'Great post-workout replenishment for cardio or strength sessions.'
        },
        'substitutions': [
            {'original': 'Cow milk', 'alternative': 'Soy milk (equal protein) or almond milk'},
            {'original': 'Almonds', 'alternative': 'Walnuts or cashews'},
            {'original': 'Banana', 'alternative': 'Apple or dates'}
        ],
        'nutrition_tip': 'Milk contains both whey (fast digesting) and casein (slow digesting) proteins for sustained amino acid delivery.'
    },

    'milk + banana + peanut butter': {
        'description': 'A nutrient-packed shake or plate of milk, ripe banana, and creamy natural peanut butter.',
        'calories': 380,
        'protein': '15 g',
        'carbs': '44 g',
        'fat': '17 g',
        'fiber': '5 g',
        'ingredients': [
            '1 glass milk (250ml)',
            '1 medium banana',
            '1.5 tbsp natural peanut butter (25g)'
        ],
        'preparation_steps': [
            'Pour chilled or warm milk into a blender jar.',
            'Add sliced ripe banana and creamy natural peanut butter.',
            'Blend on high speed for 30–45 seconds until thick, frothy, and smooth.',
            'Pour into a tall glass and serve immediately with a pinch of cinnamon.'
        ],
        'why_this_meal': 'Calorie-dense powerhouse supplying complete proteins, fast and slow carbohydrates, and healthy fats.',
        'goal_benefits': {
            'bulk': 'A premier bulking snack that makes achieving a calorie surplus easy and delicious.',
            'cut': 'Keep portions moderate to utilize its incredible satiating power during cravings.',
            'maintain': 'Supplies long-lasting endurance for busy, active days.',
            'strength': 'Fuels intense weight training and supports muscle mass maintenance.',
            'fitness': 'Great pre-workout smoothie 90 minutes before prolonged training.'
        },
        'substitutions': [
            {'original': 'Cow milk', 'alternative': 'Soy milk or oat milk'},
            {'original': 'Peanut butter', 'alternative': 'Almond butter'},
            {'original': 'Banana', 'alternative': 'Oats and berries'}
        ],
        'nutrition_tip': 'Blending this into a smoothie with ice makes it a quick and convenient post-workout recovery shake.'
    },

    'orange + greek yogurt': {
        'description': 'Juicy fresh orange segments served with creamy, high-protein Greek yogurt.',
        'calories': 190,
        'protein': '15 g',
        'carbs': '24 g',
        'fat': '3 g',
        'fiber': '3 g',
        'ingredients': [
            '1 medium fresh orange (peeled and segmented)',
            '150g plain Greek yogurt'
        ],
        'preparation_steps': [
            'Peel the orange and separate into segments.',
            'Spoon Greek yogurt into a bowl and top with the orange segments.',
            'Enjoy chilled.'
        ],
        'why_this_meal': 'Vitamin C from orange enhances antioxidant protection while Greek yogurt delivers bioavailable muscle-repair protein.',
        'goal_benefits': {
            'bulk': 'Supports recovery and reduces exercise-induced oxidative stress.',
            'cut': 'High protein and high water volume keep calories low and satiety high.',
            'maintain': 'Maintains immune health and steady energy.',
            'strength': 'Supports collagen synthesis and muscle tissue integrity.',
            'fitness': 'Refreshing, hydrating, and muscle-toning snack.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Plain thick curd'},
            {'original': 'Orange', 'alternative': 'Sweet lime (mosambi) or grapefruit'}
        ],
        'nutrition_tip': 'Do not peel away all the white pith (albedo) of the orange; it is packed with hesperidin, a circulation-boosting bioflavonoid.'
    },

    'orange + yogurt': {
        'description': 'Sweet and tangy orange segments served with fresh plain yogurt.',
        'calories': 170,
        'protein': '7 g',
        'carbs': '26 g',
        'fat': '4 g',
        'fiber': '3 g',
        'ingredients': [
            '1 medium orange',
            '150g plain fresh curd/yogurt'
        ],
        'preparation_steps': [
            'Peel and segment the orange.',
            'Serve with a bowl of fresh yogurt.',
            'Mix together and enjoy.'
        ],
        'why_this_meal': 'Supplies hydration, natural vitamin C, and digestive probiotics in a light, refreshing combination.',
        'goal_benefits': {
            'bulk': 'Hydrating snack that supports digestive health.',
            'cut': 'Low in calories, satisfying sweet cravings safely.',
            'maintain': 'Maintains daily hydration and vitamin C levels.',
            'strength': 'Supports cellular repair and antioxidant status.',
            'fitness': 'Light and energizing for daily active routines.'
        },
        'substitutions': [
            {'original': 'Yogurt', 'alternative': 'Greek yogurt for higher protein'},
            {'original': 'Orange', 'alternative': 'Tangerine or sweet lime'}
        ],
        'nutrition_tip': 'Eating whole oranges instead of juice retains all dietary fiber and prevents insulin spikes.'
    },

    'peanut butter sandwich + fruit': {
        'description': 'Whole-grain bread layered with creamy natural peanut butter, served with fresh seasonal fruit.',
        'calories': 390,
        'protein': '14 g',
        'carbs': '52 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '2 slices 100% whole-grain bread',
            '1.5 tbsp natural peanut butter',
            '1 fresh apple or banana (sliced)'
        ],
        'preparation_steps': [
            'Toast whole-grain bread slices lightly.',
            'Spread natural peanut butter evenly across one slice and top with the other.',
            'Slice the sandwich diagonally and serve with fresh sliced fruit on the side.'
        ],
        'why_this_meal': 'Combines complex whole-grain carbohydrates with plant protein, healthy fats, and fiber for sustained satiety.',
        'goal_benefits': {
            'bulk': 'Calorie-dense, whole-food clean fuel that drives muscle recovery and surplus energy.',
            'cut': 'Satisfies hunger completely; high fiber and fats delay stomach emptying.',
            'maintain': 'Maintains steady physical energy during long afternoon work hours.',
            'strength': 'Provides essential B-vitamins, magnesium, and sustained carbs for heavy lifting.',
            'fitness': 'Classic, reliable athletic fuel for endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Peanut butter', 'alternative': 'Almond butter or tahini'},
            {'original': 'Whole-grain bread', 'alternative': 'Whole-wheat pita or multigrain roti'},
            {'original': 'Fruit', 'alternative': 'Berries or seasonal pear'}
        ],
        'nutrition_tip': 'Layer sliced strawberries or banana directly inside the sandwich instead of processed jelly or jam.'
    },

    'peanut butter toast + milk': {
        'description': 'Crispy whole-grain toast topped with natural peanut butter, served with a warm or chilled glass of milk.',
        'calories': 380,
        'protein': '17 g',
        'carbs': '40 g',
        'fat': '18 g',
        'fiber': '5 g',
        'ingredients': [
            '1 slice whole-grain bread',
            '1.5 tbsp natural peanut butter',
            '1 glass milk (250ml)'
        ],
        'preparation_steps': [
            'Toast whole-grain bread until crisp and golden.',
            'Spread creamy peanut butter generously over the warm toast.',
            'Serve with a fresh glass of milk.'
        ],
        'why_this_meal': 'Delivers a complete amino acid profile by combining peanut protein with dairy casein and whey.',
        'goal_benefits': {
            'bulk': 'High-protein, calorie-dense snack that fuels lean muscle growth.',
            'cut': 'Deeply satisfying snack that prevents evening bingeing.',
            'maintain': 'Provides sustained physical and cognitive energy.',
            'strength': 'Supplies calcium, magnesium, and proteins for skeletal and muscle strength.',
            'fitness': 'Wholesome post-workout snack for active individuals.'
        },
        'substitutions': [
            {'original': 'Cow milk', 'alternative': 'Soy milk or almond milk'},
            {'original': 'Peanut butter', 'alternative': 'Almond butter or cashew butter'}
        ],
        'nutrition_tip': 'Drinking milk with peanut butter toast ensures you receive all 9 essential amino acids in optimal ratios.'
    },

    'peanut butter whole-grain toast + banana': {
        'description': 'Crisp whole-grain toast smothered in natural peanut butter and layered with fresh banana coins.',
        'calories': 360,
        'protein': '12 g',
        'carbs': '50 g',
        'fat': '15 g',
        'fiber': '7 g',
        'ingredients': [
            '1 slice thick whole-grain bread',
            '1.5 tbsp natural peanut butter',
            '1 medium ripe banana (sliced)',
            'Pinch of cinnamon or chia seeds'
        ],
        'preparation_steps': [
            'Toast the bread slice until crunchy.',
            'Spread natural peanut butter across the warm surface.',
            'Layer sliced banana coins over the peanut butter.',
            'Dust with cinnamon or chia seeds and enjoy.'
        ],
        'why_this_meal': 'A staple fitness snack providing fast-release carbs from banana, slow-release carbs from whole grains, and healthy fats.',
        'goal_benefits': {
            'bulk': 'Great pre-workout or post-workout fuel supporting high-intensity training.',
            'cut': 'High fiber and healthy fats prevent hunger crashes between meals.',
            'maintain': 'Maintains steady daytime energy and muscle glycogen.',
            'strength': 'Supplies potassium and carbohydrates for explosive power output.',
            'fitness': 'A nutrient-rich snack that fuels workouts and active recovery.'
        },
        'substitutions': [
            {'original': 'Peanut butter', 'alternative': 'Almond butter or sunflower seed butter'},
            {'original': 'Whole-grain bread', 'alternative': 'Sourdough or multigrain roti'},
            {'original': 'Banana', 'alternative': 'Sliced apple or strawberries'}
        ],
        'nutrition_tip': 'Adding a sprinkle of chia seeds adds alpha-linolenic acid (ALA) omega-3s and extra soluble fiber.'
    },

    'peanut butter whole-grain toast + fruit': {
        'description': 'Whole-grain toast with natural peanut butter accompanied by fresh seasonal fruit.',
        'calories': 350,
        'protein': '11 g',
        'carbs': '48 g',
        'fat': '15 g',
        'fiber': '7 g',
        'ingredients': [
            '1 slice whole-grain bread',
            '1.5 tbsp natural peanut butter',
            '1 cup fresh seasonal fruit slices (apple, berries, or papaya)'
        ],
        'preparation_steps': [
            'Toast the whole-grain bread to golden crispness.',
            'Spread natural peanut butter over the toast.',
            'Serve with a bowl of freshly prepared seasonal fruit.'
        ],
        'why_this_meal': 'Delivers complex carbs, plant proteins, healthy monounsaturated fats, and rich fruit phytonutrients.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and amino acids to support training and recovery.',
            'cut': 'High fiber and fats promote long-lasting satiety.',
            'maintain': 'Maintains stable blood glucose and energy levels.',
            'strength': 'Provides sustained muscular energy for evening training.',
            'fitness': 'Wholesome whole-food fuel for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Peanut butter', 'alternative': 'Almond butter'},
            {'original': 'Whole-grain toast', 'alternative': 'Rice cakes or whole-wheat pita'}
        ],
        'nutrition_tip': 'Peanut butter provides vitamin E, an important fat-soluble antioxidant that protects cell membranes.'
    },

    'roasted chana': {
        'description': 'Crisp, savory roasted Bengal gram (chickpeas) with rich natural protein and fiber.',
        'calories': 180,
        'protein': '10 g',
        'carbs': '28 g',
        'fat': '3 g',
        'fiber': '8 g',
        'ingredients': [
            '45g roasted chana (bhuna chana with skin)',
            'Pinch of chaat masala and black pepper (optional)'
        ],
        'preparation_steps': [
            'Measure a serving (45g or about 1/2 cup) of roasted chana with skin.',
            'Toss with a subtle pinch of chaat masala or black pepper.',
            'Enjoy as a crunchy, highly portable snack.'
        ],
        'why_this_meal': 'One of the best low-fat, high-protein, high-fiber plant snacks with an exceptionally low glycemic index.',
        'goal_benefits': {
            'bulk': 'Supplies clean plant protein and complex carbs between meals.',
            'cut': 'Outstanding cutting snack: 8g of filling fiber and 10g of protein for under 200 calories.',
            'maintain': 'Keeps blood sugar flat and satisfies the urge for crunchy snacks.',
            'strength': 'Supplies iron, zinc, and magnesium for muscle stamina and repair.',
            'fitness': 'A clean, oil-free fitness snack that supports metabolic conditioning.'
        },
        'substitutions': [
            {'original': 'Roasted chana', 'alternative': 'Roasted edamame or roasted sprouted moong'}
        ],
        'nutrition_tip': 'Always eat roasted chana with its brown skin intact to retain maximum insoluble prebiotic fiber.'
    },

    'roasted chana + banana': {
        'description': 'Crunchy roasted chana paired with a fresh ripe banana for an energizing balance of protein and carbs.',
        'calories': 270,
        'protein': '11 g',
        'carbs': '50 g',
        'fat': '4 g',
        'fiber': '10 g',
        'ingredients': [
            '40g roasted chana with skin',
            '1 medium ripe banana'
        ],
        'preparation_steps': [
            'Portion roasted chana into a snack bowl.',
            'Peel a fresh banana.',
            'Enjoy together as an authentic, high-fiber fitness snack.'
        ],
        'why_this_meal': 'Combines fast-acting potassium and carbs from banana with slow-burning complex carbs and protein from roasted gram.',
        'goal_benefits': {
            'bulk': 'Clean fuel for muscle recovery and surplus energy.',
            'cut': 'High fiber (10g total) provides long-lasting fullness on cutting diets.',
            'maintain': 'Maintains energy balance and cognitive vitality.',
            'strength': 'Supplies electrolytes and amino acids for muscle contractions.',
            'fitness': 'Ideal pre-workout whole-food fuel 45 minutes before exercise.'
        },
        'substitutions': [
            {'original': 'Roasted chana', 'alternative': 'Roasted peanuts or roasted soybeans'},
            {'original': 'Banana', 'alternative': 'Guava or seasonal apple'}
        ],
        'nutrition_tip': 'This traditional snack pairing delivers sustained energy without requiring any processed protein bars.'
    },

    'roasted chana + fruit': {
        'description': 'Crunchy roasted chana served with fresh seasonal fruit.',
        'calories': 240,
        'protein': '10 g',
        'carbs': '42 g',
        'fat': '4 g',
        'fiber': '10 g',
        'ingredients': [
            '40g roasted chana with skin',
            '1 cup fresh seasonal fruit (papaya, apple, or orange)'
        ],
        'preparation_steps': [
            'Chop fresh seasonal fruit into a dish.',
            'Add roasted chana alongside.',
            'Enjoy fresh and crunchy.'
        ],
        'why_this_meal': 'Supplies 10g of plant protein, massive fiber, and essential fruit vitamins with virtually zero saturated fat.',
        'goal_benefits': {
            'bulk': 'Supplies clean micronutrients and plant protein.',
            'cut': 'Massive fiber content keeps appetite suppressed for hours.',
            'maintain': 'Supports healthy digestion and stable blood sugar.',
            'strength': 'Supplies iron and minerals for red blood cell health.',
            'fitness': 'Light, oil-free, and energizing snack for active routines.'
        },
        'substitutions': [
            {'original': 'Roasted chana', 'alternative': 'Roasted edamame or roasted peanuts'},
            {'original': 'Fruit', 'alternative': 'Guava, pear, or pomegranate'}
        ],
        'nutrition_tip': 'Vitamin C from fresh fruit significantly boosts the absorption of non-heme iron from the roasted chana.'
    },

    'roasted chana + lemon': {
        'description': 'Crisp roasted chana tossed with freshly squeezed lemon juice, chaat masala, and fresh coriander.',
        'calories': 185,
        'protein': '10 g',
        'carbs': '28 g',
        'fat': '3 g',
        'fiber': '8 g',
        'ingredients': [
            '45g roasted chana with skin',
            '1 tbsp fresh lemon juice',
            'Pinch of chaat masala, roasted cumin, and finely chopped coriander'
        ],
        'preparation_steps': [
            'Place roasted chana in a small bowl.',
            'Squeeze fresh lemon juice over the top.',
            'Sprinkle with chaat masala and chopped coriander, toss quickly and enjoy immediately before it loses crispness.'
        ],
        'why_this_meal': 'Lemon juice adds ascorbic acid which enhances the bioavailability of iron from the chana while adding zest without sodium.',
        'goal_benefits': {
            'bulk': 'Clean, light protein snack that stimulates digestion.',
            'cut': 'Premier cutting snack: high protein, high fiber, satisfying crunch, and virtually no fat.',
            'maintain': 'Maintains sharp mental focus and steady metabolic rate.',
            'strength': 'Iron and protein support muscular stamina.',
            'fitness': 'A refreshing, oil-free fitness snack that supports fat burning.'
        },
        'substitutions': [
            {'original': 'Roasted chana', 'alternative': 'Sprouted boiled moong or roasted chickpeas'},
            {'original': 'Lemon juice', 'alternative': 'Lime juice or amla juice'}
        ],
        'nutrition_tip': 'Consume immediately after adding lemon juice to enjoy the maximum crunch.'
    },

    'roasted chana + seasonal fruit': {
        'description': 'Crunchy roasted chana served with fresh sliced seasonal fruit.',
        'calories': 240,
        'protein': '10 g',
        'carbs': '42 g',
        'fat': '4 g',
        'fiber': '10 g',
        'ingredients': [
            '40g roasted chana with skin',
            '1 piece fresh seasonal fruit (apple, guava, or orange)'
        ],
        'preparation_steps': [
            'Slice the seasonal fruit.',
            'Portion roasted chana.',
            'Serve together for an afternoon nutrition boost.'
        ],
        'why_this_meal': 'High in bioflavonoids, prebiotic fiber, plant protein, and essential micronutrients.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and amino acids to support training and recovery.',
            'cut': 'High fiber and low calorie density keep you full on cutting diets.',
            'maintain': 'Maintains steady blood glucose and energy levels.',
            'strength': 'Provides essential iron and B-vitamins for workout energy.',
            'fitness': 'Wholesome, clean fuel for everyday fitness conditioning.'
        },
        'substitutions': [
            {'original': 'Roasted chana', 'alternative': 'Roasted peanuts or roasted soybeans'},
            {'original': 'Seasonal fruit', 'alternative': 'Banana, papaya, or pear'}
        ],
        'nutrition_tip': 'Pairing legume protein with whole fresh fruit creates an optimal sustained-release energy source.'
    },

    'sprouts + fruit': {
        'description': 'Freshly sprouted whole moong beans tossed with diced seasonal fruits, lemon juice, and chaat masala.',
        'calories': 210,
        'protein': '12 g',
        'carbs': '38 g',
        'fat': '2 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup sprouted whole moong beans (steamed or raw)',
            '1 cup diced seasonal fruit (pomegranate, apple, raw mango)',
            '1 tbsp fresh lemon juice, pinch of rock salt and chaat masala'
        ],
        'preparation_steps': [
            'Lightly steam sprouted moong for 2 minutes (or use fresh raw sprouts).',
            'Add diced fruits and toss together in a salad bowl.',
            'Season with fresh lemon juice, rock salt, and chaat masala.',
            'Serve fresh for maximum enzyme activity.'
        ],
        'why_this_meal': 'Sprouting dramatically increases vitamin C, folate, and protein bioavailability while reducing anti-nutrients like phytates.',
        'goal_benefits': {
            'bulk': 'Enzyme-rich snack that enhances overall nutrient assimilation and digestion.',
            'cut': 'Very high volume and fiber for minimal calories; top-tier cutting food.',
            'maintain': 'Maintains vitality, cellular hydration, and gut microbiome balance.',
            'strength': 'Supplies bioavailable iron, potassium, and magnesium for muscle recovery.',
            'fitness': 'A living food snack loaded with active enzymes and antioxidants.'
        },
        'substitutions': [
            {'original': 'Moong sprouts', 'alternative': 'Sprouted black gram (kala chana) or alfalfa sprouts'},
            {'original': 'Fruit', 'alternative': 'Diced cucumber, tomatoes, and pomegranate'}
        ],
        'nutrition_tip': 'Steaming sprouts lightly for 2 minutes enhances digestibility and eliminates any surface bacteria.'
    },

    'sprouts + whole-grain toast': {
        'description': 'Seasoned crunchy moong bean sprouts served on crisp whole-grain toast with lemon and herbs.',
        'calories': 280,
        'protein': '14 g',
        'carbs': '48 g',
        'fat': '4 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup sprouted moong beans (lightly sautéed with cumin and turmeric)',
            '2 slices 100% whole-grain bread',
            '1 tsp lemon juice, fresh coriander, pinch of chaat masala'
        ],
        'preparation_steps': [
            'Sauté sprouted moong in a non-stick pan with a pinch of cumin, turmeric, and salt for 2 minutes.',
            'Toast whole-grain bread slices until crisp.',
            'Top the toast with warm seasoned sprouts, finish with lemon juice and fresh coriander, and serve.'
        ],
        'why_this_meal': 'Provides complementary plant proteins from sprouted legumes and whole grains, creating a complete amino acid profile.',
        'goal_benefits': {
            'bulk': 'Clean plant protein and complex carbs support muscle repair.',
            'cut': 'High fiber and protein keep you full during long deficit intervals.',
            'maintain': 'Maintains energy balance and cardiovascular wellness.',
            'strength': 'Provides essential iron and B-complex vitamins for metabolic energy.',
            'fitness': 'Light, digestible, and nutritious fuel for active lifestyles.'
        },
        'substitutions': [
            {'original': 'Sprouts', 'alternative': 'Boiled chickpeas or edamame'},
            {'original': 'Whole-grain toast', 'alternative': 'Sourdough bread or whole-wheat pita'}
        ],
        'nutrition_tip': 'Sprouting activates dormant enzymes, converting starches into simpler, easier-to-digest carbohydrates.'
    },

    'whole-grain toast + greek yogurt': {
        'description': 'Crispy whole-grain toast topped with thick, savory or sweet Greek yogurt and herbs.',
        'calories': 250,
        'protein': '16 g',
        'carbs': '34 g',
        'fat': '5 g',
        'fiber': '5 g',
        'ingredients': [
            '2 slices whole-grain bread',
            '120g plain thick Greek yogurt',
            'Pinch of black pepper, olive oil drizzle, or berries'
        ],
        'preparation_steps': [
            'Toast whole-grain bread slices until golden brown and crisp.',
            'Spread thick Greek yogurt over the warm toast.',
            'Season with freshly cracked black pepper and a drizzle of olive oil (savory) or fresh berries (sweet).'
        ],
        'why_this_meal': 'Combines complex fiber-rich carbohydrates with high-density complete dairy protein for prolonged satiety.',
        'goal_benefits': {
            'bulk': 'Supplies quality protein and clean carbohydrates for recovery.',
            'cut': 'High protein and dietary fiber keep appetite satisfied while cutting.',
            'maintain': 'Maintains steady blood glucose and energy levels.',
            'strength': 'Provides essential amino acids and calcium for muscle power and recovery.',
            'fitness': 'A clean, modern whole-food snack that supports workout stamina.'
        },
        'substitutions': [
            {'original': 'Greek yogurt', 'alternative': 'Low-fat cottage cheese (paneer) or hung curd'},
            {'original': 'Whole-grain toast', 'alternative': 'Rye bread or whole-wheat pita'}
        ],
        'nutrition_tip': 'Using Greek yogurt as a toast spread provides a high-protein, probiotic alternative to butter or mayonnaise.'
    },

    # -------------------------------------------------------------
    # LUNCH ITEMS (RICE, CHICKEN, PANEER, TOFU, DAL, VEGETABLES)
    # -------------------------------------------------------------
    'brown rice + chicken + vegetables + dal': {
        'description': 'High-protein fitness meal of fiber-rich brown rice, lean grilled chicken breast, yellow lentil dal, and mixed vegetables.',
        'calories': 560,
        'protein': '42 g',
        'carbs': '65 g',
        'fat': '14 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup cooked brown rice (150g)',
            '150g grilled chicken breast (cubed)',
            '1 cup yellow lentil dal (toor or moong dal)',
            '1 cup steamed mixed vegetables (broccoli, carrots, beans)',
            '1 tsp olive oil or ghee, cumin, turmeric, garlic'
        ],
        'preparation_steps': [
            'Cook brown rice until tender with grains separate.',
            'Marinate chicken breast with yogurt, garlic, turmeric, and lemon; grill or pan-sear until cooked through.',
            'Prepare a comforting dal tempered with cumin, garlic, and turmeric.',
            'Steam mixed vegetables lightly and serve together as a balanced, high-protein lunch.'
        ],
        'why_this_meal': 'Combines lean animal protein with plant protein and slow-digesting complex carbohydrates for complete muscle recovery.',
        'goal_benefits': {
            'bulk': 'Provides 42g of complete protein and clean carbohydrates to fuel intense hypertrophy and tissue synthesis.',
            'cut': 'High protein and abundant fiber maximize satiety while supporting lean muscle retention during caloric restriction.',
            'maintain': 'Delivers an optimal balance of all three macronutrients to maintain body composition effortlessly.',
            'strength': 'Supplies bioavailable iron, leucine, and complex carbohydrates for maximum strength development and power output.',
            'fitness': 'Wholesome, balanced fuel that provides long-lasting energy for all physical activities.'
        },
        'substitutions': [
            {'original': 'Chicken breast', 'alternative': 'Low-fat paneer (150g), firm tofu, or grilled fish'},
            {'original': 'Brown rice', 'alternative': 'Quinoa, red rice, or 2 whole-wheat rotis'},
            {'original': 'Yellow dal', 'alternative': 'Rajma, chana, or black lentil dal'}
        ],
        'nutrition_tip': 'Grilling or pan-searing chicken with garlic and herbs enhances flavor without adding excess cooking fats.'
    },

    'brown rice + chicken/paneer + vegetables': {
        'description': 'A wholesome fitness lunch plate of fiber-rich brown rice, grilled chicken breast or fresh paneer, and sautéed vegetables.',
        'calories': 540,
        'protein': '38 g',
        'carbs': '60 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '140g lean chicken breast OR 120g fresh paneer',
            '1.5 cups stir-fried mixed vegetables (bell peppers, zucchini, beans, carrots)',
            '1 tsp olive oil, garlic, ginger, and herbs'
        ],
        'preparation_steps': [
            'Steam brown rice until fully cooked and fluffy.',
            'Sauté diced chicken or paneer in 1 tsp olive oil with ginger, garlic, and spices until golden.',
            'Toss mixed vegetables in the same pan with herbs until tender-crisp.',
            'Plate the brown rice alongside the protein and colorful vegetables.'
        ],
        'why_this_meal': 'Supplies high-quality complete protein alongside low-glycemic complex carbohydrates and micronutrient-dense produce.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Firm tofu (150g) or grilled fish fillet'},
            {'original': 'Brown rice', 'alternative': 'Quinoa, millets, or whole-wheat chapati'}
        ],
        'nutrition_tip': 'Cooking brown rice with a dash of ginger helps ease digestion and enhances nutrient bioavailability.'
    },

    'brown rice + chicken/tofu + dal + vegetables': {
        'description': 'Nutrient-dense lunch featuring brown rice, lean chicken or organic tofu, protein-rich dal, and steamed vegetables.',
        'calories': 530,
        'protein': '38 g',
        'carbs': '64 g',
        'fat': '14 g',
        'fiber': '10 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '130g grilled chicken breast OR 150g firm tofu cubes',
            '1 cup yellow lentil dal',
            '1 cup mixed steamed vegetables (beans, carrots, cauliflower)',
            '1 tsp cumin seeds, turmeric, garlic, and lemon'
        ],
        'preparation_steps': [
            'Cook brown rice to perfection in lightly salted water.',
            'Pan-sear chicken strips or tofu cubes with turmeric and black pepper until lightly browned.',
            'Simmer yellow dal tempered with cumin, garlic, and fresh herbs.',
            'Steam mixed vegetables and serve as a complete, satisfying lunch bowl.'
        ],
        'why_this_meal': 'Dual protein sources (chicken/tofu + lentils) deliver an abundance of essential amino acids and micronutrients.',
        'goal_benefits': {
            'bulk': 'Ample protein and complex carbohydrates support glycogen recovery and lean mass growth.',
            'cut': 'Very high fiber (10g) promotes prolonged fullness during cutting phases.',
            'maintain': 'Maintains energy balance, digestive health, and lean muscle tone.',
            'strength': 'Supplies zinc, iron, and BCAAs for heavy resistance training recovery.',
            'fitness': 'Wholesome, clean fuel for all-around fitness performance.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer (120g) or grilled fish'},
            {'original': 'Brown rice', 'alternative': 'Foxtail millet or quinoa'}
        ],
        'nutrition_tip': 'Squeeze fresh lemon juice over the dal right before eating to boost plant iron absorption.'
    },

    'brown rice + chicken/tofu + vegetables': {
        'description': 'A clean fitness lunch of brown rice, seasoned chicken breast or firm tofu, and colorful garden vegetables.',
        'calories': 510,
        'protein': '36 g',
        'carbs': '58 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '140g chicken breast OR 150g firm tofu',
            '1.5 cups sautéed mixed vegetables (bell peppers, broccoli, carrots)',
            '1 tsp sesame oil or olive oil, garlic, and soy or herb seasoning'
        ],
        'preparation_steps': [
            'Cook brown rice until tender.',
            'Stir-fry cubed chicken breast or tofu in 1 tsp oil with minced garlic until golden.',
            'Add mixed vegetables and toss on high heat for 3 minutes until vibrant and crisp.',
            'Serve over a bed of warm brown rice.'
        ],
        'why_this_meal': 'Delivers lean protein, low-glycemic carbohydrates, and rich antioxidants for optimal metabolic support.',
        'goal_benefits': {
            'bulk': 'Provides essential amino acids and clean carbohydrates for recovery.',
            'cut': 'High protein and dietary fiber keep you full during a calorie deficit.',
            'maintain': 'Maintains steady energy and lean body composition.',
            'strength': 'Delivers vital nutrients to support intense lifting sessions.',
            'fitness': 'Clean, wholesome fuel for daily workouts and vitality.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer or white fish'},
            {'original': 'Brown rice', 'alternative': 'Cauliflower rice mixed with brown rice'}
        ],
        'nutrition_tip': 'Stir-frying vegetables on high heat for a short time preserves heat-sensitive vitamins and crisp texture.'
    },

    'brown rice + dal + paneer + vegetables': {
        'description': 'A vegetarian powerhouse lunch of fiber-rich brown rice, spiced yellow dal, fresh paneer cubes, and mixed vegetables.',
        'calories': 550,
        'protein': '26 g',
        'carbs': '68 g',
        'fat': '18 g',
        'fiber': '10 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '100g fresh paneer (lightly pan-seared)',
            '1 cup thick yellow or mixed dal',
            '1 cup steamed or sautéed mixed vegetables',
            '1 tsp ghee or oil, cumin, turmeric, and coriander'
        ],
        'preparation_steps': [
            'Cook brown rice until soft and fluffy.',
            'Cut paneer into cubes and lightly sauté with a pinch of turmeric and salt.',
            'Prepare dal tempered with cumin seeds, garlic, and green chilies.',
            'Steam vegetables and assemble with brown rice, paneer, and dal.'
        ],
        'why_this_meal': 'Lentils and dairy paneer combine to form a complete vegetarian amino acid profile alongside low-GI fiber.',
        'goal_benefits': {
            'bulk': 'Quality vegetarian calories, healthy fats, and protein for sustained muscle building.',
            'cut': 'Substantial dietary fiber and protein keep appetite under tight control.',
            'maintain': 'Balanced vegetarian meal supporting daily energy and lean mass.',
            'strength': 'Supplies calcium and magnesium from paneer to support muscle contractions.',
            'fitness': 'Clean whole-food vegetarian nutrition for athletic stamina.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Firm tofu (140g) or tempeh for lower saturated fat'},
            {'original': 'Brown rice', 'alternative': 'Millets or quinoa'},
            {'original': 'Yellow dal', 'alternative': 'Black dal or chana dal'}
        ],
        'nutrition_tip': 'Lightly sautéing paneer without deep-frying keeps fat levels moderate while improving texture.'
    },

    'brown rice + dal + vegetables + chicken/tofu': {
        'description': 'A balanced fitness lunch pairing brown rice with hearty lentil dal, garden vegetables, and chicken or tofu.',
        'calories': 530,
        'protein': '38 g',
        'carbs': '64 g',
        'fat': '14 g',
        'fiber': '10 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '130g grilled chicken breast OR 150g tofu',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil, cumin, garlic, turmeric'
        ],
        'preparation_steps': [
            'Steam brown rice.',
            'Grill chicken or pan-sear tofu with herbs and spices.',
            'Prepare a bowl of warm lentil dal tempered with cumin and garlic.',
            'Serve together with a generous portion of steamed vegetables.'
        ],
        'why_this_meal': 'Provides dual protein sources and complex carbohydrates for sustained energy and muscle recovery.',
        'goal_benefits': {
            'bulk': 'Supplies clean energy and amino acids to support training and recovery.',
            'cut': 'High protein and dietary fiber keep you full and satisfied.',
            'maintain': 'Maintains steady blood glucose and lean body composition.',
            'strength': 'Replenishes glycogen and provides leucine for muscle protein synthesis.',
            'fitness': 'Promotes all-around wellness, stamina, and workout recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer (120g) or fish fillet'},
            {'original': 'Brown rice', 'alternative': 'Quinoa or red rice'}
        ],
        'nutrition_tip': 'Brown rice retains its nutrient-rich bran layer, providing 3x the fiber of polished white rice.'
    },

    'brown rice + dal + vegetables + paneer': {
        'description': 'Wholesome brown rice served with aromatic lentil dal, sautéed vegetables, and pan-seared paneer.',
        'calories': 540,
        'protein': '25 g',
        'carbs': '66 g',
        'fat': '18 g',
        'fiber': '10 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '100g fresh paneer cubes',
            '1 cup yellow lentil dal',
            '1 cup mixed vegetables (beans, carrots, peas)',
            '1 tsp ghee, cumin, turmeric, garlic'
        ],
        'preparation_steps': [
            'Cook brown rice until fluffy.',
            'Pan-sear paneer cubes until golden on the edges.',
            'Simmer dal with aromatic Indian spices.',
            'Plate the brown rice with dal, paneer, and steamed vegetables.'
        ],
        'why_this_meal': 'Supplies complete vegetarian protein, rich calcium, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'Supports muscle repair and healthy weight maintenance cleanly.',
            'cut': 'Rich fiber content curbs hunger while supplying essential nutrients.',
            'maintain': 'Provides balanced nutrition for everyday wellness.',
            'strength': 'Supplies calcium and magnesium to support bone and muscle strength.',
            'fitness': 'Wholesome vegetarian fuel for daily energy.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Firm tofu or boiled chickpeas'},
            {'original': 'Brown rice', 'alternative': 'Multigrain roti (2 pcs)'}
        ],
        'nutrition_tip': 'Paneer provides casein protein, which digests slowly to provide a continuous amino acid flow.'
    },

    'brown rice + fish + vegetables + dal': {
        'description': 'A nutrient-dense lunch of brown rice, pan-seared omega-3 rich fish, comforting lentil dal, and mixed vegetables.',
        'calories': 520,
        'protein': '40 g',
        'carbs': '62 g',
        'fat': '12 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '150g white fish or salmon fillet',
            '1 cup yellow lentil dal',
            '1 cup mixed steamed vegetables (broccoli, beans, carrots)',
            '1 tsp olive oil, lemon juice, turmeric, garlic, and black pepper'
        ],
        'preparation_steps': [
            'Cook brown rice until tender.',
            'Season fish fillet with lemon, turmeric, garlic, and black pepper, then pan-sear in 1 tsp olive oil for 3–4 mins per side.',
            'Prepare dal tempered with cumin and garlic.',
            'Serve the fish alongside brown rice, dal, and steamed vegetables.'
        ],
        'why_this_meal': 'Fish provides high-quality protein and essential omega-3 fatty acids (EPA/DHA) that combat exercise-induced inflammation.',
        'goal_benefits': {
            'bulk': 'High protein and anti-inflammatory omega-3s accelerate muscle tissue repair and joint recovery.',
            'cut': 'Lean protein from fish coupled with high fiber keeps calories low and metabolic rate high.',
            'maintain': 'Supports cardiovascular health, brain function, and body composition.',
            'strength': 'Omega-3 fats support neuromuscular signaling and reduce post-training joint soreness.',
            'fitness': 'A premier athletic lunch for cardiovascular endurance and cellular health.'
        },
        'substitutions': [
            {'original': 'Fish fillet', 'alternative': 'Chicken breast (150g) or paneer/tofu'},
            {'original': 'Brown rice', 'alternative': 'Quinoa or millets'}
        ],
        'nutrition_tip': 'Omega-3 fatty acids in fish help increase muscle protein synthesis sensitivity to dietary amino acids.'
    },

    'brown rice + fish/chicken + vegetables': {
        'description': 'A clean protein-forward lunch combining brown rice with grilled fish or chicken breast and fresh sautéed vegetables.',
        'calories': 510,
        'protein': '40 g',
        'carbs': '56 g',
        'fat': '14 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '150g grilled fish fillet OR lean chicken breast',
            '1.5 cups stir-fried mixed vegetables',
            '1 tsp olive oil, herbs, lemon, and garlic'
        ],
        'preparation_steps': [
            'Steam brown rice.',
            'Season fish or chicken with herbs, lemon, and garlic; grill or pan-sear until fully cooked.',
            'Stir-fry mixed vegetables lightly with herbs and pepper.',
            'Serve together for a balanced, high-protein meal.'
        ],
        'why_this_meal': 'Supplies pure lean animal protein, complex carbohydrates, and vibrant micronutrients with minimal saturated fat.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Fish / Chicken', 'alternative': 'Paneer (120g) or firm tofu (150g)'},
            {'original': 'Brown rice', 'alternative': 'Quinoa or sweet potato'}
        ],
        'nutrition_tip': 'Seasoning fish or chicken with fresh herbs like rosemary or oregano adds potent natural antioxidant flavonoids.'
    },

    'brown rice + lean chicken/tofu + vegetables': {
        'description': 'A lean and clean lunch bowl of brown rice, tender chicken breast or organic tofu, and steamed garden vegetables.',
        'calories': 490,
        'protein': '38 g',
        'carbs': '56 g',
        'fat': '12 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked brown rice',
            '140g lean chicken breast OR 150g firm tofu',
            '1.5 cups steamed mixed vegetables (broccoli, beans, carrots)',
            '1 tsp olive oil, herbs, and lemon'
        ],
        'preparation_steps': [
            'Steam brown rice.',
            'Grill chicken breast or tofu in minimal oil with lemon and herbs.',
            'Steam mixed vegetables until crisp-tender.',
            'Plate together for a clean, lean meal.'
        ],
        'why_this_meal': 'High protein-to-calorie ratio with low glycemic impact, ideal for maintaining lean body mass.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding without unwanted fat accumulation.',
            'cut': 'Exceptional meal for cutting: massive satiety, high protein, and low fat.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids for fast post-workout recovery.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Fish fillet or low-fat paneer'},
            {'original': 'Brown rice', 'alternative': 'Quinoa or cauliflower rice blend'}
        ],
        'nutrition_tip': 'Steaming vegetables instead of boiling preserves water-soluble vitamin C and B-complex vitamins.'
    },

    'chicken + rice + dal + mixed vegetables': {
        'description': 'A hearty, classic fitness meal with tender chicken, steamed rice, comforting yellow dal, and mixed vegetables.',
        'calories': 570,
        'protein': '42 g',
        'carbs': '68 g',
        'fat': '14 g',
        'fiber': '8 g',
        'ingredients': [
            '150g grilled chicken breast',
            '1 cup cooked rice',
            '1 cup yellow lentil dal',
            '1 cup mixed vegetables',
            '1 tsp oil, cumin, garlic, turmeric'
        ],
        'preparation_steps': [
            'Cook rice until fluffy.',
            'Marinate chicken in garlic, ginger, and turmeric, then grill or pan-sear until cooked.',
            'Simmer yellow dal with aromatic cumin and garlic tempering.',
            'Steam vegetables and serve together as a satisfying plate.'
        ],
        'why_this_meal': 'A complete balanced Indian lunch delivering high-quality protein, complex carbs, and essential micronutrients.',
        'goal_benefits': {
            'bulk': 'An exceptional meal providing ample protein and carbohydrates to fuel heavy muscle growth.',
            'cut': 'High protein content preserves lean mass during caloric deficits.',
            'maintain': 'Maintains body composition and steady metabolic energy.',
            'strength': 'Delivers BCAAs, iron, and glycogen for peak strength training.',
            'fitness': 'All-around athletic nutrition that powers workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken', 'alternative': 'Paneer (140g) or firm tofu'},
            {'original': 'White rice', 'alternative': 'Brown rice or quinoa'}
        ],
        'nutrition_tip': 'Garlic and ginger in dal seasoning help stimulate digestive fire and enhance amino acid absorption.'
    },

    'rice + chicken + dal + vegetables': {
        'description': 'A balanced lunch plate of steamed rice, tender cooked chicken breast, yellow lentil dal, and mixed vegetables.',
        'calories': 560,
        'protein': '42 g',
        'carbs': '66 g',
        'fat': '14 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '150g chicken breast',
            '1 cup dal',
            '1 cup mixed vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Steam rice.',
            'Cook chicken with mild spices and herbs.',
            'Prepare a comforting lentil dal.',
            'Serve with steamed garden vegetables.'
        ],
        'why_this_meal': 'Supplies complete proteins, sustained energy, and essential vitamins for active fitness routines.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery and caloric surplus.',
            'cut': 'High protein promotes fullness and muscle retention.',
            'maintain': 'Balanced nutrition for everyday vitality.',
            'strength': 'Powers heavy resistance workouts.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken', 'alternative': 'Paneer or fish'},
            {'original': 'Rice', 'alternative': 'Brown rice or roti'}
        ],
        'nutrition_tip': 'Pairing lentils with grains like rice creates a complete complementary amino acid profile.'
    },

    'rice + chicken/paneer + dal + vegetables': {
        'description': 'Steamed rice served with tender chicken or fresh paneer, yellow lentil dal, and sautéed vegetables.',
        'calories': 550,
        'protein': '38 g',
        'carbs': '66 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g chicken breast OR 120g fresh paneer',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil/ghee, cumin, turmeric, garlic'
        ],
        'preparation_steps': [
            'Steam rice until soft.',
            'Cook chicken or pan-sear paneer with turmeric and herbs.',
            'Simmer seasoned yellow dal.',
            'Plate together with steamed mixed vegetables.'
        ],
        'why_this_meal': 'Supplies a rich blend of complete proteins, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'High protein and clean carbohydrates support muscle rebuilding.',
            'cut': 'High protein keeps hunger under control during a cut.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Firm tofu (150g) or fish'},
            {'original': 'Rice', 'alternative': 'Brown rice or 2 rotis'}
        ],
        'nutrition_tip': 'Turmeric in the dal provides curcumin, which helps soothe exercise-induced muscle inflammation.'
    },

    'rice + chicken/paneer + rajma + vegetables': {
        'description': 'A protein-dense North Indian feast of steamed rice, chicken or paneer, kidney bean rajma, and mixed vegetables.',
        'calories': 580,
        'protein': '40 g',
        'carbs': '72 g',
        'fat': '15 g',
        'fiber': '11 g',
        'ingredients': [
            '1 cup cooked rice',
            '130g chicken breast OR 100g paneer',
            '1 cup rajma (red kidney bean curry)',
            '1 cup mixed vegetables',
            '1 tsp oil, ginger, garlic, tomatoes, and spices'
        ],
        'preparation_steps': [
            'Pressure-cook soaked kidney beans and simmer in a spiced tomato-ginger-garlic gravy.',
            'Grill chicken or sauté paneer cubes lightly.',
            'Steam rice until fluffy.',
            'Serve hot with rajma, protein, and a side of sautéed vegetables.'
        ],
        'why_this_meal': 'Rajma is extraordinarily rich in dietary fiber, potassium, and plant protein, making this a nutritional powerhouse.',
        'goal_benefits': {
            'bulk': 'Abundant carbohydrates and multi-source proteins provide the ideal muscle-building surplus.',
            'cut': 'Huge fiber content (11g) keeps you completely full for hours on end.',
            'maintain': 'Provides long-lasting afternoon stamina and stable blood sugar.',
            'strength': 'Supplies iron, magnesium, and potassium for heavy strength lifting.',
            'fitness': 'Rich in antioxidants and clean energy for all athletic pursuits.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu or soya chunks'},
            {'original': 'Rajma', 'alternative': 'Chana masala or black bean curry'},
            {'original': 'Rice', 'alternative': 'Brown rice or chapati'}
        ],
        'nutrition_tip': 'Kidney beans (rajma) have a very low glycemic index, promoting steady blood sugar and sustained energy.'
    },

    'rice + chicken/paneer + vegetables': {
        'description': 'Steamed rice paired with seasoned chicken breast or fresh paneer and sautéed garden vegetables.',
        'calories': 530,
        'protein': '36 g',
        'carbs': '62 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g chicken breast OR 120g paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil, garlic, spices'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Sauté chicken or paneer with spices and garlic.',
            'Stir-fry mixed vegetables.',
            'Serve together as a balanced lunch.'
        ],
        'why_this_meal': 'Delivers quality complete protein and clean carbohydrates for efficient workout recovery.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu or fish fillet'},
            {'original': 'White rice', 'alternative': 'Brown rice or millets'}
        ],
        'nutrition_tip': 'Pairing lean protein with vegetables slows digestion, improving overall nutrient absorption.'
    },

    'rice + chicken/tofu + dal + vegetables': {
        'description': 'Steamed rice served with tender chicken or organic tofu, comforting yellow dal, and fresh vegetables.',
        'calories': 540,
        'protein': '38 g',
        'carbs': '65 g',
        'fat': '14 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g chicken breast OR 150g firm tofu',
            '1 cup yellow lentil dal',
            '1 cup mixed vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Steam rice.',
            'Cook chicken or tofu with seasonings.',
            'Prepare yellow dal with cumin tempering.',
            'Serve with steamed vegetables.'
        ],
        'why_this_meal': 'Provides dual protein sources, complex carbohydrates, and dietary fiber for optimal post-training recovery.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding and glycogen restoration.',
            'cut': 'High protein and dietary fiber keep you full during a calorie deficit.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids and minerals for lifting power.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer or fish'},
            {'original': 'Rice', 'alternative': 'Brown rice or chapati'}
        ],
        'nutrition_tip': 'Lentils provide molybdenum, a trace mineral essential for detoxifying sulfites in the body.'
    },

    'rice + dal + mixed vegetables + chicken/paneer': {
        'description': 'Steamed rice, yellow lentil dal, mixed vegetables, and grilled chicken breast or fresh paneer.',
        'calories': 550,
        'protein': '38 g',
        'carbs': '66 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '140g chicken breast OR 120g paneer',
            '1 tsp oil, cumin, garlic, turmeric'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Prepare tempered dal.',
            'Cook chicken or paneer with spices.',
            'Steam vegetables and plate together.'
        ],
        'why_this_meal': 'A wholesome Indian staple combining complete animal/dairy protein with lentil fiber and carbohydrates.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery and caloric surplus.',
            'cut': 'High protein promotes fullness and muscle retention.',
            'maintain': 'Balanced nutrition for everyday vitality.',
            'strength': 'Powers heavy resistance workouts.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu or fish'},
            {'original': 'White rice', 'alternative': 'Brown rice'}
        ],
        'nutrition_tip': 'Eating a colorful vegetable medley ensures a wide spectrum of antioxidant phytonutrients.'
    },

    'rice + dal + mixed vegetables + grilled chicken/paneer': {
        'description': 'Fluffy steamed rice, spiced yellow dal, sautéed mixed vegetables, and grilled chicken or paneer.',
        'calories': 550,
        'protein': '38 g',
        'carbs': '66 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '140g grilled chicken OR 120g paneer',
            '1 tsp oil, garlic, cumin'
        ],
        'preparation_steps': [
            'Steam rice.',
            'Simmer seasoned dal.',
            'Grill marinated chicken or paneer.',
            'Sauté vegetables and serve as a complete meal.'
        ],
        'why_this_meal': 'Supplies high biological value protein, complex carbohydrates, and fiber for active recovery.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Fish fillet or firm tofu'},
            {'original': 'Rice', 'alternative': 'Brown rice or roti'}
        ],
        'nutrition_tip': 'Grilling protein on a ridged pan allows excess fat to drain away while imparting great smoky flavor.'
    },

    'rice + dal + vegetables + grilled chicken/tofu': {
        'description': 'Steamed rice, wholesome yellow dal, fresh garden vegetables, and grilled chicken breast or firm tofu.',
        'calories': 530,
        'protein': '38 g',
        'carbs': '64 g',
        'fat': '14 g',
        'fiber': '9 g',
        'ingredients': [
            '1 cup cooked rice',
            '1 cup dal',
            '1 cup vegetables',
            '140g grilled chicken OR 150g firm tofu',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Grill chicken or tofu with seasonings.',
            'Prepare tempered dal.',
            'Steam vegetables and serve hot.'
        ],
        'why_this_meal': 'Supplies complete proteins, sustained energy, and essential vitamins for active fitness routines.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding and glycogen restoration.',
            'cut': 'High protein and dietary fiber keep you full during a calorie deficit.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids and minerals for lifting power.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer or fish'},
            {'original': 'Rice', 'alternative': 'Brown rice or quinoa'}
        ],
        'nutrition_tip': 'Tofu is rich in isoflavones, which support cardiovascular health and cellular recovery.'
    },

    'rice + fish/chicken + dal + vegetables': {
        'description': 'Steamed rice served with pan-seared fish or chicken breast, comforting dal, and mixed vegetables.',
        'calories': 540,
        'protein': '40 g',
        'carbs': '64 g',
        'fat': '13 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '150g fish fillet OR chicken breast',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil, lemon, herbs, garlic'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Pan-sear fish or chicken with garlic, lemon, and spices.',
            'Simmer yellow dal.',
            'Steam vegetables and serve together.'
        ],
        'why_this_meal': 'Combines lean animal proteins, plant-based lentil fiber, and clean carbohydrates for complete recovery.',
        'goal_benefits': {
            'bulk': 'High protein and clean carbohydrates support muscle recovery.',
            'cut': 'Lean protein keeps calories low and satiety high.',
            'maintain': 'Balanced macronutrient profile for everyday active living.',
            'strength': 'Delivers essential BCAAs and iron for power training.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Fish / Chicken', 'alternative': 'Paneer (120g) or tofu (150g)'},
            {'original': 'White rice', 'alternative': 'Brown rice'}
        ],
        'nutrition_tip': 'Fish provides iodine and selenium, which support healthy thyroid function and metabolic rate.'
    },

    'rice + fish/chicken + vegetables': {
        'description': 'Steamed rice paired with grilled fish or tender chicken breast and sautéed vegetables.',
        'calories': 510,
        'protein': '38 g',
        'carbs': '60 g',
        'fat': '14 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup cooked rice',
            '150g fish fillet OR chicken breast',
            '1.5 cups mixed sautéed vegetables',
            '1 tsp oil, lemon, herbs'
        ],
        'preparation_steps': [
            'Steam rice.',
            'Grill fish or chicken until tender.',
            'Sauté mixed vegetables in 1 tsp oil.',
            'Serve as a clean, protein-packed lunch.'
        ],
        'why_this_meal': 'Clean, easily digestible protein and carbohydrates that restore glycogen without causing digestive sluggishness.',
        'goal_benefits': {
            'bulk': 'Provides clean calories and amino acids for muscle building.',
            'cut': 'High protein content preserves lean mass while staying in a deficit.',
            'maintain': 'Maintains energy balance and body composition.',
            'strength': 'Supplies essential nutrients to power heavy lifting.',
            'fitness': 'Clean whole-food fuel for daily training.'
        },
        'substitutions': [
            {'original': 'Fish / Chicken', 'alternative': 'Paneer or firm tofu'},
            {'original': 'Rice', 'alternative': 'Brown rice or sweet potato'}
        ],
        'nutrition_tip': 'White fish like cod or tilapia is one of the lowest-fat protein sources available.'
    },

    'rice + fish/chicken/paneer + dal + vegetables': {
        'description': 'A versatile high-protein lunch of steamed rice, fish, chicken, or paneer, accompanied by dal and vegetables.',
        'calories': 550,
        'protein': '39 g',
        'carbs': '65 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g fish, chicken, or paneer',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil/ghee, cumin, garlic, turmeric'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Cook your choice of protein (fish, chicken, or paneer) with aromatic spices.',
            'Simmer yellow dal.',
            'Steam vegetables and serve hot.'
        ],
        'why_this_meal': 'A complete balanced plate providing diverse amino acids, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery and caloric surplus.',
            'cut': 'High protein promotes fullness and muscle retention.',
            'maintain': 'Balanced nutrition for everyday vitality.',
            'strength': 'Powers heavy resistance workouts.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Protein choice', 'alternative': 'Tofu or soya chunks'},
            {'original': 'Rice', 'alternative': 'Brown rice or roti'}
        ],
        'nutrition_tip': 'Rotating protein sources between fish, chicken, and dairy ensures a wider variety of trace minerals.'
    },

    'rice + fish/paneer + vegetables': {
        'description': 'Steamed rice served with pan-seared fish or fresh paneer and sautéed garden vegetables.',
        'calories': 520,
        'protein': '36 g',
        'carbs': '60 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g fish fillet OR 120g fresh paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil, garlic, lemon, herbs'
        ],
        'preparation_steps': [
            'Cook rice until fluffy.',
            'Pan-sear fish or paneer until golden and cooked.',
            'Sauté vegetables lightly with herbs and garlic.',
            'Serve together hot.'
        ],
        'why_this_meal': 'Combines bioavailable protein, clean carbohydrates, and essential micronutrients.',
        'goal_benefits': {
            'bulk': 'Provides clean fuel for muscle rebuilding.',
            'cut': 'High protein and fiber prevent hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Fish / Paneer', 'alternative': 'Chicken breast or firm tofu'},
            {'original': 'Rice', 'alternative': 'Brown rice or millets'}
        ],
        'nutrition_tip': 'Squeeze lemon over fish or paneer to enhance flavor and aid calcium absorption.'
    },

    'rice + fish/paneer + vegetables + dal': {
        'description': 'Steamed rice, pan-seared fish or paneer, yellow lentil dal, and mixed vegetables.',
        'calories': 550,
        'protein': '38 g',
        'carbs': '65 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '140g fish fillet OR 120g paneer',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil, cumin, garlic'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Cook fish or paneer with mild spices.',
            'Simmer yellow dal with garlic-cumin tempering.',
            'Steam vegetables and plate together.'
        ],
        'why_this_meal': 'A complete balanced plate providing dual proteins, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery and caloric surplus.',
            'cut': 'High protein promotes fullness and muscle retention.',
            'maintain': 'Balanced nutrition for everyday vitality.',
            'strength': 'Powers heavy resistance workouts.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Fish / Paneer', 'alternative': 'Chicken breast or tofu'},
            {'original': 'Rice', 'alternative': 'Brown rice or roti'}
        ],
        'nutrition_tip': 'Fish provides essential vitamin D, which works synergistically with the calcium in dal and paneer.'
    },

    'rice + paneer + dal + mixed vegetables': {
        'description': 'Steamed rice served with fresh pan-seared paneer cubes, yellow lentil dal, and mixed vegetables.',
        'calories': 550,
        'protein': '26 g',
        'carbs': '68 g',
        'fat': '18 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '100g fresh paneer',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp ghee, cumin, turmeric, garlic'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Pan-sear paneer cubes with turmeric and salt.',
            'Simmer yellow dal with spices.',
            'Steam mixed vegetables and serve as a complete vegetarian lunch.'
        ],
        'why_this_meal': 'Combines dairy casein protein with plant dal protein, creating a complete vegetarian amino acid profile.',
        'goal_benefits': {
            'bulk': 'Quality vegetarian calories and protein to support muscle growth.',
            'cut': 'High fiber and protein keep appetite suppressed.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies calcium and magnesium to support muscular strength.',
            'fitness': 'Clean, wholesome vegetarian fuel for active living.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Firm tofu or boiled chickpeas'},
            {'original': 'White rice', 'alternative': 'Brown rice or 2 rotis'}
        ],
        'nutrition_tip': 'Paneer provides CLA (conjugated linoleic acid), a beneficial fatty acid that supports metabolic health.'
    },

    'rice + paneer/chicken + dal + vegetables': {
        'description': 'Steamed rice, pan-seared paneer or chicken, spiced yellow dal, and sautéed vegetables.',
        'calories': 550,
        'protein': '38 g',
        'carbs': '66 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '1 cup cooked rice',
            '120g paneer OR 140g chicken breast',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '1 tsp oil/ghee, spices'
        ],
        'preparation_steps': [
            'Cook rice.',
            'Cook paneer or chicken with seasonings.',
            'Simmer yellow dal.',
            'Steam vegetables and serve together.'
        ],
        'why_this_meal': 'Supplies a rich blend of complete proteins, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'High protein and clean carbohydrates support muscle rebuilding.',
            'cut': 'High protein keeps hunger under control during a cut.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Paneer / Chicken', 'alternative': 'Tofu (150g) or fish fillet'},
            {'original': 'Rice', 'alternative': 'Brown rice or chapati'}
        ],
        'nutrition_tip': 'Adding a pinch of cumin and ginger aids the digestion of lentils and dairy proteins.'
    },

    # -------------------------------------------------------------
    # DINNER ITEMS (ROTI, CHAPATI, SOUP, PANEER, CHICKEN, DAL, CURD)
    # -------------------------------------------------------------
    '2 roti + paneer/tofu + mixed vegetables': {
        'description': 'Two fresh whole-wheat rotis served with spiced paneer or firm tofu and a hearty portion of mixed vegetables.',
        'calories': 480,
        'protein': '24 g',
        'carbs': '54 g',
        'fat': '18 g',
        'fiber': '8 g',
        'ingredients': [
            '2 medium whole-wheat rotis (chapatis)',
            '120g fresh paneer cubes OR 140g firm tofu',
            '1.5 cups mixed vegetables (cauliflower, carrots, beans, bell peppers)',
            '1 tsp oil or ghee, cumin, turmeric, coriander, and garam masala'
        ],
        'preparation_steps': [
            'Knead whole-wheat dough and roll into 2 thin rotis, cooking on a dry tawa until puffed.',
            'Sauté cumin, onions, ginger, and garlic in 1 tsp oil.',
            'Add mixed vegetables, turmeric, coriander powder, and paneer/tofu cubes; cook covered on low heat until tender.',
            'Serve hot rotis alongside the fragrant vegetable-protein curry.'
        ],
        'why_this_meal': 'A balanced, light dinner combining complex whole-grain carbohydrates with steady-digesting protein and high fiber.',
        'goal_benefits': {
            'bulk': 'Provides clean carbohydrates and quality protein to sustain overnight muscle recovery.',
            'cut': 'Controlled portion of rotis with abundant vegetables and protein ensures fullness without calorie excess.',
            'maintain': 'Maintains lean body mass and promotes steady overnight blood glucose.',
            'strength': 'Supplies magnesium, B-vitamins, and calcium to aid muscle relaxation and repair during sleep.',
            'fitness': 'Light, digestible dinner that supports deep sleep and morning workout readiness.'
        },
        'substitutions': [
            {'original': 'Paneer / Tofu', 'alternative': 'Grilled chicken breast (130g) or soya chunks'},
            {'original': 'Whole-wheat roti', 'alternative': 'Multigrain roti, jowar roti, or bajra roti'}
        ],
        'nutrition_tip': 'Avoid brushing rotis with heavy butter; a drop of pure ghee is sufficient for aroma and fat-soluble vitamin absorption.'
    },

    'chapati + chicken + vegetables + dal': {
        'description': 'Whole-wheat chapatis served with tender cooked chicken breast, spiced yellow dal, and sautéed vegetables.',
        'calories': 530,
        'protein': '40 g',
        'carbs': '60 g',
        'fat': '14 g',
        'fiber': '8 g',
        'ingredients': [
            '2 whole-wheat chapatis',
            '140g chicken breast',
            '1 cup yellow lentil dal',
            '1 cup mixed vegetables',
            '1 tsp oil, garlic, cumin, spices'
        ],
        'preparation_steps': [
            'Cook 2 whole-wheat chapatis on a hot griddle until puffed.',
            'Cook chicken breast with onions, ginger, garlic, and Indian spices.',
            'Simmer yellow dal tempered with cumin.',
            'Steam vegetables and serve together as a satisfying dinner.'
        ],
        'why_this_meal': 'High protein and complex carbohydrates support nighttime muscle protein synthesis and recovery.',
        'goal_benefits': {
            'bulk': 'Provides 40g of protein to fuel overnight muscle repair and growth.',
            'cut': 'High protein content keeps you satiated, preventing late-night snacking.',
            'maintain': 'Maintains body composition and metabolic health.',
            'strength': 'Delivers BCAAs and iron to recover from heavy resistance training.',
            'fitness': 'Optimal clean dinner that fuels morning workouts.'
        },
        'substitutions': [
            {'original': 'Chicken', 'alternative': 'Paneer (120g) or fish fillet'},
            {'original': 'Chapati', 'alternative': 'Jowar or ragi roti'}
        ],
        'nutrition_tip': 'Eating dinner 2–3 hours before bedtime ensures digestion is completed for deeper, restorative sleep.'
    },

    'chapati + chicken/fish + vegetables': {
        'description': 'Warm whole-wheat chapatis paired with grilled chicken or pan-seared fish and garden vegetables.',
        'calories': 480,
        'protein': '38 g',
        'carbs': '50 g',
        'fat': '14 g',
        'fiber': '7 g',
        'ingredients': [
            '2 whole-wheat chapatis',
            '140g chicken breast OR 150g fish fillet',
            '1.5 cups mixed vegetables',
            '1 tsp oil, lemon, herbs, garlic'
        ],
        'preparation_steps': [
            'Make 2 thin whole-wheat chapatis.',
            'Grill chicken or pan-sear fish with lemon, garlic, and herbs.',
            'Sauté mixed vegetables in 1 tsp oil until tender.',
            'Serve warm.'
        ],
        'why_this_meal': 'Clean, lean protein with low saturated fat and moderate complex carbohydrates for optimal evening nutrition.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery with complete bioavailable proteins.',
            'cut': 'Lean protein and fiber keep calories low while maximizing satiety.',
            'maintain': 'Maintains lean body mass and steady metabolism.',
            'strength': 'Supplies essential amino acids for overnight tissue repair.',
            'fitness': 'Light, nutritious dinner that prepares the body for morning exercise.'
        },
        'substitutions': [
            {'original': 'Chicken / Fish', 'alternative': 'Paneer or firm tofu'},
            {'original': 'Chapati', 'alternative': 'Multigrain roti or brown rice'}
        ],
        'nutrition_tip': 'Fish provides light, fast-digesting protein that won’t disrupt sleep quality.'
    },

    'chapati + chicken/paneer + vegetables': {
        'description': 'Whole-wheat chapatis served with spiced chicken breast or fresh paneer and sautéed vegetables.',
        'calories': 500,
        'protein': '36 g',
        'carbs': '52 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '2 whole-wheat chapatis',
            '130g chicken breast OR 120g paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil/ghee, garlic, spices'
        ],
        'preparation_steps': [
            'Roll and cook 2 fresh chapatis.',
            'Cook chicken or paneer with spices and garlic.',
            'Sauté vegetables until crisp-tender.',
            'Plate together for a wholesome dinner.'
        ],
        'why_this_meal': 'Combines complex whole-wheat carbohydrates with complete protein and essential vitamins.',
        'goal_benefits': {
            'bulk': 'Provides protein and carbohydrates that can support training energy and muscle recovery.',
            'cut': 'Provides protein and fiber that can help support fullness while maintaining a balanced meal.',
            'maintain': 'Provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
            'strength': 'Provides protein and carbohydrates that can support training performance and recovery.',
            'fitness': 'Provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Firm tofu or fish'},
            {'original': 'Chapati', 'alternative': 'Oats roti or jowar roti'}
        ],
        'nutrition_tip': 'Using freshly ground whole-wheat flour retains the wheat germ, which is packed with vitamin E and zinc.'
    },

    'chapati + dal + mixed vegetables + paneer/tofu': {
        'description': 'Whole-wheat chapatis served with yellow dal, mixed vegetable sabzi, and fresh paneer or tofu.',
        'calories': 520,
        'protein': '26 g',
        'carbs': '64 g',
        'fat': '17 g',
        'fiber': '9 g',
        'ingredients': [
            '2 whole-wheat chapatis',
            '1 cup yellow dal',
            '1 cup mixed vegetables',
            '100g paneer OR 130g tofu',
            '1 tsp oil/ghee, cumin, spices'
        ],
        'preparation_steps': [
            'Make 2 fresh chapatis.',
            'Simmer yellow dal tempered with cumin.',
            'Sauté paneer/tofu and mixed vegetables with mild spices.',
            'Serve warm as a balanced vegetarian dinner.'
        ],
        'why_this_meal': 'A complete vegetarian dinner providing complementary amino acids, complex carbs, and digestive fiber.',
        'goal_benefits': {
            'bulk': 'Supports overnight muscle recovery with diverse amino acids.',
            'cut': 'High fiber keeps you full and prevents midnight cravings.',
            'maintain': 'Maintains metabolic balance and body composition.',
            'strength': 'Supplies calcium, magnesium, and plant protein for recovery.',
            'fitness': 'Clean, wholesome vegetarian fuel for everyday vitality.'
        },
        'substitutions': [
            {'original': 'Paneer / Tofu', 'alternative': 'Grilled chicken or soya chunks'},
            {'original': 'Chapati', 'alternative': 'Multigrain roti'}
        ],
        'nutrition_tip': 'Paneer and lentils together provide both fast and slow digesting proteins for sustained recovery.'
    },

    'chapati + dal + paneer/tofu + vegetables': {
        'description': 'Warm chapatis served with lentil dal, pan-seared paneer or tofu, and garden vegetables.',
        'calories': 510,
        'protein': '25 g',
        'carbs': '62 g',
        'fat': '17 g',
        'fiber': '9 g',
        'ingredients': [
            '2 chapatis',
            '1 cup dal',
            '100g paneer or tofu',
            '1 cup mixed vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Make 2 chapatis.',
            'Prepare dal and sauté paneer/tofu with vegetables.',
            'Serve together hot.'
        ],
        'why_this_meal': 'Balanced vegetarian macronutrients supporting steady blood glucose and muscle maintenance.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding.',
            'cut': 'High protein and dietary fiber keep you full during a cut.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids for lifting recovery.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Paneer / Tofu', 'alternative': 'Chicken breast or fish'},
            {'original': 'Chapati', 'alternative': 'Ragi roti'}
        ],
        'nutrition_tip': 'Lentils provide dietary folate, which supports cellular DNA repair during sleep.'
    },

    'chapati + dal + vegetable curry + curd': {
        'description': 'Traditional dinner of chapatis, comforting dal, spiced vegetable curry, and cooling fresh curd.',
        'calories': 490,
        'protein': '20 g',
        'carbs': '66 g',
        'fat': '15 g',
        'fiber': '9 g',
        'ingredients': [
            '2 whole-wheat chapatis',
            '1 cup yellow dal',
            '1 cup mixed vegetable curry',
            '1/2 cup fresh plain curd',
            '1 tsp oil/ghee, cumin, turmeric'
        ],
        'preparation_steps': [
            'Cook 2 whole-wheat chapatis.',
            'Simmer yellow dal and prepare a vegetable curry.',
            'Serve with a side of cool probiotic curd.'
        ],
        'why_this_meal': 'Light, digestible dinner providing probiotics, prebiotic fibers, and balanced carbohydrates.',
        'goal_benefits': {
            'bulk': 'Easily digestible meal that supports gut health and recovery.',
            'cut': 'Low in saturated fat and high in fiber; perfect for cutting.',
            'maintain': 'Maintains digestive harmony and steady blood sugar.',
            'strength': 'Provides essential electrolytes and calcium.',
            'fitness': 'Promotes gut health and morning readiness.'
        },
        'substitutions': [
            {'original': 'Curd', 'alternative': 'Greek yogurt (adds 8g protein)'},
            {'original': 'Vegetable curry', 'alternative': 'Palak paneer or bhindi masala'}
        ],
        'nutrition_tip': 'Eating curd at dinner promotes tryptophan uptake, a precursor to melatonin that aids sleep.'
    },

    'chapati + fish/paneer + vegetables': {
        'description': 'Whole-wheat chapatis served with pan-seared fish or fresh paneer and sautéed vegetables.',
        'calories': 490,
        'protein': '36 g',
        'carbs': '50 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '2 chapatis',
            '140g fish fillet OR 120g paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil, garlic, lemon, herbs'
        ],
        'preparation_steps': [
            'Make 2 chapatis.',
            'Cook fish or paneer with spices and garlic.',
            'Sauté mixed vegetables.',
            'Serve together hot.'
        ],
        'why_this_meal': 'Delivers complete protein, complex carbs, and vitamins for evening restoration.',
        'goal_benefits': {
            'bulk': 'Provides clean calories and amino acids for muscle rebuilding.',
            'cut': 'High protein and fiber prevent hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Fish / Paneer', 'alternative': 'Chicken breast or tofu'},
            {'original': 'Chapati', 'alternative': 'Multigrain roti'}
        ],
        'nutrition_tip': 'Fish is light on the stomach, allowing your body to focus energy on muscular recovery rather than heavy digestion.'
    },

    'chapati + paneer + vegetable curry + curd': {
        'description': 'Whole-wheat chapatis served with paneer cubes, vegetable curry, and fresh probiotic curd.',
        'calories': 530,
        'protein': '24 g',
        'carbs': '60 g',
        'fat': '20 g',
        'fiber': '8 g',
        'ingredients': [
            '2 chapatis',
            '100g fresh paneer',
            '1 cup vegetable curry',
            '1/2 cup fresh curd',
            '1 tsp ghee, spices'
        ],
        'preparation_steps': [
            'Cook 2 chapatis.',
            'Prepare vegetable-paneer curry with mild spices.',
            'Serve with a side of chilled curd.'
        ],
        'why_this_meal': 'Combines dairy casein protein, live probiotics, and vegetable antioxidants for complete evening wellness.',
        'goal_benefits': {
            'bulk': 'Supplies healthy fats and slow-digesting protein for overnight muscle support.',
            'cut': 'Protein and fiber keep you satisfied throughout the night.',
            'maintain': 'Maintains energy balance and gut microbiome health.',
            'strength': 'Supplies calcium and magnesium to support muscular relaxation.',
            'fitness': 'Nutritious vegetarian fuel for recovery.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Tofu or soya chunks'},
            {'original': 'Curd', 'alternative': 'Greek yogurt'}
        ],
        'nutrition_tip': 'Casein protein from paneer and curd provides a steady release of amino acids over 6–8 hours of sleep.'
    },

    'chapati + paneer curry + vegetables': {
        'description': 'Warm chapatis served with a rich paneer curry and a generous side of mixed vegetables.',
        'calories': 520,
        'protein': '23 g',
        'carbs': '56 g',
        'fat': '21 g',
        'fiber': '7 g',
        'ingredients': [
            '2 chapatis',
            '120g paneer in tomato-onion curry',
            '1 cup sautéed vegetables',
            '1 tsp oil/ghee, spices'
        ],
        'preparation_steps': [
            'Cook 2 whole-wheat chapatis.',
            'Simmer paneer in a spiced tomato-onion curry.',
            'Sauté mixed vegetables and serve together.'
        ],
        'why_this_meal': 'Supplies sustained slow-release protein from paneer and complex carbohydrates from whole grains.',
        'goal_benefits': {
            'bulk': 'Calorie-dense clean meal that supports muscle repair.',
            'cut': 'Portion-controlled satisfying dinner with good protein.',
            'maintain': 'Maintains steady blood glucose and muscle tone.',
            'strength': 'Supplies calcium and phosphorus for bone and muscle integrity.',
            'fitness': 'Comforting, wholesome vegetarian fuel.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Tofu or soya chunks'},
            {'original': 'Chapati', 'alternative': 'Jowar or ragi roti'}
        ],
        'nutrition_tip': 'Cook paneer curry in a tomato-onion base rather than heavy cream to keep saturated fat in check.'
    },

    'roti + chicken/paneer + vegetables + curd': {
        'description': 'Two whole-wheat rotis served with chicken or paneer, mixed vegetables, and cool probiotic curd.',
        'calories': 520,
        'protein': '36 g',
        'carbs': '52 g',
        'fat': '18 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '130g chicken breast OR 120g paneer',
            '1 cup mixed vegetables',
            '1/2 cup fresh curd',
            '1 tsp oil/ghee, garlic, spices'
        ],
        'preparation_steps': [
            'Make 2 fresh rotis.',
            'Cook chicken or paneer with spices and garlic.',
            'Sauté mixed vegetables.',
            'Serve with a bowl of cool curd.'
        ],
        'why_this_meal': 'Dual protein sources (meat/dairy + curd) and probiotics support complete overnight recovery.',
        'goal_benefits': {
            'bulk': 'Supports muscle hypertrophy with complete bioavailable proteins.',
            'cut': 'High protein and fiber keep appetite under control.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies essential nutrients to support recovery from lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu (150g) or fish'},
            {'original': 'Roti', 'alternative': 'Multigrain chapati'}
        ],
        'nutrition_tip': 'Curd contains lactic acid which helps soothe digestive inflammation after a day of training.'
    },

    'roti + chicken/tofu + dal': {
        'description': 'Whole-wheat rotis served with spiced chicken breast or firm tofu and a bowl of comforting dal.',
        'calories': 500,
        'protein': '38 g',
        'carbs': '56 g',
        'fat': '13 g',
        'fiber': '8 g',
        'ingredients': [
            '2 rotis',
            '140g chicken breast OR 150g firm tofu',
            '1 cup yellow dal',
            '1 tsp oil, cumin, garlic, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook chicken or tofu with seasonings.',
            'Simmer yellow dal tempered with cumin and garlic.',
            'Serve together hot.'
        ],
        'why_this_meal': 'High protein, low fat, and complex carbohydrates provide the ideal fuel for post-workout restoration.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding.',
            'cut': 'High protein keeps hunger under control during a cut.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids for lifting recovery.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer (120g) or fish fillet'},
            {'original': 'Roti', 'alternative': 'Jowar or ragi roti'}
        ],
        'nutrition_tip': 'Yellow moong dal is the easiest lentil to digest, making it ideal for evening meals.'
    },

    'roti + chicken/tofu + mixed vegetables': {
        'description': 'Fresh whole-wheat rotis served with seasoned chicken breast or tofu and sautéed mixed vegetables.',
        'calories': 480,
        'protein': '36 g',
        'carbs': '50 g',
        'fat': '14 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '140g chicken breast OR 150g tofu',
            '1.5 cups mixed vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Cook 2 rotis.',
            'Sauté chicken or tofu with garlic and spices.',
            'Stir-fry mixed vegetables.',
            'Plate together for a clean dinner.'
        ],
        'why_this_meal': 'Lean protein and low-GI carbohydrates support steady blood sugar and muscle maintenance.',
        'goal_benefits': {
            'bulk': 'Provides clean fuel for muscle rebuilding.',
            'cut': 'High protein and fiber prevent hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Fish fillet or paneer'},
            {'original': 'Roti', 'alternative': 'Multigrain roti'}
        ],
        'nutrition_tip': 'Pairing protein with mixed vegetables ensures a balanced glycemic response.'
    },

    'roti + chicken/tofu + vegetable curry': {
        'description': 'Whole-wheat rotis served with chicken or tofu simmered in a spiced vegetable curry.',
        'calories': 500,
        'protein': '36 g',
        'carbs': '52 g',
        'fat': '15 g',
        'fiber': '8 g',
        'ingredients': [
            '2 rotis',
            '130g chicken OR 150g tofu',
            '1.5 cups vegetable curry',
            '1 tsp oil, ginger, garlic, spices'
        ],
        'preparation_steps': [
            'Make 2 fresh rotis.',
            'Simmer chicken/tofu in a spiced vegetable-rich curry gravy.',
            'Serve hot with the rotis.'
        ],
        'why_this_meal': 'Supplies lean protein, complex carbohydrates, and rich vegetable micronutrients.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding.',
            'cut': 'High protein keeps hunger under control during a cut.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids for lifting recovery.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Chicken / Tofu', 'alternative': 'Paneer or fish'},
            {'original': 'Roti', 'alternative': 'Oats roti'}
        ],
        'nutrition_tip': 'Ginger and garlic in the curry base stimulate digestion and support blood circulation.'
    },

    'roti + dal + mixed vegetables': {
        'description': 'A comforting traditional dinner of whole-wheat rotis, yellow lentil dal, and mixed vegetables.',
        'calories': 450,
        'protein': '18 g',
        'carbs': '65 g',
        'fat': '12 g',
        'fiber': '9 g',
        'ingredients': [
            '2 whole-wheat rotis',
            '1 cup yellow dal',
            '1.5 cups mixed vegetables',
            '1 tsp ghee, cumin, turmeric, garlic'
        ],
        'preparation_steps': [
            'Make 2 fresh rotis.',
            'Simmer dal with cumin-garlic tempering.',
            'Sauté mixed vegetables with mild spices.',
            'Serve together hot.'
        ],
        'why_this_meal': 'A light, high-fiber vegetarian dinner that is easy on digestion and promotes restful sleep.',
        'goal_benefits': {
            'bulk': 'Easily digestible carbohydrates and plant protein for recovery.',
            'cut': 'Low-calorie, high-fiber dinner that supports fat loss.',
            'maintain': 'Maintains digestive harmony and metabolic stability.',
            'strength': 'Provides essential minerals and steady overnight energy.',
            'fitness': 'Clean, light vegetarian fuel that supports morning readiness.'
        },
        'substitutions': [
            {'original': 'Yellow dal', 'alternative': 'Sprouted moong dal or rajma'},
            {'original': 'Roti', 'alternative': 'Jowar or bajra roti'}
        ],
        'nutrition_tip': 'Whole grains and lentils together form a complete amino acid profile with all 9 essential amino acids.'
    },

    'roti + dal + vegetables': {
        'description': 'Fresh whole-wheat rotis, comforting lentil dal, and garden vegetables.',
        'calories': 440,
        'protein': '17 g',
        'carbs': '64 g',
        'fat': '12 g',
        'fiber': '9 g',
        'ingredients': [
            '2 rotis',
            '1 cup dal',
            '1 cup vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Simmer dal.',
            'Sauté vegetables and serve hot.'
        ],
        'why_this_meal': 'Light, digestible plant-based nutrition for clean evening recovery.',
        'goal_benefits': {
            'bulk': 'Provides clean fuel for muscle rebuilding.',
            'cut': 'High fiber prevents hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support recovery.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Dal', 'alternative': 'Chana dal or paneer bhurji'},
            {'original': 'Roti', 'alternative': 'Multigrain chapati'}
        ],
        'nutrition_tip': 'Adding a pinch of asafoetida (hing) when tempering dal prevents gas and bloating.'
    },

    'roti + fish + vegetables + curd': {
        'description': 'Whole-wheat rotis served with pan-seared fish fillet, mixed vegetables, and fresh probiotic curd.',
        'calories': 500,
        'protein': '38 g',
        'carbs': '50 g',
        'fat': '15 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '150g white fish or salmon',
            '1 cup mixed vegetables',
            '1/2 cup fresh curd',
            '1 tsp olive oil, garlic, lemon, herbs'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Pan-sear fish with garlic, lemon, and herbs.',
            'Sauté mixed vegetables.',
            'Serve with a bowl of cool curd.'
        ],
        'why_this_meal': 'Omega-3 rich fish protein combined with probiotics, fiber, and complex carbohydrates for optimal recovery.',
        'goal_benefits': {
            'bulk': 'High protein and anti-inflammatory fats support overnight muscle repair.',
            'cut': 'Lean fish protein keeps calories low and metabolic rate high.',
            'maintain': 'Supports cardiovascular health and lean muscle tone.',
            'strength': 'Omega-3s reduce post-training joint and muscle inflammation.',
            'fitness': 'A premier light dinner that promotes deep sleep and recovery.'
        },
        'substitutions': [
            {'original': 'Fish', 'alternative': 'Chicken breast or paneer'},
            {'original': 'Roti', 'alternative': 'Multigrain roti'}
        ],
        'nutrition_tip': 'Fish is digested much faster than red meat, ensuring restful, undisturbed sleep.'
    },

    'roti + fish/tofu + vegetables + curd': {
        'description': 'Whole-wheat rotis, pan-seared fish or firm tofu, mixed vegetables, and fresh curd.',
        'calories': 490,
        'protein': '36 g',
        'carbs': '50 g',
        'fat': '15 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '140g fish OR 150g firm tofu',
            '1 cup vegetables',
            '1/2 cup curd',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook fish or tofu with seasonings.',
            'Sauté vegetables and serve with fresh curd.'
        ],
        'why_this_meal': 'Supplies lean protein, probiotics, and complex carbs for overnight cellular restoration.',
        'goal_benefits': {
            'bulk': 'Clean fuel that supports muscle rebuilding.',
            'cut': 'High protein and dietary fiber keep you full during a cut.',
            'maintain': 'Maintains energy balance and metabolic health.',
            'strength': 'Supplies essential amino acids for lifting recovery.',
            'fitness': 'Promotes endurance and clean athletic nutrition.'
        },
        'substitutions': [
            {'original': 'Fish / Tofu', 'alternative': 'Chicken breast or paneer'},
            {'original': 'Roti', 'alternative': 'Jowar roti'}
        ],
        'nutrition_tip': 'Probiotic curd at dinner helps maintain a healthy balance of gut bacteria overnight.'
    },

    'roti + paneer + vegetable curry + curd': {
        'description': 'Whole-wheat rotis, paneer cubes in vegetable curry, and fresh probiotic curd.',
        'calories': 520,
        'protein': '24 g',
        'carbs': '58 g',
        'fat': '20 g',
        'fiber': '8 g',
        'ingredients': [
            '2 rotis',
            '100g fresh paneer',
            '1 cup vegetable curry',
            '1/2 cup curd',
            '1 tsp ghee, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Prepare paneer and vegetable curry.',
            'Serve with fresh curd.'
        ],
        'why_this_meal': 'Slow-release casein protein from paneer and curd provides sustained amino acids through the night.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery with slow-digesting proteins.',
            'cut': 'Keeps you full and prevents nighttime hunger.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies calcium and magnesium to support recovery.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Tofu or soya chunks'},
            {'original': 'Curd', 'alternative': 'Greek yogurt'}
        ],
        'nutrition_tip': 'Casein protein prevents muscle catabolism during long overnight fasting periods.'
    },

    'roti + paneer + vegetables': {
        'description': 'Whole-wheat rotis served with spiced paneer cubes and sautéed mixed vegetables.',
        'calories': 480,
        'protein': '22 g',
        'carbs': '52 g',
        'fat': '19 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '120g fresh paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil/ghee, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Sauté paneer with spices and mixed vegetables.',
            'Serve hot.'
        ],
        'why_this_meal': 'Provides complete vegetarian protein, calcium, and complex carbohydrates.',
        'goal_benefits': {
            'bulk': 'Provides clean calories and amino acids for muscle rebuilding.',
            'cut': 'High protein and fiber prevent hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Firm tofu or chicken breast'},
            {'original': 'Roti', 'alternative': 'Multigrain chapati'}
        ],
        'nutrition_tip': 'Paneer contains conjugated linoleic acid (CLA), which supports healthy fat metabolism.'
    },

    'roti + paneer + vegetables + curd': {
        'description': 'Whole-wheat rotis served with pan-seared paneer, mixed vegetables, and fresh curd.',
        'calories': 520,
        'protein': '25 g',
        'carbs': '54 g',
        'fat': '20 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '110g paneer',
            '1 cup vegetables',
            '1/2 cup curd',
            '1 tsp ghee, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook paneer with vegetables and spices.',
            'Serve with fresh curd.'
        ],
        'why_this_meal': 'Supplies slow-release casein protein, live probiotics, and dietary vegetable fiber.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery with slow-digesting proteins.',
            'cut': 'Keeps you full and prevents nighttime hunger.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies calcium and magnesium to support recovery.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Paneer', 'alternative': 'Tofu or chicken breast'},
            {'original': 'Curd', 'alternative': 'Greek yogurt'}
        ],
        'nutrition_tip': 'Curd and paneer together supply optimal bioavailable calcium for bone strength.'
    },

    'roti + paneer/chicken + dal + vegetables': {
        'description': 'Whole-wheat rotis served with chicken or paneer, spiced yellow dal, and mixed vegetables.',
        'calories': 530,
        'protein': '38 g',
        'carbs': '58 g',
        'fat': '16 g',
        'fiber': '8 g',
        'ingredients': [
            '2 rotis',
            '130g chicken OR 110g paneer',
            '1 cup dal',
            '1 cup vegetables',
            '1 tsp oil/ghee, cumin, garlic'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook chicken or paneer with spices.',
            'Simmer yellow dal.',
            'Serve with steamed vegetables.'
        ],
        'why_this_meal': 'A complete balanced plate providing dual proteins, complex carbohydrates, and gut-healthy fiber.',
        'goal_benefits': {
            'bulk': 'High protein and clean carbohydrates support muscle recovery.',
            'cut': 'High protein promotes fullness and muscle retention.',
            'maintain': 'Balanced nutrition for everyday vitality.',
            'strength': 'Powers heavy resistance workouts.',
            'fitness': 'Optimal fuel for workout endurance and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu or fish'},
            {'original': 'Roti', 'alternative': 'Multigrain roti'}
        ],
        'nutrition_tip': 'Tempering dal with garlic and cumin enhances nutrient absorption and aids digestion.'
    },

    'roti + paneer/chicken + vegetables': {
        'description': 'Warm whole-wheat rotis served with seasoned chicken breast or fresh paneer and sautéed vegetables.',
        'calories': 490,
        'protein': '36 g',
        'carbs': '50 g',
        'fat': '16 g',
        'fiber': '7 g',
        'ingredients': [
            '2 rotis',
            '130g chicken OR 110g paneer',
            '1.5 cups mixed vegetables',
            '1 tsp oil, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook chicken or paneer with seasonings.',
            'Sauté mixed vegetables and serve hot.'
        ],
        'why_this_meal': 'Combines lean protein with whole-grain carbohydrates and rich vegetable fiber.',
        'goal_benefits': {
            'bulk': 'Provides clean fuel for muscle rebuilding.',
            'cut': 'High protein and fiber prevent hunger cravings.',
            'maintain': 'Maintains steady energy and body composition.',
            'strength': 'Supplies essential nutrients to support intense lifting.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Tofu or fish'},
            {'original': 'Roti', 'alternative': 'Jowar or ragi roti'}
        ],
        'nutrition_tip': 'Sautéing vegetables lightly keeps their natural crunch and micronutrient density intact.'
    },

    'roti + paneer/tofu + vegetables + curd': {
        'description': 'Fresh rotis, pan-seared paneer or firm tofu, mixed vegetables, and cool curd.',
        'calories': 510,
        'protein': '25 g',
        'carbs': '54 g',
        'fat': '19 g',
        'fiber': '8 g',
        'ingredients': [
            '2 rotis',
            '110g paneer OR 140g tofu',
            '1 cup vegetables',
            '1/2 cup curd',
            '1 tsp ghee/oil, spices'
        ],
        'preparation_steps': [
            'Make 2 rotis.',
            'Cook paneer or tofu with vegetables and spices.',
            'Serve with fresh plain curd.'
        ],
        'why_this_meal': 'Supplies slow-digesting protein, gut probiotics, and high-fiber complex carbohydrates.',
        'goal_benefits': {
            'bulk': 'Supports muscle recovery with slow-digesting proteins.',
            'cut': 'Keeps you full and prevents nighttime hunger.',
            'maintain': 'Maintains lean body mass and steady energy.',
            'strength': 'Supplies calcium and magnesium to support recovery.',
            'fitness': 'Wholesome fuel for daily workouts and recovery.'
        },
        'substitutions': [
            {'original': 'Paneer / Tofu', 'alternative': 'Chicken breast or fish'},
            {'original': 'Curd', 'alternative': 'Greek yogurt'}
        ],
        'nutrition_tip': 'Tofu contains all 9 essential amino acids with lower saturated fat than paneer.'
    },

    'vegetable soup + 1-2 roti + protein': {
        'description': 'A warming bowl of garden vegetable soup served with 1–2 whole-wheat rotis and lean protein (chicken, paneer, or tofu).',
        'calories': 440,
        'protein': '32 g',
        'carbs': '46 g',
        'fat': '12 g',
        'fiber': '8 g',
        'ingredients': [
            '1.5 cups hearty vegetable soup (tomatoes, carrots, beans, spinach)',
            '1–2 whole-wheat rotis',
            '120g grilled chicken breast OR 100g paneer / tofu',
            '1 tsp olive oil, black pepper, herbs'
        ],
        'preparation_steps': [
            'Simmer mixed vegetables with garlic, ginger, vegetable broth, and black pepper until tender.',
            'Grill chicken breast, paneer, or tofu cubes lightly with herbs.',
            'Cook 1–2 fresh whole-wheat rotis on a dry griddle.',
            'Serve the steaming vegetable soup alongside warm rotis and protein.'
        ],
        'why_this_meal': 'An exceptionally light, hydrating, and micronutrient-dense dinner that promotes cellular hydration and recovery.',
        'goal_benefits': {
            'bulk': 'Easily digestible meal that replenishes hydration and provides clean protein before bed.',
            'cut': 'High soup volume and fiber create intense satiety for minimal calories; top-tier cutting dinner.',
            'maintain': 'Maintains hydration, electrolyte balance, and lean muscle mass.',
            'strength': 'Supplies potassium, magnesium, and bioavailable amino acids for muscle relaxation.',
            'fitness': 'Promotes deep recovery, cardiovascular health, and morning lightness.'
        },
        'substitutions': [
            {'original': 'Protein', 'alternative': 'Boiled eggs (2–3) or sprouted moong'},
            {'original': 'Roti', 'alternative': 'Whole-grain toast or boiled sweet potato'}
        ],
        'nutrition_tip': 'Starting your dinner with a clear vegetable soup can naturally reduce subsequent calorie intake by up to 20%.'
    },

    'vegetable soup + dal + 1-2 roti': {
        'description': 'A soothing, light dinner of vegetable soup, protein-rich yellow dal, and 1–2 whole-wheat rotis.',
        'calories': 420,
        'protein': '18 g',
        'carbs': '58 g',
        'fat': '10 g',
        'fiber': '9 g',
        'ingredients': [
            '1.5 cups vegetable soup',
            '1 cup yellow lentil dal',
            '1–2 whole-wheat rotis',
            '1 tsp oil, cumin, garlic, black pepper'
        ],
        'preparation_steps': [
            'Prepare a comforting vegetable soup seasoned with black pepper.',
            'Simmer yellow dal with light cumin and garlic tempering.',
            'Cook 1–2 thin rotis and serve warm with the soup and dal.'
        ],
        'why_this_meal': 'Extremely easy to digest, deeply hydrating, and rich in bioavailable plant minerals.',
        'goal_benefits': {
            'bulk': 'Hydrating and light, assisting in digestive rest between heavy training days.',
            'cut': 'Low-calorie high-volume dinner that ensures a calorie deficit with zero hunger.',
            'maintain': 'Maintains digestive harmony, hydration, and steady blood sugar.',
            'strength': 'Supplies potassium and magnesium to prevent nocturnal muscle cramps.',
            'fitness': 'Clean, restorative dinner that leaves you feeling light and energized the next morning.'
        },
        'substitutions': [
            {'original': 'Yellow dal', 'alternative': 'Paneer cubes in dal or chicken broth'},
            {'original': 'Roti', 'alternative': 'Brown rice (1/2 cup)'}
        ],
        'nutrition_tip': 'Black pepper in the soup contains piperine, which boosts the absorption of vital micronutrients from the vegetables.'
    },

    'vegetable soup + paneer/chicken + 1-2 roti': {
        'description': 'Warming vegetable soup served with grilled chicken breast or paneer and 1–2 whole-wheat rotis.',
        'calories': 460,
        'protein': '34 g',
        'carbs': '48 g',
        'fat': '13 g',
        'fiber': '8 g',
        'ingredients': [
            '1.5 cups fresh vegetable soup',
            '130g grilled chicken OR 110g paneer',
            '1–2 whole-wheat rotis',
            '1 tsp olive oil, herbs, black pepper'
        ],
        'preparation_steps': [
            'Simmer mixed vegetables in seasoned broth until rich and flavorful.',
            'Grill chicken breast or paneer with black pepper and herbs.',
            'Cook 1–2 fresh rotis.',
            'Serve the warm soup, rotis, and protein together.'
        ],
        'why_this_meal': 'Delivers high-density complete protein in a light, high-volume, highly hydrating format.',
        'goal_benefits': {
            'bulk': 'Provides clean protein and hydration for overnight recovery.',
            'cut': 'High volume and protein keep you full while maintaining a strong calorie deficit.',
            'maintain': 'Maintains lean body mass and promotes restful sleep.',
            'strength': 'Supplies amino acids and electrolytes to support muscle tissue repair.',
            'fitness': 'Optimal light dinner for athletic individuals training in the mornings.'
        },
        'substitutions': [
            {'original': 'Chicken / Paneer', 'alternative': 'Firm tofu or fish fillet'},
            {'original': 'Roti', 'alternative': 'Sourdough toast or brown rice'}
        ],
        'nutrition_tip': 'Vegetable soup provides vital electrolytes like potassium and sodium, helping maintain cellular fluid balance.'
    }
}


def get_goal_benefit_text(meal_name, goal_code, why_text=None):
    """
    Generate dynamic goal benefit text matching requirements for all 5 goals:
    bulk, cut, maintain, strength, fitness.
    """
    goal_code = (goal_code or 'fitness').lower()
    
    goal_labels = {
        'bulk': 'Build Muscle / Bulk',
        'cut': 'Lose Fat / Cut',
        'maintain': 'Maintain Weight',
        'strength': 'Build Strength',
        'fitness': 'General Fitness',
    }
    
    # Standard high quality baseline phrasing matching exact user prompt requirements
    default_benefits = {
        'bulk': 'This meal provides protein and carbohydrates that can support training energy and muscle recovery.',
        'cut': 'This meal provides protein and fiber that can help support fullness while maintaining a balanced meal.',
        'maintain': 'This meal provides a balanced combination of protein, carbohydrates, fats and fiber for everyday nutrition.',
        'strength': 'This meal provides protein and carbohydrates that can support training performance and recovery.',
        'fitness': 'This meal provides a balanced combination of whole foods, protein, carbohydrates and fiber for everyday fitness.',
    }
    
    # Try normalized lookup in registry first
    key = normalize_meal_name(meal_name)
    if key in MEAL_DETAILS_REGISTRY:
        reg_benefits = MEAL_DETAILS_REGISTRY[key].get('goal_benefits', {})
        if goal_code in reg_benefits:
            return reg_benefits[goal_code]
            
    return default_benefits.get(goal_code, default_benefits['fitness'])


def get_meal_details(meal, profile=None):
    """
    Retrieve or construct complete rich detail dictionary for any DietMeal or food name.
    """
    if not meal:
        return None
        
    meal_type = getattr(meal, 'meal_type', 'breakfast')
    meal_name = getattr(meal, 'name', str(meal))
    user_goal = getattr(profile, 'goal', getattr(meal, 'goal', 'fitness'))
    
    # Check if this is the hydration item
    if meal_type == 'hydration' or 'water' in meal_name.lower():
        data = dict(HYDRATION_DATA)
        data['goal_benefit'] = get_goal_benefit_text('hydration', user_goal)
        data['user_goal_display'] = {
            'bulk': 'Build Muscle / Bulk',
            'cut': 'Lose Fat / Cut',
            'maintain': 'Maintain Weight',
            'strength': 'Build Strength',
            'fitness': 'General Fitness',
        }.get(user_goal, 'General Fitness')
        return data

    key = normalize_meal_name(meal_name)
    
    # 1. Exact match in curated registry
    if key in MEAL_DETAILS_REGISTRY:
        item = dict(MEAL_DETAILS_REGISTRY[key])
        item['name'] = meal_name
        item['meal_type'] = meal_type
        item['is_hydration'] = False
        item['goal_benefit'] = item.get('goal_benefits', {}).get(user_goal, get_goal_benefit_text(meal_name, user_goal))
        item['user_goal_display'] = {
            'bulk': 'Build Muscle / Bulk',
            'cut': 'Lose Fat / Cut',
            'maintain': 'Maintain Weight',
            'strength': 'Build Strength',
            'fitness': 'General Fitness',
        }.get(user_goal, 'General Fitness')
        return item
        
    # 2. Fuzzy match against registry keys
    for reg_key, reg_data in MEAL_DETAILS_REGISTRY.items():
        if reg_key in key or key in reg_key:
            item = dict(reg_data)
            item['name'] = meal_name
            item['meal_type'] = meal_type
            item['is_hydration'] = False
            item['goal_benefit'] = item.get('goal_benefits', {}).get(user_goal, get_goal_benefit_text(meal_name, user_goal))
            item['user_goal_display'] = {
                'bulk': 'Build Muscle / Bulk',
                'cut': 'Lose Fat / Cut',
                'maintain': 'Maintain Weight',
                'strength': 'Build Strength',
                'fitness': 'General Fitness',
            }.get(user_goal, 'General Fitness')
            return item

    # 3. Dynamic fallback for any unforeseen meal name
    # Build sensible realistic values
    fallback = {
        'name': meal_name,
        'meal_type': meal_type,
        'is_hydration': False,
        'description': f'A nutrient-dense fitness meal pairing wholesome ingredients for balanced everyday nutrition.',
        'calories': 460 if meal_type in ('breakfast', 'lunch', 'dinner') else 220,
        'protein': '26 g' if meal_type in ('breakfast', 'lunch', 'dinner') else '10 g',
        'carbs': '55 g' if meal_type in ('breakfast', 'lunch', 'dinner') else '26 g',
        'fat': '14 g' if meal_type in ('breakfast', 'lunch', 'dinner') else '8 g',
        'fiber': '7 g' if meal_type in ('breakfast', 'lunch', 'dinner') else '4 g',
        'ingredients': [f'{part.strip()}' for part in re.split(r'[\+,/]', meal_name) if part.strip()],
        'preparation_steps': [
            f'Prepare fresh ingredients cleanly for {meal_name}.',
            'Cook with minimal healthy oil (olive oil or ghee) over medium heat.',
            'Season with fresh herbs, black pepper, and minimal sea salt.',
            'Plate thoughtfully and enjoy warm with adequate hydration.'
        ],
        'why_this_meal': f'This meal delivers a wholesome combination of protein, dietary fiber, and complex carbohydrates to support training recovery.',
        'goal_benefit': get_goal_benefit_text(meal_name, user_goal),
        'user_goal_display': {
            'bulk': 'Build Muscle / Bulk',
            'cut': 'Lose Fat / Cut',
            'maintain': 'Maintain Weight',
            'strength': 'Build Strength',
            'fitness': 'General Fitness',
        }.get(user_goal, 'General Fitness'),
        'substitutions': [
            {'original': 'Primary protein', 'alternative': 'Paneer / Tofu / Chicken breast'},
            {'original': 'Primary grain', 'alternative': 'Whole-grain roti / Brown rice / Oats'}
        ],
        'nutrition_tip': 'Focus on whole, minimally processed ingredients and chew your food thoroughly for optimal nutrient absorption.'
    }
    return fallback
