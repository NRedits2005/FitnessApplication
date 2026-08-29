from django.db.models import Case, IntegerField, Q, Value, When
from django.db.models.functions import Lower
from django.utils import timezone

from .models import DietMeal, Exercise


MEAL_ORDER = ['breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner', 'hydration']
PULLUP_BAR_MOVEMENTS = ('pull-up', 'chin-up', 'dead hang', 'hanging knee raise', 'hanging leg raise')
HOME_EQUIPMENT_MAP = {'band': 'resistance_band', 'pullup_bar': 'pullup_bar'}

# Women's Fitness category display order
WOMENS_CATEGORIES = [
    'Beginner-Friendly',
    'Lower Body & Glutes',
    'Upper Body',
    'Core',
    'Cardio & Fat Burning',
    'Mobility & Recovery',
]
WOMENS_STANDARD_CATEGORIES = tuple(
    category for category in WOMENS_CATEGORIES if category != 'Beginner-Friendly'
)
MALE_LIBRARY_BODY_PARTS = ('Back', 'Biceps', 'Calisthenics', 'Cardio', 'Chest', 'Core', 'Full Body', 'Legs', 'Shoulders')


def selected_equipment(profile):
    """Return normalized home equipment, always including bodyweight movement."""
    selected = {HOME_EQUIPMENT_MAP.get(item, item) for item in (profile.home_equipment or [])}
    return selected | {'bodyweight'}


def get_available_exercises(profile):
    """Single source of truth for profile-compatible exercises."""
    exercises = Exercise.objects.all()

    # --- Gender-based visibility ---
    if profile.gender == 'female':
        exercises = exercises.filter(gender_category__in=['female', 'all'])
    elif profile.gender == 'male':
        exercises = exercises.filter(gender_category__in=['male', 'all'])
    else:
        # Prefer-not-to-say is intentionally neutral: do not infer either
        # gender-specific experience from an unset/private profile value.
        exercises = exercises.filter(gender_category='all')

    if profile.workout_location == 'gym':
        return exercises
    equipment = selected_equipment(profile)
    compatible = Q(is_bodyweight=True) | Q(equipment_type__in=equipment)
    if 'pullup_bar' in equipment:
        compatible |= Q(name__in=['Pull-Up', 'Chin-Up', 'Hanging Knee Raise', 'Hanging Leg Raise', 'Dead Hang'])
    exercises = exercises.filter(compatible)
    if 'pullup_bar' not in equipment:
        exercises = exercises.exclude(name__in=['Pull-Up', 'Chin-Up', 'Hanging Knee Raise', 'Hanging Leg Raise', 'Dead Hang'])
    return exercises


def search_exercises(exercises, query):
    """Search the existing Exercise fields, ranking direct name matches first."""
    query = (query or '').strip()
    if not query:
        return exercises
    matches = (
        Q(name__icontains=query)
        | Q(body_part__icontains=query)
        | Q(muscles_targeted__icontains=query)
        | Q(category__icontains=query)
        | Q(equipment_type__icontains=query)
        | Q(description__icontains=query)
    )
    return exercises.filter(matches).annotate(
        search_rank=Case(
            When(name__icontains=query, then=Value(0)),
            When(Q(body_part__icontains=query) | Q(muscles_targeted__icontains=query), then=Value(1)),
            When(Q(category__icontains=query) | Q(equipment_type__icontains=query), then=Value(2)),
            default=Value(3), output_field=IntegerField(),
        )
    ).order_by('search_rank', Lower('name'), 'name', 'pk')


def get_womens_category_queryset(profile, category=None):
    """Return profile-compatible Women's Fitness exercises for one category.

    ``Beginner-Friendly`` is a view category backed by Exercise's boolean,
    rather than a second, competing value in the category column.
    """
    exercises = get_available_exercises(profile)
    womens_qs = exercises.filter(
        Q(category__in=WOMENS_STANDARD_CATEGORIES) | Q(is_beginner_friendly=True)
    ).distinct()
    if category == 'Beginner-Friendly':
        return womens_qs.filter(is_beginner_friendly=True)
    if category in WOMENS_STANDARD_CATEGORIES:
        return womens_qs.filter(category=category)
    return womens_qs


