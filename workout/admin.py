from django.contrib import admin
from .models import Exercise, Workout, WorkoutExercise, WorkoutSet


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'gender_category', 'is_bodyweight', 'is_beginner_friendly')
    list_filter = ('category', 'difficulty', 'gender_category', 'is_bodyweight', 'is_beginner_friendly', 'equipment_type')
    search_fields = ('name', 'muscles_targeted', 'body_part')


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 0


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('date', 'completed', 'created_at')
    list_filter = ('completed', 'date')
    inlines = [WorkoutExerciseInline]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'workout', 'sets_planned', 'reps_planned', 'weight')


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ('workout_exercise', 'set_number', 'reps_completed', 'completed', 'skipped', 'completed_at')
