"""Safe normalization and duplicate consolidation for the exercise catalogue."""
import re

from django.db import transaction
from django.db.models.functions import Lower


def normalize_name(value):
    return re.sub(r'\s+', ' ', (value or '').strip())


def quality(exercise):
    fields = ('body_part', 'category', 'description', 'instructions', 'muscles_targeted', 'beginner_tips', 'equipment_type', 'image')
    score = sum(bool(getattr(exercise, field, '')) for field in fields)
    if exercise.image and 'exercise-photo-grid.png' not in exercise.image:
        score += 10
    return score


@transaction.atomic
def cleanup_exercises(Exercise, WorkoutExercise):
    """Normalize names, retain the most complete row, and preserve workout links."""
    normalized = 0
    removed = 0
    for exercise in Exercise.objects.order_by('pk'):
        clean_name = normalize_name(exercise.name)
        if exercise.name != clean_name:
            exercise.name = clean_name
            exercise.save(update_fields=['name'])
            normalized += 1

    duplicate_names = (Exercise.objects.annotate(normalized_name=Lower('name'))
                       .values_list('normalized_name', flat=True).distinct())
    for normalized_name in duplicate_names:
        group = list(Exercise.objects.filter(name__iexact=normalized_name).order_by('pk'))
        if len(group) < 2:
            continue
        keeper = max(group, key=lambda item: (quality(item), -item.pk))
        for redundant in group:
            if redundant.pk == keeper.pk:
                continue
            WorkoutExercise.objects.filter(exercise=redundant).update(exercise=keeper)
            redundant.delete()
            removed += 1
    return normalized, removed
