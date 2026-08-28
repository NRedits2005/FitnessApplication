from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.functions import Lower
from .exercise_cleanup import normalize_name


def format_weight_display(value):
    """
    Format weight for clean display without unnecessary decimals and with thousands separators.
    Examples:
        0 -> '0'
        1200 -> '1,200'
        1200.5 -> '1,200.5'
        4700 -> '4,700'
    """
    if value is None:
        return '0'
    try:
        val = Decimal(str(value))
    except Exception:
        return '0'

    if val == 0:
        return '0'
    if val % 1 == 0:
        return f"{int(val):,}"
    return f"{val:,.2f}".rstrip('0').rstrip('.')


def calculate_exercise_volume(exercise_entry):
    """
    Calculate the total weight lifted for a single WorkoutExercise:
    Weight × Repetitions × Completed Sets
    Bodyweight exercises or exercises with no external weight contribute 0 kg.
    Only completed sets count.
    """
    if exercise_entry.exercise.is_bodyweight or exercise_entry.weight is None:
        return Decimal('0')

    # A WorkoutSet is the record of work actually performed.  Planned values
    # must never add volume: a user may abandon a workout before completing a
    # single set.  Summing each completed set also correctly handles a
    # different weight or rep count on every set without double-counting.
    return sum(
        (
            Decimal(str(workout_set.reps_completed))
            * (workout_set.weight if workout_set.weight is not None else Decimal('0'))
            for workout_set in exercise_entry.sets.all()
            if workout_set.completed
        ),
        Decimal('0'),
    )


def calculate_workout_volume(workout):
    """
    Calculate the total weight lifted across all exercises in a workout.
    """
    entries = workout.workout_exercises.all()
    total = Decimal('0')
    for entry in entries:
        total += calculate_exercise_volume(entry)
    return total


def calculate_user_total_volume(user):
    """
    Calculate the user's accumulated total weight lifted across all COMPLETED workouts.
    Only includes the given user's completed workouts.
    """
    if not user or not user.is_authenticated:
        return Decimal('0')

    completed_workouts = Workout.objects.filter(
        user=user,
        completed=True
    ).prefetch_related('workout_exercises__exercise', 'workout_exercises__sets')

    total = Decimal('0')
    for workout in completed_workouts:
        total += calculate_workout_volume(workout)
    return total


