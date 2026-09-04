from django.core.management.base import BaseCommand

from workout.models import DietMeal


# The plans are data, not HTML: every goal gets its own seven-day set of meal slots.
ROTATIONS = {
    'bulk': [
        ('Oats with milk, banana + 2–3 eggs', 'Greek yogurt + almonds', 'Rice + chicken/paneer + vegetables', 'Peanut butter whole-grain toast + fruit', 'Roti + paneer/chicken + dal + vegetables'),
        ('3–4 eggs + whole-grain toast + banana', 'Curd + mixed nuts', 'Brown rice + chicken/tofu + dal + vegetables', 'Banana + peanut butter', 'Chapati + paneer curry + vegetables'),
        ('Vegetable dosa + sambar + eggs', 'Greek yogurt + banana + walnuts', 'Rice + fish/paneer + vegetables', 'Sprouts + fruit', 'Roti + chicken/tofu + dal'),
        ('Vegetable upma + eggs + curd', 'Milk + banana + almonds', 'Rice + chicken/paneer + rajma + vegetables', 'Peanut butter sandwich + fruit', 'Chapati + fish/paneer + vegetables'),
        ('Poha with peanuts + eggs + fruit', 'Greek yogurt + nuts', 'Brown rice + chicken/tofu + dal + vegetables', 'Milk + banana + peanut butter', 'Roti + paneer/chicken + vegetables'),
        ('Oats + milk + banana + peanut butter + eggs', 'Curd + fruit + almonds', 'Rice + fish/chicken/paneer + dal + vegetables', 'Sprouts + whole-grain toast', 'Chapati + chicken/paneer + vegetables'),
        ('Idli + sambar + eggs + fruit', 'Greek yogurt + banana + nuts', 'Rice + chicken/paneer + dal + vegetables', 'Peanut butter toast + milk', 'Roti + paneer/tofu + vegetables + curd'),
    ],
    'cut': [
        ('Vegetable upma + 2 eggs', 'Apple + a small handful of almonds', 'Brown rice + chicken/paneer + vegetables', 'Roasted chana + lemon', 'Vegetable soup + paneer/chicken + 1–2 roti'),
        ('Idli + sambar + curd', 'Greek yogurt + fruit', 'Rice + dal + vegetables + grilled chicken/tofu', 'Guava + peanuts', 'Roti + paneer/chicken + vegetables'),
        ('Eggs + whole-grain toast + fruit', 'Apple + curd', 'Brown rice + lean chicken/tofu + vegetables', 'Fruit + a small handful of nuts', 'Roti + dal + mixed vegetables'),
        ('Vegetable oats + curd', 'Guava + Greek yogurt', 'Rice + fish/paneer + vegetables', 'Roasted chana', 'Vegetable soup + 1–2 roti + protein'),
        ('Poha with vegetables + eggs', 'Orange + yogurt', 'Brown rice + dal + vegetables + chicken/tofu', 'Apple + almonds', 'Roti + paneer + vegetables'),
        ('Dosa + sambar + eggs', 'Fruit + curd', 'Rice + fish/chicken + vegetables', 'Roasted chana + fruit', 'Roti + dal + vegetables'),
        ('Oats + milk + fruit + eggs', 'Greek yogurt + fruit', 'Brown rice + chicken/paneer + vegetables', 'Guava + a small handful of peanuts', 'Vegetable soup + dal + 1–2 roti'),
    ],
    'maintain': [
        ('Vegetable dosa + sambar + 2 eggs', 'Apple + Greek yogurt', 'Rice + dal + mixed vegetables + grilled chicken/paneer', 'Roasted chana + seasonal fruit', '2 roti + paneer/tofu + mixed vegetables'),
        ('Oats with milk + banana + almonds', 'Guava + curd', 'Brown rice + chicken/tofu + vegetables', 'Fruit + small handful of peanuts', 'Chapati + dal + vegetable curry + curd'),
        ('Idli + sambar + curd + fruit', 'Greek yogurt + mixed fruit', 'Rice + fish/paneer + vegetables', 'Apple + almonds', 'Roti + chicken/tofu + vegetable curry'),
        ('Vegetable poha + 2 eggs + fruit', 'Banana + curd', 'Brown rice + dal + vegetables + paneer', 'Roasted chana + fruit', 'Chapati + chicken/fish + vegetables'),
        ('Vegetable upma + eggs + curd', 'Orange + Greek yogurt', 'Rice + chicken/tofu + dal + vegetables', 'Apple + small handful of nuts', 'Roti + paneer + vegetables + curd'),
        ('Whole-grain toast + vegetable omelette + fruit', 'Guava + peanuts', 'Brown rice + fish/chicken + vegetables', 'Greek yogurt + banana', 'Chapati + dal + mixed vegetables + paneer/tofu'),
        ('Dosa + sambar + eggs + fruit', 'Curd + almonds + seasonal fruit', 'Rice + paneer/chicken + dal + vegetables', 'Roasted chana + banana', 'Roti + fish/tofu + vegetables + curd'),
    ],
    'strength': [
        ('Oats with milk + banana + 3 eggs', 'Greek yogurt + banana + walnuts', 'Chicken + rice + dal + mixed vegetables', 'Peanut butter whole-grain toast + fruit', 'Roti + chicken/paneer + vegetables + curd'),
        ('Vegetable omelette + whole-grain toast + fruit', 'Milk + banana + almonds', 'Brown rice + fish + vegetables + dal', 'Roasted chana + fruit', 'Chapati + paneer + vegetable curry + curd'),
        ('Idli + sambar + 3 eggs + fruit', 'Greek yogurt + nuts', 'Rice + chicken + dal + vegetables', 'Banana + peanut butter', 'Roti + fish + vegetables + curd'),
        ('Poha with peanuts + eggs + curd', 'Milk + banana + almonds', 'Rice + paneer + dal + mixed vegetables', 'Whole-grain toast + Greek yogurt', 'Chapati + chicken + vegetables + dal'),
        ('Dosa + sambar + eggs + curd', 'Banana + Greek yogurt + walnuts', 'Brown rice + chicken + vegetables + dal', 'Roasted chana + fruit', 'Roti + paneer/tofu + vegetables + curd'),
        ('Oats + milk + banana + peanut butter + eggs', 'Curd + fruit + almonds', 'Rice + fish/chicken + dal + vegetables', 'Peanut butter whole-grain toast + banana', 'Chapati + chicken/paneer + vegetables'),
        ('Vegetable upma + eggs + curd + fruit', 'Greek yogurt + banana + nuts', 'Rice + chicken/paneer + dal + vegetables', 'Milk + banana + peanut butter', 'Roti + fish/tofu + vegetables + curd'),
    ],
    'fitness': [
        ('Vegetable upma + 2 eggs + curd', 'Apple + Greek yogurt', 'Rice + dal + mixed vegetables + chicken/paneer', 'Roasted chana + seasonal fruit', '2 roti + paneer/tofu + mixed vegetables'),
        ('Idli + sambar + curd + fruit', 'Guava + a small handful of almonds', 'Brown rice + chicken/tofu + vegetables', 'Banana + peanuts', 'Chapati + dal + vegetable curry + curd'),
        ('Oats with milk + banana + nuts', 'Greek yogurt + seasonal fruit', 'Rice + fish/paneer + vegetables + dal', 'Roasted chana + fruit', 'Roti + chicken/tofu + mixed vegetables'),
        ('Vegetable poha + 2 eggs + fruit', 'Apple + curd', 'Brown rice + dal + paneer + vegetables', 'Greek yogurt + banana', 'Chapati + chicken/fish + vegetables'),
        ('Dosa + sambar + eggs + fruit', 'Guava + Greek yogurt', 'Rice + chicken/tofu + dal + vegetables', 'Apple + almonds', 'Roti + paneer + vegetable curry + curd'),
        ('Whole-grain toast + vegetable omelette + fruit', 'Banana + curd + a few nuts', 'Brown rice + fish/chicken + vegetables', 'Roasted chana + seasonal fruit', 'Chapati + dal + paneer/tofu + vegetables'),
        ('Vegetable oats + eggs + curd', 'Orange + Greek yogurt', 'Rice + paneer/chicken + dal + vegetables', 'Fruit + mixed nuts', 'Roti + fish/tofu + vegetables + curd'),
    ],
}