def get_workout_select_exercises(profile):
    """Return the exercises a user can choose from when starting a workout."""
    if profile.gender == 'female':
        return get_womens_category_queryset(profile)
    return get_available_exercises(profile).filter(body_part__in=MALE_LIBRARY_BODY_PARTS)


def get_womens_exercises(profile):
    """Return Women's Fitness exercises grouped using the same category rules as the library."""
    grouped = {}
    for cat in WOMENS_CATEGORIES:
        cat_exercises = list(get_womens_category_queryset(profile, cat).order_by('name'))
        if cat_exercises:
            grouped[cat] = cat_exercises
    return grouped


def score_exercise(exercise, profile):
    """Score compatible exercises using goal and profile factors, not hard restrictions."""
    name, part = exercise.name.lower(), exercise.body_part.lower()
    score = 0
    if profile.goal in ('bulk', 'strength') and not exercise.is_bodyweight:
        score += 5
    if profile.goal == 'cut' and (exercise.is_bodyweight or part == 'cardio'):
        score += 4
    if profile.goal == 'fitness':
        score += 2
    if profile.workout_location == 'home' and 'pullup_bar' in selected_equipment(profile) and name in PULLUP_BAR_MOVEMENTS:
        score += 4
    if profile.gender == 'female' and any(term in name for term in ('squat', 'lunge', 'hip thrust', 'glute', 'step-up', 'row', 'plank')):
        score += 2
    if profile.gender == 'male' and any(term in name for term in ('bench', 'row', 'press', 'squat', 'deadlift', 'pull')):
        score += 2
    if profile.bmi and profile.bmi >= 25 and any(term in name for term in ('walking', 'cycling', 'step-up', 'plank', 'bird dog', 'glute bridge')):
        score += 3
    if profile.experience_level == 'beginner':
        if exercise.category == 'Beginner' or exercise.is_beginner_friendly or any(term in name for term in ('wall push-up', 'knee push-up', 'bodyweight squat', 'bird dog', 'dead bug', 'glute bridge', 'plank')):
            score += 4
        if any(term in name for term in ('muscle-up', 'front lever', 'back lever', 'handstand', 'pistol')):
            score -= 7
    if profile.age and profile.age >= 50 and any(term in name for term in ('burpee', 'pistol', 'handstand', 'jumping')):
        score -= 4
    return score


def get_recommended_exercises(profile, limit=4):
    exercises = list(get_workout_select_exercises(profile))
    ranked = ((score_exercise(exercise, profile), exercise.name.lower(), exercise) for exercise in exercises)
    recs = [item[2] for item in sorted(ranked, key=lambda item: (-item[0], item[1]))[:limit]]
    gender = profile.gender if profile else 'male'
    from .image_utils import attach_exercise_images
    return attach_exercise_images(recs, gender)


def daily_workout(profile):
    recs = get_recommended_exercises(profile, limit=4)
    return {
        'title': 'Home Workout' if profile.workout_location == 'home' else 'Gym Workout',
        'reason': 'Personalized for your goal, age, BMI, location, equipment, gender, and experience.',
        'exercises': recs,
    }


def diet_meals(profile, date=None):
    date = date or timezone.localdate()
    meals = list(DietMeal.objects.filter(goal=profile.goal, day_of_week=date.weekday()))
    meals.sort(key=lambda meal: MEAL_ORDER.index(meal.meal_type))
    from .diet_image_utils import attach_diet_images
    return attach_diet_images(meals)


def diet_for(profile):
    return {'title': {'bulk': 'Build muscle', 'cut': 'Lose fat', 'maintain': 'Maintain weight', 'strength': 'Build strength', 'fitness': 'Improve fitness'}.get(profile.goal, 'General wellness')}
