from django.core.management.base import BaseCommand
from workout.exercise_cleanup import cleanup_exercises
from workout.models import Exercise, WorkoutExercise


class Command(BaseCommand):
    help = 'Normalize exercise names and safely consolidate duplicate catalogue records.'

    def handle(self, *args, **options):
        normalized, removed = cleanup_exercises(Exercise, WorkoutExercise)
        self.stdout.write(self.style.SUCCESS(f'Normalized {normalized} names and removed {removed} duplicate exercise records.'))