MEAL_TYPES = ('breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner', 'hydration')


class Command(BaseCommand):
    help = 'Create or update the seven-day personalized diet meal catalogue.'

    def handle(self, *args, **options):
        count = 0
        for goal, source in ROTATIONS.items():
            for day, meals in enumerate(source):
                complete = (*meals, 'Keep water nearby and drink regularly throughout the day.')
                for slot, (meal_type, name) in enumerate(zip(MEAL_TYPES, complete)):
                    from workout.diet_image_utils import get_diet_image_path
                    image = get_diet_image_path(name, meal_type)
                    description = self.description(goal, meal_type, name)
                    DietMeal.objects.update_or_create(
                        goal=goal, day_of_week=day, meal_type=meal_type,
                        defaults={'name': name, 'description': description, 'image': image},
                    )
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Created or updated {count} diet meal slots.'))

    @staticmethod
    def description(goal, meal_type, name):
        if meal_type == 'hydration':
            return 'A gentle hydration reminder; individual needs vary with weather and activity.'
        goal_text = {
            'bulk': 'supports muscle-building energy with protein, carbohydrates and colourful produce',
            'cut': 'keeps a satisfying balance of protein, fibre and whole foods',
            'maintain': 'balances protein, carbohydrates, healthy fats and produce',
            'strength': 'supports training energy and protein intake across the day',
            'fitness': 'supports steady energy and balanced everyday nutrition',
        }[goal]
        return f'{name} {goal_text}.'
