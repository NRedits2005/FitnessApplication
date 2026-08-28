from decimal import Decimal
from datetime import timedelta
from django.db.models import Count, DateField, DecimalField, ExpressionWrapper, F, Max, Sum
from django.db.models.functions import Coalesce, Lower, TruncDate
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.html import escape
from .forms import ProfileForm, RegisterForm, StartWorkoutForm
from .models import DietMeal, Exercise, UserProfile, Workout, WorkoutExercise, WorkoutSet
from .recommendations import daily_workout, diet_for, diet_meals, get_available_exercises, get_recommended_exercises, get_womens_category_queryset, get_womens_exercises, search_exercises, WOMENS_CATEGORIES
from .analytics import RANGES, build_progress_data, get_range, progress_insights
from .image_utils import attach_exercise_images, get_exercise_image_path


def login_view(request):
    if request.user.is_authenticated:
        return redirect('workout:dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('workout:dashboard')
    return render(request, 'workout/login.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('workout:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        UserProfile.objects.create(user=user)
        login(request, user)
        return redirect('workout:dashboard')
    return render(request, 'workout/register.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('workout:login')


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.profile_completed:
        return redirect('workout:profile_setup')
    today = timezone.localdate()
    completed_today = Workout.objects.filter(user=request.user, date=today, completed=True)
    entries_today = WorkoutExercise.objects.filter(workout__in=completed_today)
    total_volume = sum((entry.volume or Decimal('0') for entry in entries_today), Decimal('0'))
    workouts = Workout.objects.filter(user=request.user).prefetch_related('workout_exercises__exercise')
    context = {
        'workouts': workouts, 'today_exercises': entries_today.count(),
        'today_sets': WorkoutSet.objects.filter(workout_exercise__workout__in=completed_today, completed=True).count(),
        'today_volume': total_volume, 'profile': profile, 'plan': daily_workout(profile), 'diet': diet_for(profile), 'diet_meals': diet_meals(profile),
        'week_workouts': workouts.filter(completed=True, date__gte=today-timedelta(days=today.weekday())).count(),
        'total_weight_lifted': profile.total_weight_lifted_display,
        'is_female': profile.gender == 'female',
    }
    return render(request, 'workout/dashboard.html', context)


@login_required
def profile_setup(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.profile_completed = True
        # Handle profile image
        if form.cleaned_data.get('remove_photo'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = None
        elif form.cleaned_data.get('profile_image'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = form.cleaned_data['profile_image']
        profile.save()
        return redirect('workout:dashboard')
    return render(request, 'workout/profile_form.html', {'form': form, 'setup': True, 'profile': profile})


@login_required
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'workout/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        # Handle profile image
        if form.cleaned_data.get('remove_photo'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = None
        elif form.cleaned_data.get('profile_image'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = form.cleaned_data['profile_image']
        profile.save()
        return redirect('workout:profile')
    return render(request, 'workout/profile_form.html', {'form': form, 'profile': profile})


@login_required
def diet(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    try:
        offset = int(request.GET.get('offset', 0))
    except (TypeError, ValueError):
        offset = 0
    offset = max(-30, min(30, offset)); date = timezone.localdate() + timedelta(days=offset)
    return render(request, 'workout/diet.html', {'profile': profile, 'date': date, 'meals': diet_meals(profile, date), 'offset': offset})


def diet_meal_fallback(request, meal_id):
    meal = get_object_or_404(DietMeal, pk=meal_id)
    name = escape(meal.name)
    label = escape(meal.get_meal_type_display())
    accent = {'breakfast': '#d68a26', 'morning_snack': '#5f8f3c', 'lunch': '#227453', 'evening_snack': '#9e5a88', 'dinner': '#365f96', 'hydration': '#327ca8'}[meal.meal_type]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="{name}"><rect width="960" height="540" fill="#f3f6f2"/><rect x="38" y="38" width="884" height="464" rx="28" fill="#ffffff" stroke="#dbe5df" stroke-width="3"/><circle cx="480" cy="210" r="92" fill="{accent}" opacity=".13"/><path d="M405 200h150l-18 92H423z" fill="{accent}" opacity=".82"/><path d="M430 180c22-38 43-38 63 0 22-38 43-38 63 0" fill="none" stroke="{accent}" stroke-width="14" stroke-linecap="round"/><text x="480" y="365" text-anchor="middle" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="#25342d">{name}</text><text x="480" y="405" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#66766d">{label} meal idea</text></svg>'''
    return HttpResponse(svg, content_type='image/svg+xml')


@login_required
def start_workout(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.profile_completed:
        return redirect('workout:profile_setup')
    if request.method == 'POST':
        form = StartWorkoutForm(request.POST, profile=profile)
        if form.is_valid():
            exercise = form.cleaned_data['exercise']
            workout = Workout.objects.create(user=request.user)
            weight = None if exercise.is_bodyweight else form.cleaned_data['weight']
            entry = WorkoutExercise.objects.create(workout=workout, exercise=exercise, sets_planned=form.cleaned_data['sets'], reps_planned=form.cleaned_data['repetitions'], weight=weight, rest_seconds=form.cleaned_data['rest_minutes'] * 60 + form.cleaned_data['rest_seconds'], exercise_seconds=form.cleaned_data['exercise_minutes'] * 60 + form.cleaned_data['exercise_seconds'])
            return redirect('workout:workout_session', entry_id=entry.id)
    else:
        initial = {}
        try:
            recommendation_id = int(request.GET.get('recommendation', ''))
        except (TypeError, ValueError):
            recommendation_id = None
        if recommendation_id and get_available_exercises(profile).filter(pk=recommendation_id).exists():
            initial['exercise'] = recommendation_id
        form = StartWorkoutForm(profile=profile, initial=initial)
    return render(request, 'workout/start_workout.html', {
        'form': form, 'exercises': form.fields['exercise'].queryset,
        'recommendation': get_recommended_exercises(profile, limit=1)[0] if get_recommended_exercises(profile, limit=1) else None,
    })


@login_required
def workout_session(request, entry_id):
    entry = get_object_or_404(WorkoutExercise.objects.select_related('exercise', 'workout'), pk=entry_id, workout__user=request.user)
    if entry.workout.completed:
        return redirect('workout:workout_complete', workout_id=entry.workout_id)
    last_set = entry.sets.aggregate(last=Max('set_number'))['last'] or 0
    return render(request, 'workout/workout_session.html', {'entry': entry, 'next_set': last_set + 1})


@require_POST
@login_required
def complete_set(request, entry_id):
    entry = get_object_or_404(WorkoutExercise.objects.select_related('exercise', 'workout'), pk=entry_id, workout__user=request.user)
    set_number = (entry.sets.aggregate(last=Max('set_number'))['last'] or 0) + 1
    if set_number > entry.sets_planned:
        return JsonResponse({'complete': True, 'redirect': f'/complete/{entry.workout_id}/'})
    skipped = request.POST.get('skip') == '1'
    if skipped:
        reps_completed, set_weight = 0, None
    else:
        try:
            reps_completed = int(request.POST.get('reps', entry.reps_planned))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Repetitions must be a whole number.'}, status=400)
        if not 1 <= reps_completed <= 500:
            return JsonResponse({'error': 'Repetitions must be between 1 and 500.'}, status=400)

        if entry.exercise.is_bodyweight:
            set_weight = None
        else:
            raw_weight = request.POST.get('weight', entry.weight)
            try:
                set_weight = Decimal(str(raw_weight))
            except Exception:
                return JsonResponse({'error': 'Weight must be a valid number.'}, status=400)
            if not Decimal('0') <= set_weight <= Decimal('99999.99'):
                return JsonResponse({'error': 'Weight must be between 0 and 99,999.99 kg.'}, status=400)

    WorkoutSet.objects.create(
        workout_exercise=entry, set_number=set_number,
        reps_completed=reps_completed, weight=set_weight,
        completed=not skipped, skipped=skipped, completed_at=timezone.now(),
    )
    final = set_number == entry.sets_planned
    if final:
        entry.workout.completed = True
        entry.workout.completed_at = timezone.now()
        entry.workout.save(update_fields=['completed', 'completed_at'])
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        today = timezone.localdate()
        if profile.last_workout_date != today:
            profile.current_streak = profile.current_streak + 1 if profile.last_workout_date == today - timedelta(days=1) else 1
            profile.longest_streak = max(profile.longest_streak, profile.current_streak); profile.last_workout_date = today
            profile.save(update_fields=['current_streak','longest_streak','last_workout_date'])
    return JsonResponse({'complete': final, 'skipped': skipped, 'set_number': set_number, 'next_set': set_number + 1, 'redirect': f'/complete/{entry.workout_id}/' if final else None})


@login_required
def workout_complete(request, workout_id):
    workout = get_object_or_404(Workout.objects.prefetch_related('workout_exercises__exercise', 'workout_exercises__sets'), pk=workout_id, user=request.user)
    entries = workout.workout_exercises.all()
    total_volume = workout.total_volume
    completed_sets = sum(entry.sets.filter(completed=True).count() for entry in entries)
    total_reps = sum(workout_set.reps_completed for entry in entries for workout_set in entry.sets.all())
    return render(request, 'workout/workout_complete.html', {'workout': workout, 'entries': entries, 'total_volume': total_volume, 'completed_sets': completed_sets, 'total_reps': total_reps})


@require_POST
@login_required
def delete_workout(request, workout_id):
    get_object_or_404(Workout, pk=workout_id, user=request.user).delete()
    return redirect('workout:dashboard')


@login_required
def history(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    workouts = Workout.objects.filter(user=request.user).prefetch_related('workout_exercises__exercise', 'workout_exercises__sets')
    return render(request, 'workout/history.html', {
        'workouts': workouts,
        'profile': profile,
        'total_weight_lifted': profile.total_weight_lifted_display,
        'completed_count': workouts.filter(completed=True).count(),
    })


@login_required
def progress(request):
    """Show the current user's completed-workout analytics and history."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.profile_completed:
        return redirect('workout:profile_setup')

    today = timezone.localdate()
    range_key, start_date = get_range(request.GET.get('range', '30d'), today)
    # Prefer the actual completion date.  The date field remains a fallback
    # for workouts saved before completed_at was introduced.
    base_workouts = Workout.objects.filter(user=request.user, completed=True).annotate(
        analytics_date=Coalesce(TruncDate('completed_at'), F('date'), output_field=DateField())
    )
    all_time_workouts = base_workouts.count()
    if start_date:
        base_workouts = base_workouts.filter(analytics_date__gte=start_date)
    workouts = base_workouts.prefetch_related('workout_exercises__exercise', 'workout_exercises__sets')
    data = build_progress_data(workouts, today)

    # The heatmap always covers the last 12 months, independently of the selected summary range.
    heatmap_start = today - timedelta(days=364)
    heatmap_workouts = Workout.objects.filter(user=request.user, completed=True).annotate(
        analytics_date=Coalesce(TruncDate('completed_at'), F('date'), output_field=DateField())
    ).filter(analytics_date__gte=heatmap_start).prefetch_related('workout_exercises__exercise', 'workout_exercises__sets')
    heatmap_activity = build_progress_data(heatmap_workouts, today)['activity']

    range_days = RANGES[range_key][1]
    previous_workouts = 0
    if range_days:
        previous_start = start_date - timedelta(days=range_days)
        previous_workouts = Workout.objects.filter(user=request.user, completed=True).annotate(
            analytics_date=Coalesce(TruncDate('completed_at'), F('date'), output_field=DateField())
        ).filter(analytics_date__gte=previous_start, analytics_date__lt=start_date).count()
    insights = progress_insights(data, profile, range_days, previous_workouts, today)
    milestones = [(1, 'First Workout'), (5, '5 Workouts'), (10, '10 Workouts'), (25, '25 Workouts'), (50, '50 Workouts'), (100, '100 Workouts')]
    streak_milestones = [(7, '7-Day Streak'), (30, '30-Day Streak')]
    chart_data = {
        'frequency': data['frequency'], 'volume': data['volume'],
        'activity': heatmap_activity, 'heatmapStart': heatmap_start.isoformat(),
    }
    return render(request, 'workout/progress.html', {
        'profile': profile, 'summary': data['summary'], 'history': data['history'],
        'all_time_workouts': all_time_workouts,
        'ranges': RANGES, 'selected_range': range_key, 'range_label': RANGES[range_key][0],
        'insights': insights, 'milestones': milestones, 'streak_milestones': streak_milestones,
        'chart_data': chart_data,
    })


@login_required
def workout_history_detail(request, workout_id):
    workout = get_object_or_404(Workout.objects.prefetch_related('workout_exercises__exercise', 'workout_exercises__sets'), pk=workout_id, user=request.user)
    entries = workout.workout_exercises.all()
    total_volume = workout.total_volume
    completed_sets = sum(entry.sets.filter(completed=True).count() for entry in entries)
    total_reps = sum(workout_set.reps_completed for entry in entries for workout_set in entry.sets.all())
    return render(request, 'workout/workout_complete.html', {'workout': workout, 'entries': entries, 'total_volume': total_volume, 'completed_sets': completed_sets, 'total_reps': total_reps, 'history_detail': True})


@login_required
def exercise_library(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.profile_completed:
        return redirect('workout:profile_setup')

    is_female = profile.gender == 'female'
    query = request.GET.get('q', '').strip()

    # This is the only collection rendered by the Library. It starts with the
    # saved profile setup, so later search/category filters cannot reveal an
    # exercise requiring unavailable equipment.
    exercises = get_available_exercises(profile)

    if is_female:
        # Women's fitness filters
        womens_categories = WOMENS_CATEGORIES
        selected_category = request.GET.get('category', '')
        if selected_category and selected_category not in womens_categories:
            selected_category = ''

        exercises = get_womens_category_queryset(profile, selected_category or None)
        if query:
            exercises = search_exercises(exercises, query)
        else:
            exercises = exercises.order_by('category', Lower('name'), 'name', 'pk')

        # Attach gender-matched images for female library
        exercises = attach_exercise_images(list(exercises), 'female')

        is_home_workout = profile.workout_location == 'home'

        # Build Women's Fitness equipment pills for Home users
        wf_equipment = []
        if is_home_workout:
            WF_EQUIPMENT_OPTIONS = [
                ('bodyweight', 'No Equipment', '🏋️'),
                ('dumbbell', 'Dumbbells', '🏋️'),
                ('resistance_band', 'Resistance Band', '🔗'),
                ('other', 'Chair', '🪑'),
                ('bench', 'Bench / Step', '🪜'),
                ('pullup_bar', 'Pull-Up Bar', '🏗️'),
                ('other_bike', 'Exercise Bike', '🚴'),
                ('jump_rope', 'Jump Rope', '🤸'),
            ]
            user_equip = set(profile.home_equipment or [])
            # Map profile equipment keys to our WF option keys
            equip_mapping = {
                'bodyweight': 'bodyweight', 'dumbbell': 'dumbbell',
                'band': 'resistance_band', 'bench': 'bench',
                'pullup_bar': 'pullup_bar', 'jump_rope': 'jump_rope',
            }
            selected_keys = {equip_mapping.get(e, e) for e in user_equip}
            # Always include bodyweight
            selected_keys.add('bodyweight')

            for key, label, icon in WF_EQUIPMENT_OPTIONS:
                wf_equipment.append({
                    'key': key, 'label': label, 'icon': icon,
                    'selected': key in selected_keys,
                })

        return render(request, 'workout/exercise_library.html', {
            'exercises': exercises, 'query': query,
            'is_female': True,
            'womens_categories': womens_categories,
            'selected_category': selected_category,
            'is_home_workout': is_home_workout,
            'wf_equipment': wf_equipment,
        })
    else:
        # Existing male/default filters
        body_parts = ['Back', 'Biceps', 'Calisthenics', 'Cardio', 'Chest', 'Core', 'Full Body', 'Legs', 'Shoulders']
        body_part = request.GET.get('body_part', '')
        if body_part not in body_parts:
            body_part = ''

        if query:
            exercises = search_exercises(exercises, query)
        if body_part:
            exercises = exercises.filter(body_part=body_part)
        if not query:
            exercises = exercises.order_by('body_part', Lower('name'), 'name', 'pk')
        equipment_labels = {
            'bodyweight': 'No equipment', 'dumbbell': 'Dumbbells',
            'band': 'Resistance Bands', 'pullup_bar': 'Pull-up Bar',
            'kettlebell': 'Kettlebell', 'bench': 'Bench', 'mat': 'Yoga Mat',
            'jump_rope': 'Jump Rope',
        }
        is_home_workout = profile.workout_location == 'home'
        profile_equipment = []
        if is_home_workout:
            profile_equipment = [equipment_labels.get(item, item.replace('_', ' ').title()) for item in profile.home_equipment]
            if not profile_equipment:
                profile_equipment = ['No equipment']

        # Attach gender-matched images for male library
        exercises = attach_exercise_images(list(exercises), 'male')

        return render(request, 'workout/exercise_library.html', {
            'exercises': exercises, 'profile_equipment': profile_equipment,
            'body_parts': body_parts, 'selected_body_part': body_part, 'query': query,
            'is_home_workout': is_home_workout, 'is_female': False,
        })


@login_required
def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    compatible = get_available_exercises(profile).filter(pk=exercise.pk).exists() if profile.profile_completed else False
    recommended = exercise.pk in {item.pk for item in get_recommended_exercises(profile)} if profile.profile_completed else False
    # Attach gender-matched image
    gender = profile.gender if profile.profile_completed else 'male'
    exercise.image = get_exercise_image_path(exercise.name, exercise.category, gender)
    return render(request, 'workout/exercise_detail.html', {'exercise': exercise, 'compatible': compatible, 'recommended': recommended, 'profile': profile})


def exercise_visual(request, exercise_id):
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    name = escape(exercise.name)
    category = escape(exercise.category)
    # A unique, local movement card for every exercise; never depends on third-party image URLs.
    accent = {'Chest': '#16835a', 'Back': '#2765b0', 'Legs': '#b06b22', 'Shoulders': '#7557a8', 'Arms': '#af4d69', 'Core': '#1d8193', 'Calisthenics': '#3b7b57', 'Cardio': '#c35b3e', 'Beginner': '#368163', 'Lower Body & Glutes': '#a855f7', 'Upper Body': '#c026d3', 'Cardio & Fat Burning': '#e11d48', 'Mobility & Recovery': '#0891b2', 'Beginner-Friendly': '#16a34a'}.get(exercise.category, '#16835a')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img" aria-label="{name} movement illustration"><rect width="640" height="360" rx="28" fill="#edf6f1"/><circle cx="320" cy="88" r="34" fill="{accent}"/><path d="M320 122 L320 224 M320 148 L235 195 M320 148 L405 195 M320 222 L253 302 M320 222 L388 302" stroke="{accent}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M120 282 Q320 235 520 282" stroke="#b6d6c7" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M465 100 C535 145 535 230 465 255" stroke="{accent}" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M450 235 L465 255 L486 239" stroke="{accent}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><text x="320" y="335" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#25342d">{name}</text><text x="320" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#527064">{category} movement guide</text></svg>'''
    return HttpResponse(svg, content_type='image/svg+xml')
