from django.core.management.base import BaseCommand

from workout.models import DietMeal


# The plans are data, not HTML: every goal gets its own seven-day set of meal slots.
ROTATIONS = {
    'bulk': [
        ('Oats, eggs and banana', 'Greek yogurt, fruit and nuts', 'Rice with chicken / paneer and vegetables', 'Banana with peanut butter', 'Roti with paneer / chicken and vegetables'),
        ('Idli, sambar, eggs and fruit', 'Milk / soy milk with almonds', 'Rice with fish / tofu and vegetables', 'Curd with banana', 'Chapati with dal, paneer and vegetables'),
        ('Poha, vegetable omelette and fruit', 'Greek yogurt with fruit', 'Brown rice with chicken / paneer and vegetables', 'Roasted chana and orange', 'Roti with chicken / tofu and vegetables'),
        ('Dosa, sambar and curd', 'Banana and mixed nuts', 'Rice with rajma and vegetables', 'Peanut butter toast with fruit', 'Chapati with fish / paneer and vegetables'),
        ('Oats with milk, fruit and seeds', 'Curd with walnuts', 'Rice with fish / paneer and vegetables', 'Yogurt with banana', 'Roti with paneer and vegetables'),
        ('Upma, eggs and fruit', 'Fruit with peanuts', 'Rice with chicken / tofu and vegetables', 'Roasted chana with curd', 'Chapati with mixed vegetables and dal'),
        ('Idli, sambar and fruit', 'Greek yogurt and nuts', 'Rice with dal, paneer and vegetables', 'Banana with peanut butter', 'Roti with paneer / chicken and vegetables'),
    ],
    'cut': [
        ('Eggs, whole-grain toast and fruit', 'Apple with yogurt', 'Brown rice with lean protein and vegetables', 'Fruit with a small serving of nuts', 'Roti with dal and vegetables'),
        ('Vegetable oats and curd', 'Guava with Greek yogurt', 'Rice with fish / tofu and vegetables', 'Roasted chana', 'Chapati with paneer / chicken salad'),
        ('Poha with eggs and fruit', 'Orange with yogurt', 'Brown rice with dal and vegetables', 'Apple with almonds', 'Roti with tofu / chicken and vegetables'),
        ('Dosa, sambar and fruit', 'Curd with berries / seasonal fruit', 'Rice with paneer / chicken and vegetables', 'Fruit with peanuts', 'Chapati with dal and mixed vegetables'),
        ('Oats, milk and fruit', 'Apple with curd', 'Rice with fish / tofu and vegetables', 'Yogurt with banana', 'Roti with paneer and vegetables'),
        ('Vegetable upma and eggs', 'Fruit with nuts', 'Brown rice with chicken / paneer and vegetables', 'Roasted chana with lemon', 'Vegetable soup with protein and roti'),
        ('Idli, sambar and curd', 'Greek yogurt with fruit', 'Rice with dal and vegetables', 'Guava with peanuts', 'Roti with paneer / chicken and vegetables'),
    ],
    'maintain': [
        ('Oats with milk, fruit and seeds', 'Curd with fruit and nuts', 'Rice with dal / chicken and vegetables', 'Banana with peanuts', 'Roti with paneer / tofu and vegetables'),
        ('Idli, sambar and fruit', 'Milk / soy milk with nuts', 'Rice with fish / paneer and vegetables', 'Curd with fruit', 'Chapati with dal and vegetables'),
        ('Poha, eggs / tofu and fruit', 'Greek yogurt with fruit', 'Brown rice with rajma and vegetables', 'Roasted chana', 'Roti with chicken / paneer and vegetables'),
        ('Dosa, sambar and curd', 'Banana with nuts', 'Rice with dal and vegetables', 'Peanut butter toast', 'Chapati with fish / tofu and vegetables'),
        ('Oats, milk and banana', 'Curd with walnuts', 'Rice with paneer / chicken and vegetables', 'Fruit with yogurt', 'Roti with mixed vegetables and dal'),
        ('Upma, eggs / tofu and fruit', 'Fruit with peanuts', 'Rice with chicken / paneer and vegetables', 'Roasted chana with curd', 'Chapati with vegetables and paneer'),
        ('Idli, sambar and fruit', 'Greek yogurt and nuts', 'Rice with dal, paneer and vegetables', 'Banana with peanut butter', 'Roti with paneer / chicken and vegetables'),
    ],
}

MEAL_TYPES = ('breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner', 'hydration')


class Command(BaseCommand):
    help = 'Create or update the seven-day personalized diet meal catalogue.'

    def handle(self, *args, **options):
        count = 0
        for goal_index, goal in enumerate(('bulk', 'cut', 'maintain', 'strength', 'fitness')):
            source = ROTATIONS['bulk'] if goal == 'strength' else ROTATIONS['maintain'] if goal == 'fitness' else ROTATIONS[goal]
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
        goal_text = {'bulk': 'supports muscle-building energy with protein, carbohydrates and colourful produce', 'cut': 'keeps a satisfying balance of protein, fibre and whole foods', 'maintain': 'balances protein, carbohydrates, healthy fats and produce', 'strength': 'supports training energy and protein intake across the day', 'fitness': 'supports steady energy and balanced everyday nutrition'}[goal]
        return f'{name} {goal_text}.'