class Exercise(models.Model):
    class EquipmentType(models.TextChoices):
        BODYWEIGHT = 'bodyweight', 'Bodyweight'
        BARBELL = 'barbell', 'Barbell'
        DUMBBELL = 'dumbbell', 'Dumbbell'
        KETTLEBELL = 'kettlebell', 'Kettlebell'
        CABLE = 'cable', 'Cable'
        MACHINE = 'machine', 'Machine'
        RESISTANCE_BAND = 'resistance_band', 'Resistance band'
        PULLUP_BAR = 'pullup_bar', 'Pull-up bar'
        BENCH = 'bench', 'Bench'
        PLATE = 'plate', 'Plate-loaded'
        STEP = 'step', 'Step / Platform'
        JUMP_ROPE = 'jump_rope', 'Jump Rope'
        OTHER = 'other', 'Other'

    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    class GenderCategory(models.TextChoices):
        ALL = 'all', 'All'
        FEMALE = 'female', 'Female'
        MALE = 'male', 'Male'

    name = models.CharField(max_length=120)
    body_part = models.CharField(max_length=40, default='Full Body')
    equipment_type = models.CharField(max_length=20, choices=EquipmentType.choices, default=EquipmentType.OTHER)
    category = models.CharField(max_length=40)
    description = models.TextField()
    instructions = models.TextField()
    muscles_targeted = models.CharField(max_length=255)
    beginner_tips = models.TextField(blank=True)
    is_bodyweight = models.BooleanField(default=False)
    image = models.CharField(max_length=255, blank=True, help_text='Local visual URL (filled by the seed command).')
    created_at = models.DateTimeField(auto_now_add=True)

    # --- New fields for Women's Fitness & gender-based visibility ---
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE)
    gender_category = models.CharField(max_length=10, choices=GenderCategory.choices, default=GenderCategory.ALL)
    recommended_sets = models.CharField(max_length=30, blank=True, default='')
    recommended_reps = models.CharField(max_length=30, blank=True, default='')
    recommended_duration = models.CharField(max_length=40, blank=True, default='')
    recommended_rest = models.CharField(max_length=30, blank=True, default='')
    is_beginner_friendly = models.BooleanField(default=False)

    class Meta:
        ordering = ['category', 'name']
        constraints = [models.UniqueConstraint(Lower('name'), name='unique_exercise_name_ci')]

    def save(self, *args, **kwargs):
        self.name = normalize_name(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_image_url(self, gender=None):
        """Return gender-matched image URL from static/workout/images/(male|female), auto-creating PNG if missing."""
        if not gender:
            gender = getattr(self, 'active_gender', None)
        if not gender:
            gender = 'female' if self.gender_category == 'female' else 'male'
        from .image_utils import get_exercise_image_path
        return get_exercise_image_path(self.name, self.category, gender)

    @property
    def body_part_tag(self):
        """User-friendly body-part label for Women's Fitness exercise cards."""
        TAG_MAP = {
            'Bodyweight Squat': 'Quadriceps', 'Bodyweight Lunge': 'Legs',
            'Chair Squat': 'Quadriceps', 'Glute Bridge': 'Glutes',
            'Single-Leg Glute Bridge': 'Glutes', 'Hip Thrust': 'Glutes',
            'Donkey Kicks': 'Glutes', 'Fire Hydrants': 'Glutes',
            'Sumo Squat': 'Inner Thighs', 'Bulgarian Split Squat': 'Legs',
            'Reverse Lunge': 'Glutes', 'Walking Lunges': 'Legs',
            'Step-Ups': 'Legs', 'Standing Leg Raises': 'Hips',
            'Goblet Squat': 'Glutes', 'Romanian Deadlift': 'Hamstrings',
            'Curtsy Lunge': 'Glutes',
            'Plank': 'Core', 'Knee Plank': 'Core', 'Side Plank': 'Obliques',
            'Dead Bug': 'Core', 'Bird Dog': 'Core',
            'Bicycle Crunch': 'Core', 'Bicycle Crunches': 'Core',
            'Crunch': 'Core', 'Reverse Crunches': 'Lower Abs',
            'Leg Raise': 'Core', 'Leg Raises': 'Lower Abs',
            'Mountain Climbers': 'Core', 'Russian Twist': 'Core',
            'Sit-Up': 'Core', 'Heel Taps': 'Obliques',
            'Hanging Leg Raise': 'Core',
            'Dumbbell Bicep Curl': 'Biceps', 'Hammer Curl': 'Biceps',
            'Dumbbell Row': 'Back', 'Resistance-Band Row': 'Back',
            'Dumbbell Shoulder Press': 'Shoulders',
            'Dumbbell Lateral Raise': 'Shoulders',
            'Dumbbell Front Raise': 'Shoulders',
            'Overhead Tricep Extension': 'Triceps',
            'Tricep Kickback': 'Triceps',
            'Wall Push-Ups': 'Chest', 'Knee Push-Ups': 'Chest',
            'Incline Push-Ups': 'Chest', 'Standard Push-Ups': 'Chest',
            'Jumping Jacks': 'Full Body', 'High Knees': 'Legs',
            'Butt Kicks': 'Hamstrings', 'Running': 'Legs',
            'Jogging': 'Legs', 'Cycling': 'Legs',
            'Skipping Rope': 'Full Body', 'Marching in Place': 'Legs',
            'Step Jacks': 'Full Body', 'Dancing / Cardio Dance': 'Full Body',
            'Brisk Walking': 'Full Body',
            'Butterfly Stretch': 'Inner Thighs', 'Cat-Cow Stretch': 'Back',
            'Chest Stretch': 'Chest', "Child's Pose": 'Back',
            'Cobra Stretch': 'Abdominals', 'Full-Body Stretch': 'Full Body',
            'Glute Stretch': 'Glutes', 'Hamstring Stretch': 'Hamstrings',
            'Hip Flexor Stretch': 'Hip Flexors',
            'Shoulder Stretch': 'Shoulders',
        }
        if self.name in TAG_MAP:
            return TAG_MAP[self.name]
        # Fallback: use the first entry in muscles_targeted, or body_part
        if self.muscles_targeted:
            return self.muscles_targeted.split(',')[0].strip()
        return self.body_part


class Workout(models.Model):
    user = models.ForeignKey(User, related_name='workouts', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'Workout on {self.date}'

    @property
    def duration_seconds(self):
        if not self.completed_at:
            return None
        return max(0, int((self.completed_at - self.created_at).total_seconds()))

    @property
    def total_volume(self):
        return calculate_workout_volume(self)

    @property
    def total_volume_display(self):
        return format_weight_display(self.total_volume)


class UserProfile(models.Model):
    class Goal(models.TextChoices):
        BULK = 'bulk', 'Build Muscle / Bulk'
        CUT = 'cut', 'Lose Fat / Cut'
        MAINTAIN = 'maintain', 'Maintain Weight'
        STRENGTH = 'strength', 'Build Strength'
        FITNESS = 'fitness', 'General Fitness'

    user = models.OneToOneField(User, related_name='fitness_profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=80, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    # Null is retained only for legacy profiles that have not yet selected a
    # gender.  The profile form exposes only Male and Female choices.
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female')], null=True, blank=True, default=None)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    goal = models.CharField(max_length=20, choices=Goal.choices, default=Goal.FITNESS)
    workout_location = models.CharField(max_length=10, choices=[('gym','Gym'),('home','Home')], default='home')
    experience_level = models.CharField(max_length=20, choices=[('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')], default='beginner')
    home_equipment = models.JSONField(default=list, blank=True)
    profile_completed = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    current_streak = models.PositiveIntegerField(default=0); longest_streak = models.PositiveIntegerField(default=0); last_workout_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)

    @property
    def bmi(self):
        if not self.height_cm or not self.weight_kg: return None
        return round(float(self.weight_kg) / (float(self.height_cm) / 100) ** 2, 1)

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None: return ''
        return 'Underweight' if bmi < 18.5 else 'Healthy range' if bmi < 25 else 'Overweight' if bmi < 30 else 'Obesity'

    @property
    def total_weight_lifted(self):
        return calculate_user_total_volume(self.user)

    @property
    def total_weight_lifted_display(self):
        return format_weight_display(self.total_weight_lifted)

    @property
    def equipment_display_list(self):
        labels = {
            'bodyweight': 'No equipment',
            'dumbbell': 'Dumbbells',
            'band': 'Resistance Bands',
            'pullup_bar': 'Pull-up Bar',
            'kettlebell': 'Kettlebell',
            'bench': 'Bench',
            'mat': 'Yoga Mat',
            'jump_rope': 'Jump Rope',
        }
        if not self.home_equipment:
            return ['No equipment (Bodyweight)']
        return [labels.get(item, str(item).replace('_', ' ').title()) for item in self.home_equipment]


class DailyDietPlan(models.Model):
    user = models.ForeignKey(User, related_name='diet_plans', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.localdate)
    goal = models.CharField(max_length=20)
    breakfast = models.CharField(max_length=255); morning_snack = models.CharField(max_length=255)
    lunch = models.CharField(max_length=255); evening_snack = models.CharField(max_length=255)
    dinner = models.CharField(max_length=255); hydration = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','date'], name='unique_daily_diet_plan')]

class DietMeal(models.Model):
    meal_type = models.CharField(max_length=20, choices=[('breakfast','Breakfast'),('morning_snack','Mid-morning snack'),('lunch','Lunch'),('evening_snack','Evening snack'),('dinner','Dinner'),('hydration','Hydration')])
    name = models.CharField(max_length=160)
    description = models.CharField(max_length=255)
    image = models.CharField(max_length=500)
    goal = models.CharField(max_length=20, default='all')
    day_of_week = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['meal_type','goal','day_of_week'], name='unique_diet_meal_slot')]

    def __str__(self):
        return f'{self.name} ({self.get_meal_type_display()} - {self.goal})'

    def get_image_url(self):
        from .diet_image_utils import get_diet_image_path
        return get_diet_image_path(self.name, self.meal_type)


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, related_name='workout_exercises', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, related_name='workout_entries', on_delete=models.PROTECT)
    sets_planned = models.PositiveIntegerField()
    reps_planned = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(default=60)
    exercise_seconds = models.PositiveIntegerField(default=30)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    @property
    def volume(self):
        if self.exercise.is_bodyweight or self.weight is None:
            return None
        return calculate_exercise_volume(self)

    def __str__(self):
        return f'{self.exercise.name} ({self.workout})'


class WorkoutSet(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, related_name='sets', on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField()
    reps_completed = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    completed = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['workout_exercise', 'set_number'], name='unique_workout_set')]
        ordering = ['set_number']

    def __str__(self):
        return f'{self.workout_exercise.exercise.name} set {self.set_number}'
