from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import DietMeal, Exercise, UserProfile, Workout, WorkoutExercise, WorkoutSet


class ExerciseLibraryProfileFilteringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('library-user', password='password')
        self.profile = UserProfile.objects.create(
            user=self.user, profile_completed=True, workout_location='home',
            home_equipment=['dumbbell'],
        )
        self.client.login(username='library-user', password='password')
        self.dumbbell_back = self.make_exercise('Dumbbell Row', 'dumbbell', 'Back')
        self.dumbbell_chest = self.make_exercise('Dumbbell Press', 'dumbbell', 'Chest')
        self.band_chest = self.make_exercise('Band Press', 'resistance_band', 'Chest')
        self.barbell_chest = self.make_exercise('Barbell Press', 'barbell', 'Chest')
        self.bodyweight_core = self.make_exercise('Bodyweight Plank', 'bodyweight', 'Core', True)

    def make_exercise(self, name, equipment_type, body_part, is_bodyweight=False):
        return Exercise.objects.create(
            name=name, body_part=body_part, equipment_type=equipment_type,
            is_bodyweight=is_bodyweight, category='Beginner', description='Description',
            instructions='Instructions', muscles_targeted='Core',
        )

    def library(self, **params):
        return self.client.get(reverse('workout:exercise_library'), params)

    def rendered_ids(self, response):
        return {e.pk for e in response.context['exercises']}

    def test_library_uses_only_saved_profile_equipment(self):
        response = self.library()
        self.assertEqual(
            self.rendered_ids(response),
            {self.dumbbell_back.pk, self.dumbbell_chest.pk, self.bodyweight_core.pk},
        )
        self.assertContains(response, 'Based on your equipment:')
        self.assertNotContains(response, 'All equipment')
        self.assertNotContains(response, 'ALL EXERCISES')

    def test_body_part_filter_runs_after_profile_equipment_filter(self):
        response = self.library(body_part='Chest')
        self.assertEqual(self.rendered_ids(response), {self.dumbbell_chest.pk})
        self.assertNotContains(response, 'Barbell Press')
        self.assertNotContains(response, 'Band Press')

    def test_search_and_body_part_remain_within_profile_equipment(self):
        response = self.library(q='Press', body_part='Chest')
        self.assertEqual(self.rendered_ids(response), {self.dumbbell_chest.pk})
        self.assertNotContains(response, 'Barbell Press')
        self.assertNotContains(response, 'Band Press')

    def test_profile_equipment_changes_update_library_automatically(self):
        self.profile.home_equipment = ['band']
        self.profile.save(update_fields=['home_equipment'])
        response = self.library()
        self.assertEqual(self.rendered_ids(response), {self.band_chest.pk, self.bodyweight_core.pk})
        self.assertNotContains(response, 'Dumbbell Row')

    def test_empty_body_part_uses_the_requested_empty_state(self):
        response = self.library(body_part='Shoulders')
        self.assertEqual(self.rendered_ids(response), set())
        self.assertContains(response, 'No exercises found for this category with your current equipment.')

    def test_navigation_contains_the_fixed_body_part_categories(self):
        response = self.library()
        self.assertEqual(
            response.context['body_parts'],
            ['Back', 'Biceps', 'Calisthenics', 'Cardio', 'Chest', 'Core', 'Full Body', 'Legs', 'Shoulders'],
        )

    def test_gym_library_includes_all_exercises_regardless_of_saved_home_equipment(self):
        self.profile.workout_location = 'gym'
        self.profile.save(update_fields=['workout_location'])

        response = self.library()

        self.assertEqual(
            self.rendered_ids(response),
            {self.dumbbell_back.pk, self.dumbbell_chest.pk, self.band_chest.pk, self.barbell_chest.pk, self.bodyweight_core.pk},
        )
        self.assertFalse(response.context['is_home_workout'])
        self.assertNotContains(response, 'Based on your equipment:')

    def test_gym_body_part_and_search_filter_the_complete_library(self):
        self.profile.workout_location = 'gym'
        self.profile.save(update_fields=['workout_location'])

        response = self.library(body_part='Chest', q='Press')

        self.assertEqual(
            self.rendered_ids(response),
            {self.dumbbell_chest.pk, self.band_chest.pk, self.barbell_chest.pk},
        )


class WomensFitnessCategoryFilteringTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('female-library-user', password='password')
        self.profile = UserProfile.objects.create(
            user=self.user, profile_completed=True, gender='female', workout_location='gym',
        )
        self.client.login(username='female-library-user', password='password')
        self.beginner_lower = self.make_exercise(
            'Beginner Glute Bridge', 'Lower Body & Glutes', beginner=True,
        )
        self.lower = self.make_exercise('Romanian Deadlift', 'Lower Body & Glutes')
        self.upper = self.make_exercise('Dumbbell Row', 'Upper Body')
        self.core = self.make_exercise('Plank', 'Core')
        self.cardio = self.make_exercise('Jumping Jacks', 'Cardio & Fat Burning')
        self.mobility = self.make_exercise('Cat-Cow Stretch', 'Mobility & Recovery')

    def make_exercise(self, name, category, beginner=False):
        return Exercise.objects.create(
            name=name, category=category, body_part='Core', equipment_type='bodyweight',
            description='Description', instructions='Instructions', muscles_targeted='Core',
            is_bodyweight=True, gender_category='female', is_beginner_friendly=beginner,
        )

    def library(self, **params):
        return self.client.get(reverse('workout:exercise_library'), params)

    def returned_names(self, response):
        return {e.name for e in response.context['exercises']}

    def test_each_womens_category_uses_its_persisted_category_rule(self):
        expected = {
            'Beginner-Friendly': {'Beginner Glute Bridge'},
            'Lower Body & Glutes': {'Beginner Glute Bridge', 'Romanian Deadlift'},
            'Upper Body': {'Dumbbell Row'},
            'Core': {'Plank'},
            'Cardio & Fat Burning': {'Jumping Jacks'},
            'Mobility & Recovery': {'Cat-Cow Stretch'},
        }
        for category, names in expected.items():
            with self.subTest(category=category):
                response = self.library(category=category)
                self.assertEqual(self.returned_names(response), names)
                self.assertEqual(response.context['selected_category'], category)

    def test_womens_category_combines_with_search_and_default_shows_all(self):
        response = self.library(category='Lower Body & Glutes', q='deadlift')
        self.assertEqual(self.returned_names(response), {'Romanian Deadlift'})

        response = self.library()
        self.assertEqual(self.returned_names(response), {
            'Beginner Glute Bridge', 'Romanian Deadlift', 'Dumbbell Row', 'Plank',
            'Jumping Jacks', 'Cat-Cow Stretch',
        })

    def test_female_start_workout_dropdown_matches_library_exercise_names(self):
        Exercise.objects.create(
            name='Female Strength Press', category='Strength', body_part='Chest',
            equipment_type='bodyweight', description='Description',
            instructions='Instructions', muscles_targeted='Chest',
            is_bodyweight=True, gender_category='female',
        )

        library_response = self.library()
        start_response = self.client.get(reverse('workout:start_workout'))

        library_names = self.returned_names(library_response)
        dropdown_names = set(
            start_response.context['form'].fields['exercise'].queryset.values_list('name', flat=True)
        )

        self.assertEqual(dropdown_names, library_names)
        self.assertNotIn('Female Strength Press', dropdown_names)

    def test_category_links_encode_ampersands_and_preserve_active_state(self):
        response = self.library(category='Cardio & Fat Burning')
        self.assertContains(response, 'category=Lower%20Body%20%26%20Glutes')
        self.assertContains(response, 'filter active')

    def test_male_library_keeps_body_part_filters(self):
        self.profile.gender = 'male'
        self.profile.save(update_fields=['gender'])
        general = Exercise.objects.create(
            name='General Chest Press', category='Chest', body_part='Chest',
            equipment_type='barbell', description='Description', instructions='Instructions',
            muscles_targeted='Chest', gender_category='all',
        )
        response = self.library(body_part='Chest')
        self.assertFalse(response.context['is_female'])
        self.assertEqual({e.pk for e in response.context['exercises']}, {general.pk})


class ExerciseSearchAndAutocompleteTests(TestCase):
    def setUp(self):
        self.female = User.objects.create_user('search-female', password='password')
        self.male = User.objects.create_user('search-male', password='password')
        self.neutral = User.objects.create_user('search-neutral', password='password')
        UserProfile.objects.create(user=self.female, profile_completed=True, gender='female', workout_location='gym')
        UserProfile.objects.create(user=self.male, profile_completed=True, gender='male', workout_location='gym')
        UserProfile.objects.create(user=self.neutral, profile_completed=True, gender='prefer_not', workout_location='gym')
        self.female_squat = self.make_exercise(
            'Goblet Squat', 'Lower Body & Glutes', 'Legs', 'Glutes, Quadriceps', 'dumbbell', 'female',
        )
        self.female_stretch = self.make_exercise(
            'Cat-Cow Stretch', 'Mobility & Recovery', 'Back', 'Spine and core mobility', 'bodyweight', 'female',
        )
        self.female_only = self.make_exercise(
            'Women Only Press', 'Upper Body', 'Chest', 'Chest', 'dumbbell', 'female',
        )
        self.male_pull = self.make_exercise(
            'Pull-Up', 'Back', 'Back', 'Lats and Biceps', 'pullup_bar', 'all',
        )
        self.male_chest = self.make_exercise(
            'Bench Press', 'Chest', 'Chest', 'Pectorals', 'barbell', 'all',
        )

    def make_exercise(self, name, category, body_part, muscles, equipment, gender):
        return Exercise.objects.create(
            name=name, category=category, body_part=body_part, muscles_targeted=muscles,
            equipment_type=equipment, gender_category=gender, description=f'{body_part} training movement',
            instructions='Instructions', is_bodyweight=equipment == 'bodyweight',
        )

    def library_names(self, user, **params):
        self.client.login(username=user.username, password='password')
        response = self.client.get(reverse('workout:exercise_library'), params)
        self.assertEqual(response.status_code, 200)
        return response, {e.name for e in response.context['exercises']}

    def test_female_searches_all_supported_fields_without_leaking_male_library(self):
        _, names = self.library_names(self.female, q='GLUT')
        self.assertEqual(names, {'Goblet Squat'})
        _, names = self.library_names(self.female, q='mobility')
        self.assertEqual(names, {'Cat-Cow Stretch'})
        _, names = self.library_names(self.female, q='chest')
        self.assertEqual(names, {'Women Only Press'})
        _, names = self.library_names(self.female, category='Lower Body & Glutes', q='squa')
        self.assertEqual(names, {'Goblet Squat'})

    def test_male_search_and_start_autocomplete_use_only_available_exercises(self):
        response, names = self.library_names(self.male, q='BICE')
        self.assertEqual(names, {'Pull-Up'})
        self.assertNotContains(response, 'Women Only Press')

        response = self.client.get(reverse('workout:start_workout'))
        choices = set(response.context['form'].fields['exercise'].queryset.values_list('name', flat=True))
        self.assertEqual(choices, {'Pull-Up', 'Bench Press'})
        self.assertContains(response, 'id="exercise-dropdown"')
        self.assertContains(response, 'exercise-suggestions')
        self.assertNotContains(response, 'exercise-autocomplete')
        self.assertNotContains(response, 'Type an exercise name, muscle, or equipment')

    def test_exercise_detail_links_open_for_visible_exercises(self):
        response, _ = self.library_names(self.female, q='squat')
        detail_url = reverse('workout:exercise_detail', kwargs={'exercise_id': self.female_squat.id})
        self.assertContains(response, detail_url)
        detail = self.client.get(detail_url)
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Goblet Squat')

    def test_prefer_not_to_say_uses_only_the_neutral_library_and_dropdown(self):
        response, names = self.library_names(self.neutral)
        self.assertFalse(response.context['is_female'])
        self.assertEqual(names, {'Pull-Up', 'Bench Press'})
        self.assertNotContains(response, "WOMEN'S FITNESS")
        self.assertNotContains(response, 'Women Only Press')

        response = self.client.get(reverse('workout:start_workout'))
        choices = set(response.context['form'].fields['exercise'].queryset.values_list('name', flat=True))
        self.assertEqual(choices, {'Pull-Up', 'Bench Press'})
        self.assertContains(response, 'Select an exercise')
        self.assertNotContains(response, 'Type an exercise name, muscle, or equipment')

    def test_profile_gender_form_exposes_only_male_and_female(self):
        from .forms import ProfileForm

        self.assertEqual(
            list(ProfileForm().fields['gender'].choices),
            [('', 'Select gender'), ('male', 'Male'), ('female', 'Female')],
        )


class ProgressAnalyticsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('analytics-user', password='password')
        self.profile = UserProfile.objects.create(
            user=self.user, profile_completed=True, workout_location='gym', current_streak=2,
        )
        self.exercise = Exercise.objects.create(
            name='Analytics Press', body_part='Chest', equipment_type='barbell', category='Strength',
            description='Description', instructions='Instructions', muscles_targeted='Chest',
        )

    def test_progress_requires_login(self):
        response = self.client.get(reverse('workout:progress'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('workout:login'), response.url)

    def test_progress_has_friendly_empty_state(self):
        self.client.login(username='analytics-user', password='password')
        response = self.client.get(reverse('workout:progress'))
        self.assertContains(response, 'Your progress will appear here')
        self.assertContains(response, 'Start Workout')

    def test_progress_uses_only_completed_workouts_and_completed_sets(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import Workout, WorkoutExercise, WorkoutSet

        workout = Workout.objects.create(user=self.user, date=timezone.localdate(), completed=True, completed_at=timezone.now())
        entry = WorkoutExercise.objects.create(workout=workout, exercise=self.exercise, sets_planned=2, reps_planned=10, weight='20')
        WorkoutSet.objects.create(workout_exercise=entry, set_number=1, reps_completed=10, weight='20', completed=True)
        WorkoutSet.objects.create(workout_exercise=entry, set_number=2, reps_completed=0, weight=None, completed=False, skipped=True)
        Workout.objects.create(user=self.user, date=timezone.localdate() - timedelta(days=1), completed=False)

        self.client.login(username='analytics-user', password='password')
        response = self.client.get(reverse('workout:progress'), {'range': '7d'})
        summary = response.context['summary']
        self.assertEqual(summary['workouts'], 1)
        self.assertEqual(summary['sets'], 1)
        self.assertEqual(summary['reps'], 10)
        self.assertEqual(summary['volume'], '200')
        self.assertContains(response, 'Completed workouts')

    def test_progress_history_is_scoped_to_the_logged_in_user(self):
        from django.utils import timezone
        from .models import Workout

        other = User.objects.create_user('other-analytics-user', password='password')
        Workout.objects.create(user=other, date=timezone.localdate(), completed=True)
        self.client.login(username='analytics-user', password='password')
        response = self.client.get(reverse('workout:progress'))
        self.assertEqual(response.context['summary']['workouts'], 0)

    def test_progress_uses_completion_date_and_per_set_decimal_weights(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import Workout, WorkoutExercise, WorkoutSet

        # Started yesterday but completed today: it belongs in today's analytics.
        workout = Workout.objects.create(
            user=self.user, date=timezone.localdate() - timedelta(days=1),
            completed=True, completed_at=timezone.now(),
        )
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, sets_planned=3,
            reps_planned=10, weight='10',
        )
        WorkoutSet.objects.create(workout_exercise=entry, set_number=1, reps_completed=10, weight='10', completed=True)
        WorkoutSet.objects.create(workout_exercise=entry, set_number=2, reps_completed=10, weight='10', completed=True)
        WorkoutSet.objects.create(workout_exercise=entry, set_number=3, reps_completed=8, weight='12', completed=True)

        self.client.login(username='analytics-user', password='password')
        response = self.client.get(reverse('workout:progress'), {'range': 'today'})
        self.assertEqual(response.context['summary']['volume'], '296')

    def test_planned_values_without_completed_sets_have_zero_volume(self):
        from .models import Workout, WorkoutExercise

        workout = Workout.objects.create(user=self.user, completed=True)
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, sets_planned=3,
            reps_planned=10, weight='20',
        )
        self.assertEqual(entry.volume, 0)


class DashboardTotalWeightLiftedTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user('user-a', password='password')
        self.profile_a = UserProfile.objects.create(
            user=self.user_a, profile_completed=True, name='Alice',
            workout_location='home', home_equipment=['dumbbell', 'bench'],
            height_cm=170, weight_kg=65,
        )
        self.user_b = User.objects.create_user('user-b', password='password')
        self.profile_b = UserProfile.objects.create(
            user=self.user_b, profile_completed=True, name='Bob',
            workout_location='home', home_equipment=['dumbbell'],
            height_cm=180, weight_kg=75,
        )
        self.dumbbell_curl = Exercise.objects.create(
            name='Dumbbell Curl', body_part='Biceps', equipment_type='dumbbell',
            category='Beginner', description='Desc', instructions='Inst',
            muscles_targeted='Biceps', is_bodyweight=False,
        )
        self.bench_press = Exercise.objects.create(
            name='Bench Press', body_part='Chest', equipment_type='bench',
            category='Beginner', description='Desc', instructions='Inst',
            muscles_targeted='Chest', is_bodyweight=False,
        )
        self.push_up = Exercise.objects.create(
            name='Push-Up', body_part='Chest', equipment_type='bodyweight',
            category='Beginner', description='Desc', instructions='Inst',
            muscles_targeted='Chest', is_bodyweight=True,
        )

    def login_user(self, user):
        self.client.login(username=user.username, password='password')

    def test_new_user_dashboard_displays_zero_kg(self):
        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_weight_lifted'], '0')
        self.assertContains(response, 'TOTAL WEIGHT LIFTED')
        self.assertContains(response, '<strong>0<small> kg</small></strong>')
        self.assertContains(response, 'Total weight lifted')

    def test_single_weighted_exercise_all_sets_completed(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        workout = Workout.objects.create(user=self.user_a, completed=True)
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.dumbbell_curl,
            sets_planned=3, reps_planned=10, weight=Decimal('40.00'),
        )
        for set_num in range(1, 4):
            WorkoutSet.objects.create(
                workout_exercise=entry, set_number=set_num,
                reps_completed=10, weight=Decimal('40.00'), completed=True,
            )

        self.assertEqual(entry.volume, Decimal('1200.00'))
        self.assertEqual(workout.total_volume, Decimal('1200.00'))
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('1200.00'))
        self.assertEqual(self.profile_a.total_weight_lifted_display, '1,200')

        self.login_user(self.user_a)
        # Dashboard check
        dash_response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(dash_response.status_code, 200)
        self.assertEqual(dash_response.context['total_weight_lifted'], '1,200')
        self.assertContains(dash_response, '<strong>1,200<small> kg</small></strong>')

        # Workout complete check
        complete_response = self.client.get(reverse('workout:workout_complete', kwargs={'workout_id': workout.id}))
        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.context['total_volume'], Decimal('1200.00'))
        self.assertContains(complete_response, '1200 kg')

    def test_partial_completed_sets_only_completed_count(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        # 3 sets planned, 2 completed (10 reps each), 1 skipped (0 reps)
        workout = Workout.objects.create(user=self.user_a, completed=True)
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.dumbbell_curl,
            sets_planned=3, reps_planned=10, weight=Decimal('40.00'),
        )
        WorkoutSet.objects.create(
            workout_exercise=entry, set_number=1,
            reps_completed=10, weight=Decimal('40.00'), completed=True,
        )
        WorkoutSet.objects.create(
            workout_exercise=entry, set_number=2,
            reps_completed=10, weight=Decimal('40.00'), completed=True,
        )
        WorkoutSet.objects.create(
            workout_exercise=entry, set_number=3,
            reps_completed=0, weight=None, completed=False, skipped=True,
        )

        # 40 kg * 10 reps * 2 sets = 800 kg
        self.assertEqual(entry.volume, Decimal('800.00'))
        self.assertEqual(workout.total_volume, Decimal('800.00'))
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('800.00'))
        self.assertEqual(self.profile_a.total_weight_lifted_display, '800')

        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertContains(response, '<strong>800<small> kg</small></strong>')

    def test_multiple_exercises_in_one_workout(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        workout = Workout.objects.create(user=self.user_a, completed=True)
        # Entry 1: 40 kg * 10 reps * 3 sets = 1,200 kg
        entry1 = WorkoutExercise.objects.create(
            workout=workout, exercise=self.dumbbell_curl,
            sets_planned=3, reps_planned=10, weight=Decimal('40.00'), order=1,
        )
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=entry1, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)

        # Entry 2: 50 kg * 8 reps * 2 sets = 800 kg
        entry2 = WorkoutExercise.objects.create(
            workout=workout, exercise=self.bench_press,
            sets_planned=2, reps_planned=8, weight=Decimal('50.00'), order=2,
        )
        for s in range(1, 3):
            WorkoutSet.objects.create(workout_exercise=entry2, set_number=s, reps_completed=8, weight=Decimal('50.00'), completed=True)

        # Entry 3: Bodyweight Push-Up -> 0 kg
        entry3 = WorkoutExercise.objects.create(
            workout=workout, exercise=self.push_up,
            sets_planned=3, reps_planned=15, weight=None, order=3,
        )
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=entry3, set_number=s, reps_completed=15, weight=None, completed=True)

        # Total = 1,200 + 800 + 0 = 2,000 kg
        self.assertEqual(workout.total_volume, Decimal('2000.00'))
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('2000.00'))
        self.assertEqual(self.profile_a.total_weight_lifted_display, '2,000')

        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertContains(response, '<strong>2,000<small> kg</small></strong>')

    def test_multiple_completed_workouts_accumulate(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        # Workout 1 = 1,200 kg
        w1 = Workout.objects.create(user=self.user_a, completed=True)
        e1 = WorkoutExercise.objects.create(workout=w1, exercise=self.dumbbell_curl, sets_planned=3, reps_planned=10, weight=Decimal('40.00'))
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=e1, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)

        # Workout 2 = 800 kg
        w2 = Workout.objects.create(user=self.user_a, completed=True)
        e2 = WorkoutExercise.objects.create(workout=w2, exercise=self.dumbbell_curl, sets_planned=3, reps_planned=10, weight=Decimal('40.00'))
        for s in range(1, 3):
            WorkoutSet.objects.create(workout_exercise=e2, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)
        WorkoutSet.objects.create(workout_exercise=e2, set_number=3, reps_completed=0, weight=None, completed=False, skipped=True)

        # Workout 3 = 2,000 kg
        w3 = Workout.objects.create(user=self.user_a, completed=True)
        e3 = WorkoutExercise.objects.create(workout=w3, exercise=self.bench_press, sets_planned=4, reps_planned=10, weight=Decimal('50.00'))
        for s in range(1, 5):
            WorkoutSet.objects.create(workout_exercise=e3, set_number=s, reps_completed=10, weight=Decimal('50.00'), completed=True)

        # Accumulated = 1,200 + 800 + 2,000 = 4,000 kg
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('4000.00'))
        self.assertEqual(self.profile_a.total_weight_lifted_display, '4,000')

        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.context['total_weight_lifted'], '4,000')
        self.assertContains(response, '<strong>4,000<small> kg</small></strong>')

    def test_incompleted_workout_not_counted(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        # Completed workout: 1,200 kg
        w1 = Workout.objects.create(user=self.user_a, completed=True)
        e1 = WorkoutExercise.objects.create(workout=w1, exercise=self.dumbbell_curl, sets_planned=3, reps_planned=10, weight=Decimal('40.00'))
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=e1, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)

        # Incomplete / in-progress workout: planned 2,000 kg (completed=False)
        w2 = Workout.objects.create(user=self.user_a, completed=False)
        e2 = WorkoutExercise.objects.create(workout=w2, exercise=self.bench_press, sets_planned=4, reps_planned=10, weight=Decimal('50.00'))

        # Only w1 should count -> 1,200 kg
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('1200.00'))
        self.assertEqual(self.profile_a.total_weight_lifted_display, '1,200')

    def test_refresh_does_not_double_count(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        workout = Workout.objects.create(user=self.user_a, completed=True)
        entry = WorkoutExercise.objects.create(workout=workout, exercise=self.dumbbell_curl, sets_planned=3, reps_planned=10, weight=Decimal('40.00'))
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=entry, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)

        self.login_user(self.user_a)
        for _ in range(3):
            r = self.client.get(reverse('workout:dashboard'))
            self.assertEqual(r.context['total_weight_lifted'], '1,200')
            rc = self.client.get(reverse('workout:workout_complete', kwargs={'workout_id': workout.id}))
            self.assertEqual(rc.context['total_volume'], Decimal('1200.00'))

    def test_user_isolation(self):
        from .models import Workout, WorkoutExercise, WorkoutSet
        from decimal import Decimal

        # User A has 1,200 kg
        w_a = Workout.objects.create(user=self.user_a, completed=True)
        e_a = WorkoutExercise.objects.create(workout=w_a, exercise=self.dumbbell_curl, sets_planned=3, reps_planned=10, weight=Decimal('40.00'))
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=e_a, set_number=s, reps_completed=10, weight=Decimal('40.00'), completed=True)

        # User B has 0 kg
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('1200.00'))
        self.assertEqual(self.profile_b.total_weight_lifted, Decimal('0'))

        self.login_user(self.user_b)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.context['total_weight_lifted'], '0')
        self.assertContains(response, '<strong>0<small> kg</small></strong>')

    def test_bodyweight_exercises_contribute_zero(self):
        from .models import Workout, WorkoutExercise, WorkoutSet

        workout = Workout.objects.create(user=self.user_a, completed=True)
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.push_up,
            sets_planned=3, reps_planned=12, weight=None,
        )
        for s in range(1, 4):
            WorkoutSet.objects.create(workout_exercise=entry, set_number=s, reps_completed=12, weight=None, completed=True)

        from decimal import Decimal
        self.assertEqual(entry.volume, None)
        self.assertEqual(workout.total_volume, Decimal('0'))
        self.assertEqual(self.profile_a.total_weight_lifted, Decimal('0'))

        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.context['total_weight_lifted'], '0')

    def test_dashboard_stats_card_order_and_structure(self):
        self.login_user(self.user_a)
        response = self.client.get(reverse('workout:dashboard'))
        content = response.content.decode('utf-8')

        # Check all 5 labels in exact order
        streak_idx = content.find('STREAK')
        bmi_idx = content.find('BMI')
        weight_idx = content.find('WEIGHT')
        total_lifted_idx = content.find('TOTAL WEIGHT LIFTED')
        total_days_idx = content.find('TOTAL DAYS')

        self.assertTrue(streak_idx != -1 and bmi_idx != -1 and weight_idx != -1 and total_lifted_idx != -1 and total_days_idx != -1)
        self.assertTrue(streak_idx < bmi_idx < weight_idx < total_lifted_idx < total_days_idx)


class CompletedSetPersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('set-logger', password='password')
        UserProfile.objects.create(user=self.user, profile_completed=True, workout_location='gym')
        self.exercise = Exercise.objects.create(
            name='Goblet Squat Test', body_part='Legs', equipment_type='dumbbell',
            category='Strength', description='Description', instructions='Instructions',
            muscles_targeted='Legs', is_bodyweight=False,
        )
        self.client.login(username='set-logger', password='password')

    def test_completion_endpoint_persists_each_set_weight_and_reps(self):
        from decimal import Decimal
        from .models import Workout, WorkoutExercise

        workout = Workout.objects.create(user=self.user)
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, sets_planned=3,
            reps_planned=10, weight='10',
        )
        endpoint = reverse('workout:complete_set', kwargs={'entry_id': entry.id})
        for reps, weight in ((10, '10'), (10, '10'), (8, '12')):
            response = self.client.post(endpoint, {'reps': reps, 'weight': weight})
            self.assertEqual(response.status_code, 200)

        workout.refresh_from_db()
        self.assertTrue(workout.completed)
        self.assertEqual(workout.total_volume, 296)
        self.assertEqual(
            list(entry.sets.values_list('reps_completed', 'weight')),
            [(10, Decimal('10.00')), (10, Decimal('10.00')), (8, Decimal('12.00'))],
        )
        response = self.client.get(reverse('workout:progress'), {'range': 'today'})
        self.assertEqual(response.context['summary']['volume'], '296')


class DashboardRecommendationsCountTests(TestCase):
    def setUp(self):
        for i in range(10):
            Exercise.objects.create(
                name=f'Female Exercise {i}', body_part='Legs', equipment_type='bodyweight',
                category='Lower Body & Glutes', description=f'Female desc {i}', instructions='Instructions',
                muscles_targeted='Glutes', is_bodyweight=True, gender_category='female',
            )
            Exercise.objects.create(
                name=f'Male Exercise {i}', body_part='Chest', equipment_type='bodyweight',
                category='Chest', description=f'Male desc {i}', instructions='Instructions',
                muscles_targeted='Chest', is_bodyweight=True, gender_category='all',
            )

    def test_female_dashboard_gives_exactly_4_recommended_exercises(self):
        user = User.objects.create_user('female-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, gender='female', workout_location='gym')
        self.client.login(username='female-user', password='password')
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['plan']['exercises']), 4)
        self.assertContains(response, "Top 4 recommended exercises")

    def test_male_dashboard_gives_exactly_4_recommended_exercises(self):
        user = User.objects.create_user('male-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, gender='male', workout_location='gym')
        self.client.login(username='male-user', password='password')
        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Men's Fitness")
        self.assertContains(response, "Top 4 recommended exercises")


class DietNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_diet_meals')

    def test_all_five_goals_have_seven_days_and_six_meals(self):
        goals = ('bulk', 'cut', 'maintain', 'strength', 'fitness')
        expected_slots = ('breakfast', 'morning_snack', 'lunch', 'evening_snack', 'dinner', 'hydration')
        for goal in goals:
            for day in range(7):
                meals = list(DietMeal.objects.filter(goal=goal, day_of_week=day))
                self.assertEqual(len(meals), 6, f"Goal {goal} Day {day+1} should have exactly 6 meals")
                slot_types = tuple(m.meal_type for m in meals)
                self.assertEqual(set(slot_types), set(expected_slots))

    def test_existing_cut_meals_preserved(self):
        # Day 1 of Cut must have exact requested meals
        day1_meals = {m.meal_type: m.name for m in DietMeal.objects.filter(goal='cut', day_of_week=0)}
        self.assertEqual(day1_meals['breakfast'], 'Vegetable upma + 2 eggs')
        self.assertEqual(day1_meals['morning_snack'], 'Apple + a small handful of almonds')
        self.assertEqual(day1_meals['lunch'], 'Brown rice + chicken/paneer + vegetables')
        self.assertEqual(day1_meals['evening_snack'], 'Roasted chana + lemon')
        self.assertEqual(day1_meals['dinner'], 'Vegetable soup + paneer/chicken + 1–2 roti')
        self.assertEqual(day1_meals['hydration'], 'Keep water nearby and drink regularly throughout the day.')

    def test_case_1_new_user_actual_first_day_hides_previous_and_shows_next(self):
        user = User.objects.create_user('case1-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='case1-user', password='password')

        response = self.client.get(reverse('workout:diet'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '← Previous Day')
        self.assertContains(response, 'Today')
        self.assertContains(response, 'Next Day →')

    def test_case_2_day_2_shows_both_previous_and_next(self):
        user = User.objects.create_user('case2-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='case2-user', password='password')

        # Navigate to next day (Day 2 of user experience: offset 1)
        response = self.client.get(reverse('workout:diet'), {'offset': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '← Previous Day')
        self.assertContains(response, 'Today')
        self.assertContains(response, 'Next Day →')

    def test_case_3_day_7_shows_both_previous_and_next(self):
        user = User.objects.create_user('case3-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='case3-user', password='password')

        # Navigate to Day 7 of user experience (offset 6)
        response = self.client.get(reverse('workout:diet'), {'offset': 6})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '← Previous Day')
        self.assertContains(response, 'Today')
        self.assertContains(response, 'Next Day →')

    def test_case_4_day_7_next_loops_to_day_1_with_previous_available_to_day_7(self):
        user = User.objects.create_user('case4-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='case4-user', password='password')

        # Get Day 7
        r_d7 = self.client.get(reverse('workout:diet'), {'day': 7})
        self.assertEqual(r_d7.context['day_number'], 7)
        self.assertContains(r_d7, 'Oats + milk + fruit + eggs')
        offset_d7 = r_d7.context['offset']

        # Next from Day 7 -> Day 1 (offset_d7 + 1)
        r_looped_d1 = self.client.get(reverse('workout:diet'), {'offset': offset_d7 + 1})
        self.assertEqual(r_looped_d1.status_code, 200)
        self.assertEqual(r_looped_d1.context['day_number'], 1)
        self.assertContains(r_looped_d1, '← Previous Day')
        self.assertContains(r_looped_d1, 'Today')
        self.assertContains(r_looped_d1, 'Next Day →')
        self.assertContains(r_looped_d1, 'Vegetable upma + 2 eggs')

        # Looped Day 1 -> Previous -> Day 7 (offset_d7)
        r_back_to_d7 = self.client.get(reverse('workout:diet'), {'offset': offset_d7})
        self.assertEqual(r_back_to_d7.status_code, 200)
        self.assertEqual(r_back_to_d7.context['day_number'], 7)
        self.assertContains(r_back_to_d7, 'Oats + milk + fruit + eggs')

    def test_case_5_actual_first_ever_day_previous_is_not_available(self):
        user = User.objects.create_user('case5-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='case5-user', password='password')

        # Attempting to navigate before actual first day (e.g. offset -1) is clamped to start date
        response = self.client.get(reverse('workout:diet'), {'offset': -1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['offset'], 0)
        self.assertNotContains(response, '← Previous Day')
        self.assertContains(response, 'Today')
        self.assertContains(response, 'Next Day →')

    def test_goals_remain_unchanged_during_wrapping(self):
        goals_data = {
            'cut': ('Vegetable upma + 2 eggs', 'Oats + milk + fruit + eggs'),
            'bulk': ('Oats with milk, banana + 2–3 eggs', 'Idli + sambar + eggs + fruit'),
            'maintain': ('Vegetable dosa + sambar + 2 eggs', 'Dosa + sambar + eggs + fruit'),
            'strength': ('Oats with milk + banana + 3 eggs', 'Vegetable upma + eggs + curd + fruit'),
            'fitness': ('Vegetable upma + 2 eggs + curd', 'Vegetable oats + eggs + curd'),
        }
        for goal, (day1_meal, day7_meal) in goals_data.items():
            user = User.objects.create_user(f'diet-wrap-{goal}', password='password')
            UserProfile.objects.create(user=user, profile_completed=True, goal=goal)
            self.client.login(username=f'diet-wrap-{goal}', password='password')

            # Day 7 -> Next -> Day 1
            r_d7 = self.client.get(reverse('workout:diet'), {'day': 7})
            self.assertContains(r_d7, day7_meal)
            offset_d7 = r_d7.context['offset']

            r_d1 = self.client.get(reverse('workout:diet'), {'offset': offset_d7 + 1})
            self.assertEqual(r_d1.context['day_number'], 1)
            self.assertContains(r_d1, day1_meal)

            # Day 1 -> Previous -> Day 7
            offset_d1 = r_d1.context['offset']
            r_d7_prev = self.client.get(reverse('workout:diet'), {'offset': offset_d1 - 1})
            self.assertEqual(r_d7_prev.context['day_number'], 7)
            self.assertContains(r_d7_prev, day7_meal)

    def test_cut_exact_seven_day_plan_meals(self):
        user = User.objects.create_user('cut-exact-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='cut-exact-user', password='password')

        expected_days = {
            1: ('Vegetable upma + 2 eggs', 'Apple + a small handful of almonds', 'Brown rice + chicken/paneer + vegetables', 'Roasted chana + lemon', 'Vegetable soup + paneer/chicken + 1–2 roti'),
            2: ('Idli + sambar + curd', 'Greek yogurt + fruit', 'Rice + dal + vegetables + grilled chicken/tofu', 'Guava + peanuts', 'Roti + paneer/chicken + vegetables'),
            3: ('Eggs + whole-grain toast + fruit', 'Apple + curd', 'Brown rice + lean chicken/tofu + vegetables', 'Fruit + a small handful of nuts', 'Roti + dal + mixed vegetables'),
            4: ('Vegetable oats + curd', 'Guava + Greek yogurt', 'Rice + fish/paneer + vegetables', 'Roasted chana', 'Vegetable soup + 1–2 roti + protein'),
            5: ('Poha with vegetables + eggs', 'Orange + yogurt', 'Brown rice + dal + vegetables + chicken/tofu', 'Apple + almonds', 'Roti + paneer + vegetables'),
            6: ('Dosa + sambar + eggs', 'Fruit + curd', 'Rice + fish/chicken + vegetables', 'Roasted chana + fruit', 'Roti + dal + vegetables'),
            7: ('Oats + milk + fruit + eggs', 'Greek yogurt + fruit', 'Brown rice + chicken/paneer + vegetables', 'Guava + a small handful of peanuts', 'Vegetable soup + dal + 1–2 roti'),
        }

        for day_num, meals in expected_days.items():
            resp = self.client.get(reverse('workout:diet'), {'day': day_num})
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Lose Fat / Cut')
            for m in meals:
                self.assertContains(resp, m)

    def test_maintain_exact_seven_day_plan_meals(self):
        user = User.objects.create_user('maint-exact-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='maintain')
        self.client.login(username='maint-exact-user', password='password')

        expected_days = {
            1: ('Vegetable dosa + sambar + 2 eggs', 'Apple + Greek yogurt', 'Rice + dal + mixed vegetables + grilled chicken/paneer', 'Roasted chana + seasonal fruit', '2 roti + paneer/tofu + mixed vegetables'),
            2: ('Oats with milk + banana + almonds', 'Guava + curd', 'Brown rice + chicken/tofu + vegetables', 'Fruit + small handful of peanuts', 'Chapati + dal + vegetable curry + curd'),
            3: ('Idli + sambar + curd + fruit', 'Greek yogurt + mixed fruit', 'Rice + fish/paneer + vegetables', 'Apple + almonds', 'Roti + chicken/tofu + vegetable curry'),
            4: ('Vegetable poha + 2 eggs + fruit', 'Banana + curd', 'Brown rice + dal + vegetables + paneer', 'Roasted chana + fruit', 'Chapati + chicken/fish + vegetables'),
            5: ('Vegetable upma + eggs + curd', 'Orange + Greek yogurt', 'Rice + chicken/tofu + dal + vegetables', 'Apple + small handful of nuts', 'Roti + paneer + vegetables + curd'),
            6: ('Whole-grain toast + vegetable omelette + fruit', 'Guava + peanuts', 'Brown rice + fish/chicken + vegetables', 'Greek yogurt + banana', 'Chapati + dal + mixed vegetables + paneer/tofu'),
            7: ('Dosa + sambar + eggs + fruit', 'Curd + almonds + seasonal fruit', 'Rice + paneer/chicken + dal + vegetables', 'Roasted chana + banana', 'Roti + fish/tofu + vegetables + curd'),
        }

        for day_num, meals in expected_days.items():
            resp = self.client.get(reverse('workout:diet'), {'day': day_num})
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Maintain Weight')
            for m in meals:
                self.assertContains(resp, m)

    def test_strength_exact_seven_day_plan_meals(self):
        user = User.objects.create_user('strength-exact-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='strength')
        self.client.login(username='strength-exact-user', password='password')

        expected_days = {
            1: ('Oats with milk + banana + 3 eggs', 'Greek yogurt + banana + walnuts', 'Chicken + rice + dal + mixed vegetables', 'Peanut butter whole-grain toast + fruit', 'Roti + chicken/paneer + vegetables + curd'),
            2: ('Vegetable omelette + whole-grain toast + fruit', 'Milk + banana + almonds', 'Brown rice + fish + vegetables + dal', 'Roasted chana + fruit', 'Chapati + paneer + vegetable curry + curd'),
            3: ('Idli + sambar + 3 eggs + fruit', 'Greek yogurt + nuts', 'Rice + chicken + dal + vegetables', 'Banana + peanut butter', 'Roti + fish + vegetables + curd'),
            4: ('Poha with peanuts + eggs + curd', 'Milk + banana + almonds', 'Rice + paneer + dal + mixed vegetables', 'Whole-grain toast + Greek yogurt', 'Chapati + chicken + vegetables + dal'),
            5: ('Dosa + sambar + eggs + curd', 'Banana + Greek yogurt + walnuts', 'Brown rice + chicken + vegetables + dal', 'Roasted chana + fruit', 'Roti + paneer/tofu + vegetables + curd'),
            6: ('Oats + milk + banana + peanut butter + eggs', 'Curd + fruit + almonds', 'Rice + fish/chicken + dal + vegetables', 'Peanut butter whole-grain toast + banana', 'Chapati + chicken/paneer + vegetables'),
            7: ('Vegetable upma + eggs + curd + fruit', 'Greek yogurt + banana + nuts', 'Rice + chicken/paneer + dal + vegetables', 'Milk + banana + peanut butter', 'Roti + fish/tofu + vegetables + curd'),
        }

        for day_num, meals in expected_days.items():
            resp = self.client.get(reverse('workout:diet'), {'day': day_num})
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Build Strength')
            for m in meals:
                self.assertContains(resp, m)

    def test_fitness_exact_seven_day_plan_meals(self):
        user = User.objects.create_user('fitness-exact-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='fitness')
        self.client.login(username='fitness-exact-user', password='password')

        expected_days = {
            1: ('Vegetable upma + 2 eggs + curd', 'Apple + Greek yogurt', 'Rice + dal + mixed vegetables + chicken/paneer', 'Roasted chana + seasonal fruit', '2 roti + paneer/tofu + mixed vegetables'),
            2: ('Idli + sambar + curd + fruit', 'Guava + a small handful of almonds', 'Brown rice + chicken/tofu + vegetables', 'Banana + peanuts', 'Chapati + dal + vegetable curry + curd'),
            3: ('Oats with milk + banana + nuts', 'Greek yogurt + seasonal fruit', 'Rice + fish/paneer + vegetables + dal', 'Roasted chana + fruit', 'Roti + chicken/tofu + mixed vegetables'),
            4: ('Vegetable poha + 2 eggs + fruit', 'Apple + curd', 'Brown rice + dal + paneer + vegetables', 'Greek yogurt + banana', 'Chapati + chicken/fish + vegetables'),
            5: ('Dosa + sambar + eggs + fruit', 'Guava + Greek yogurt', 'Rice + chicken/tofu + dal + vegetables', 'Apple + almonds', 'Roti + paneer + vegetable curry + curd'),
            6: ('Whole-grain toast + vegetable omelette + fruit', 'Banana + curd + a few nuts', 'Brown rice + fish/chicken + vegetables', 'Roasted chana + seasonal fruit', 'Chapati + dal + paneer/tofu + vegetables'),
            7: ('Vegetable oats + eggs + curd', 'Orange + Greek yogurt', 'Rice + paneer/chicken + dal + vegetables', 'Fruit + mixed nuts', 'Roti + fish/tofu + vegetables + curd'),
        }

        for day_num, meals in expected_days.items():
            resp = self.client.get(reverse('workout:diet'), {'day': day_num})
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'General Fitness')
            for m in meals:
                self.assertContains(resp, m)

    def test_bulk_exact_seven_day_plan_meals(self):
        user = User.objects.create_user('bulk-exact-user', password='password')
        UserProfile.objects.create(user=user, profile_completed=True, goal='bulk')
        self.client.login(username='bulk-exact-user', password='password')

        expected_days = {
            1: ('Oats with milk, banana + 2–3 eggs', 'Greek yogurt + almonds', 'Rice + chicken/paneer + vegetables', 'Peanut butter whole-grain toast + fruit', 'Roti + paneer/chicken + dal + vegetables'),
            2: ('3–4 eggs + whole-grain toast + banana', 'Curd + mixed nuts', 'Brown rice + chicken/tofu + dal + vegetables', 'Banana + peanut butter', 'Chapati + paneer curry + vegetables'),
            3: ('Vegetable dosa + sambar + eggs', 'Greek yogurt + banana + walnuts', 'Rice + fish/paneer + vegetables', 'Sprouts + fruit', 'Roti + chicken/tofu + dal'),
            4: ('Vegetable upma + eggs + curd', 'Milk + banana + almonds', 'Rice + chicken/paneer + rajma + vegetables', 'Peanut butter sandwich + fruit', 'Chapati + fish/paneer + vegetables'),
            5: ('Poha with peanuts + eggs + fruit', 'Greek yogurt + nuts', 'Brown rice + chicken/tofu + dal + vegetables', 'Milk + banana + peanut butter', 'Roti + paneer/chicken + vegetables'),
            6: ('Oats + milk + banana + peanut butter + eggs', 'Curd + fruit + almonds', 'Rice + fish/chicken/paneer + dal + vegetables', 'Sprouts + whole-grain toast', 'Chapati + chicken/paneer + vegetables'),
            7: ('Idli + sambar + eggs + fruit', 'Greek yogurt + banana + nuts', 'Rice + chicken/paneer + dal + vegetables', 'Peanut butter toast + milk', 'Roti + paneer/tofu + vegetables + curd'),
        }

        for day_num, meals in expected_days.items():
            resp = self.client.get(reverse('workout:diet'), {'day': day_num})
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Build Muscle / Bulk')
            for m in meals:
                self.assertContains(resp, m)

    def test_changing_profile_goal_changes_diet_page_meals(self):
        user = User.objects.create_user('diet-goal-switch', password='password')
        profile = UserProfile.objects.create(user=user, profile_completed=True, goal='cut')
        self.client.login(username='diet-goal-switch', password='password')

        # On Cut, day 1 shows Vegetable upma + 2 eggs
        resp_cut = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_cut, 'Vegetable upma + 2 eggs')
        self.assertContains(resp_cut, 'Lose Fat / Cut')

        # Change goal to Bulk
        profile.goal = 'bulk'
        profile.save(update_fields=['goal'])
        resp_bulk = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_bulk, 'Oats with milk, banana + 2–3 eggs')
        self.assertContains(resp_bulk, 'Build Muscle / Bulk')

        # Change goal to Maintain
        profile.goal = 'maintain'
        profile.save(update_fields=['goal'])
        resp_maint = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_maint, 'Vegetable dosa + sambar + 2 eggs')
        self.assertContains(resp_maint, 'Maintain Weight')

        # Change goal to Strength
        profile.goal = 'strength'
        profile.save(update_fields=['goal'])
        resp_str = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_str, 'Oats with milk + banana + 3 eggs')
        self.assertContains(resp_str, 'Build Strength')

        # Change goal to Fitness
        profile.goal = 'fitness'
        profile.save(update_fields=['goal'])
        resp_fit = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_fit, 'Vegetable upma + 2 eggs + curd')
        self.assertContains(resp_fit, 'General Fitness')

        # Change goal back to Cut
        profile.goal = 'cut'
        profile.save(update_fields=['goal'])
        resp_cut2 = self.client.get(reverse('workout:diet'), {'day': 1})
        self.assertContains(resp_cut2, 'Vegetable upma + 2 eggs')
        self.assertContains(resp_cut2, 'Lose Fat / Cut')


class DashboardRecommendationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_exercises')

    def test_male_dashboard_recommended_section_structure(self):
        user = User.objects.create_user('male-dash-user', password='password')
        profile = UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='cut', workout_location='gym', experience_level='beginner'
        )
        self.client.login(username='male-dash-user', password='password')

        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Heading and subtitle
        self.assertContains(response, "Men's Fitness")
        self.assertContains(response, "Top 4 recommended exercises curated for your goals and experience level.")
        self.assertContains(response, "PERSONALIZED FOR YOU")
        self.assertContains(response, "Browse All Exercises")

        # Context has exactly 4 exercises
        exercises = response.context['plan']['exercises']
        self.assertEqual(len(exercises), 4)

        # Card elements: View Details, bodypart badge
        self.assertContains(response, "View Details")

    def test_female_dashboard_recommended_section_structure(self):
        user = User.objects.create_user('female-dash-user', password='password')
        profile = UserProfile.objects.create(
            user=user, profile_completed=True, gender='female',
            goal='cut', workout_location='home', experience_level='beginner'
        )
        self.client.login(username='female-dash-user', password='password')

        response = self.client.get(reverse('workout:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Women's Fitness")
        self.assertContains(response, "Top 4 recommended exercises curated for your goals and experience level.")
        self.assertContains(response, "Browse All Exercises")
        self.assertContains(response, "View Details")

        exercises = response.context['plan']['exercises']
        self.assertEqual(len(exercises), 4)


class MaleExerciseDetailsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_exercises')
        call_command('seed_womens_exercises')

    def test_ninety_four_male_exercises_have_unique_details(self):
        from workout.recommendations import get_available_exercises, MALE_LIBRARY_BODY_PARTS
        user = User.objects.create_user('male-detail-user', password='password')
        profile = UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        male_exercises = get_available_exercises(profile).filter(body_part__in=MALE_LIBRARY_BODY_PARTS)
        self.assertEqual(male_exercises.count(), 94)

        descriptions = set()
        instructions_set = set()
        beginner_tips_set = set()

        for ex in male_exercises:
            self.assertTrue(len(ex.description.strip()) >= 30, f"{ex.name} description is too short")
            self.assertNotIn("straightforward", ex.description.lower())
            descriptions.add(ex.description.strip())

            steps = [line.strip() for line in ex.instructions.split('\n') if line.strip() and line.strip()[0].isdigit()]
            self.assertTrue(4 <= len(steps) <= 6, f"{ex.name} has {len(steps)} steps instead of 4-6")
            self.assertNotIn("move slowly with control", ex.instructions.lower())
            instructions_set.add(ex.instructions.strip())

            self.assertTrue(len(ex.beginner_tips.strip()) >= 20, f"{ex.name} beginner tip is too short")
            self.assertNotIn("start light, focus on smooth technique", ex.beginner_tips.lower())
            beginner_tips_set.add(ex.beginner_tips.strip())

        self.assertEqual(len(descriptions), 94)
        self.assertEqual(len(instructions_set), 94)
        self.assertEqual(len(beginner_tips_set), 94)

    def test_exercise_detail_page_removes_duplicate_category_badge(self):
        user = User.objects.create_user('detail-badge-user', password='password')
        UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        self.client.login(username='detail-badge-user', password='password')

        # Bear Crawl has category='Full Body', body_part='Full Body', difficulty='intermediate'
        bear_crawl = Exercise.objects.get(name='Bear Crawl')
        resp = self.client.get(reverse('workout:exercise_detail', args=[bear_crawl.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Bear Crawl is a full-body dynamic movement')
        self.assertContains(resp, '<li>Start on all fours with hands stacked under your shoulders and knees under your hips.</li>')
        self.assertContains(resp, 'Do not let your hips rise into the air')

        # In media-badges, 'Full Body' should appear only once as a badge
        content = resp.content.decode()
        start = content.find('class="media-badges"')
        end = content.find('</div>', start)
        media_badges_html = content[start:end]
        self.assertEqual(media_badges_html.count('Full Body'), 1)

    def test_workout_session_movement_form_numbered_list(self):
        user = User.objects.create_user('session-form-user', password='password')
        UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        self.client.login(username='session-form-user', password='password')

        from workout.models import Workout, WorkoutExercise
        workout = Workout.objects.create(user=user)
        back_squat = Exercise.objects.get(name='Back Squat')
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=back_squat,
            sets_planned=3, reps_planned=10, rest_seconds=60, exercise_seconds=45
        )

        resp = self.client.get(reverse('workout:workout_session', args=[entry.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Movement Form')
        self.assertContains(resp, '<ol class="movement-form-list">')
        self.assertContains(resp, '<li>Position a barbell across your upper back and traps, gripping the bar firmly with hands slightly wider than shoulders.</li>')
        self.assertContains(resp, '<li>Exhale as you lock out your hips and reset your brace for the next rep.</li>')

    def test_all_94_male_exercises_image_consistency(self):
        from workout.recommendations import get_available_exercises, MALE_LIBRARY_BODY_PARTS
        from workout.models import Workout, WorkoutExercise
        import re

        user = User.objects.create_user('img-audit-user', password='password')
        profile = UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        self.client.login(username='img-audit-user', password='password')
        male_exercises = get_available_exercises(profile).filter(body_part__in=MALE_LIBRARY_BODY_PARTS)
        self.assertEqual(male_exercises.count(), 94)

        workout = Workout.objects.create(user=user)

        for ex in male_exercises:
            # 1. Detail page image
            resp_d = self.client.get(reverse('workout:exercise_detail', args=[ex.id]))
            self.assertEqual(resp_d.status_code, 200)
            m_d = re.search(r'class="detail-photo"\s+src="([^"]+)"', resp_d.content.decode())
            self.assertTrue(bool(m_d), f"Detail photo not found for {ex.name}")
            img_d = m_d.group(1).split('?')[0]

            # 2. Workout session image
            entry = WorkoutExercise.objects.create(
                workout=workout, exercise=ex, sets_planned=3, reps_planned=10, rest_seconds=60, exercise_seconds=45
            )
            resp_w = self.client.get(reverse('workout:workout_session', args=[entry.id]))
            self.assertEqual(resp_w.status_code, 200)
            m_w = re.search(r'src="([^"]+)"\s+alt="Photo for [^"]*"\s+class="exercise-photo"', resp_w.content.decode())
            self.assertTrue(bool(m_w), f"Workout photo not found for {ex.name}")
            img_w = m_w.group(1).split('?')[0]

            self.assertEqual(img_d, img_w, f"Image mismatch for {ex.name}: detail has {img_d}, workout has {img_w}")
            self.assertIn('/static/workout/images/male/', img_d)

    def test_workout_session_duplicate_category_eyebrow_fixed(self):
        from workout.models import Workout, WorkoutExercise
        user = User.objects.create_user('eyebrow-audit-user', password='password')
        UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        self.client.login(username='eyebrow-audit-user', password='password')

        workout = Workout.objects.create(user=user)
        # Overhead Press has body_part='Shoulders' and category='Shoulders'
        overhead_press = Exercise.objects.get(name='Overhead Press')
        entry = WorkoutExercise.objects.create(
            workout=workout, exercise=overhead_press,
            sets_planned=3, reps_planned=10, rest_seconds=60, exercise_seconds=45
        )
        resp = self.client.get(reverse('workout:workout_session', args=[entry.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<p class="eyebrow">SHOULDERS</p>')
        self.assertNotContains(resp, 'SHOULDERS · SHOULDERS')

    def test_all_94_male_exercises_have_tailored_recommended_workout(self):
        from workout.recommendations import get_available_exercises, MALE_LIBRARY_BODY_PARTS
        import re

        user = User.objects.create_user('rec-test-user', password='password')
        profile = UserProfile.objects.create(
            user=user, profile_completed=True, gender='male',
            goal='fitness', workout_location='gym'
        )
        self.client.login(username='rec-test-user', password='password')

        male_exercises = get_available_exercises(profile).filter(body_part__in=MALE_LIBRARY_BODY_PARTS)
        self.assertEqual(male_exercises.count(), 94)

        for ex in male_exercises:
            self.assertTrue(bool(ex.recommended_sets), f"{ex.name} missing recommended_sets")
            self.assertTrue(bool(ex.recommended_reps or ex.recommended_duration), f"{ex.name} missing both reps and duration")
            self.assertTrue(bool(ex.recommended_rest), f"{ex.name} missing recommended_rest")

            resp = self.client.get(reverse('workout:exercise_detail', args=[ex.id]))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Recommended Workout')
            self.assertContains(resp, 'wf-male')
            cards = re.findall(r'<div class="wf-param-card">', resp.content.decode())
            self.assertEqual(len(cards), 3, f"{ex.name} does not render exactly 3 parameter cards")


class FoodDetailDataIntegrityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_diet_meals')

    def test_every_diet_meal_has_complete_unique_details(self):
        from workout.diet_details import get_meal_details
        goals = ('bulk', 'cut', 'maintain', 'strength', 'fitness')
        for goal in goals:
            meals = DietMeal.objects.filter(goal=goal)
            self.assertEqual(meals.count(), 42) # 7 days * 6 meals
            for meal in meals:
                detail = get_meal_details(meal)
                self.assertIsNotNone(detail, f"Missing detail for {meal.name} ({meal.goal})")
                self.assertTrue(bool(detail.get('description')), f"Empty description for {meal.name}")
                self.assertIn('calories', detail)
                self.assertTrue(bool(detail.get('why_this_meal')), f"Empty why_this_meal for {meal.name}")
                self.assertTrue(bool(detail.get('goal_benefit')), f"Empty goal_benefit for {meal.name}")
                self.assertTrue(bool(detail.get('nutrition_tip')), f"Empty nutrition_tip for {meal.name}")

                if meal.meal_type == 'hydration':
                    self.assertTrue(detail.get('is_hydration'))
                    self.assertTrue(bool(detail.get('habit_text')))
                    self.assertGreaterEqual(len(detail.get('guidance', [])), 4)
                else:
                    self.assertFalse(detail.get('is_hydration'))
                    self.assertGreaterEqual(len(detail.get('ingredients', [])), 2, f"Too few ingredients for {meal.name}")
                    self.assertGreaterEqual(len(detail.get('preparation_steps', [])), 3, f"Too few prep steps for {meal.name}")
                    self.assertGreaterEqual(len(detail.get('substitutions', [])), 1, f"Missing substitutions for {meal.name}")

    def test_goal_specific_text_changes_dynamically_with_user_goal(self):
        from workout.diet_details import get_meal_details
        sample_meal = DietMeal.objects.filter(name='Whole-grain toast + vegetable omelette + fruit').first()
        if not sample_meal:
            sample_meal = DietMeal.objects.exclude(meal_type='hydration').first()

        benefits = {}
        for goal_code in ('bulk', 'cut', 'maintain', 'strength', 'fitness'):
            mock_profile = type('Profile', (), {'goal': goal_code})()
            det = get_meal_details(sample_meal, mock_profile)
            benefits[goal_code] = det['goal_benefit']

        # Ensure benefits are populated
        for goal_code, text in benefits.items():
            self.assertTrue(bool(text), f"Empty benefit for {goal_code}")

        # Check keyword alignments
        self.assertIn('muscle', benefits['bulk'].lower())
        self.assertTrue('cut' in benefits['cut'].lower() or 'fullness' in benefits['cut'].lower() or 'fat' in benefits['cut'].lower() or 'satiety' in benefits['cut'].lower())
        self.assertTrue('maintain' in benefits['maintain'].lower() or 'balanced' in benefits['maintain'].lower() or 'everyday' in benefits['maintain'].lower())
        self.assertTrue('strength' in benefits['strength'].lower() or 'performance' in benefits['strength'].lower() or 'power' in benefits['strength'].lower() or 'recovery' in benefits['strength'].lower())
        self.assertTrue('fitness' in benefits['fitness'].lower() or 'vitality' in benefits['fitness'].lower() or 'endurance' in benefits['fitness'].lower() or 'everyday' in benefits['fitness'].lower())


class DietPageFoodDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command
        call_command('seed_diet_meals')

    def test_diet_page_contains_modal_markup_and_interactive_cards(self):
        user = User.objects.create_user('diet-modal-user', password='password')
        UserProfile.objects.create(
            user=user, profile_completed=True, goal='fitness', gender='female'
        )
        self.client.login(username='diet-modal-user', password='password')

        resp = self.client.get(reverse('workout:diet'))
        self.assertEqual(resp.status_code, 200)

        # Main food cards are interactive
        self.assertContains(resp, 'meal-card-interactive')
        self.assertContains(resp, 'role="button"')
        self.assertContains(resp, 'aria-haspopup="dialog"')
        self.assertContains(resp, 'View details &amp; recipe')

        # Modal overlay structure
        self.assertContains(resp, 'id="food-detail-overlay"')
        self.assertContains(resp, 'id="modal-backdrop"')
        self.assertContains(resp, 'id="modal-close-x"')
        self.assertContains(resp, 'id="modal-standard-view"')
        self.assertContains(resp, 'id="modal-hydration-view"')

        # Specific section titles
        self.assertContains(resp, 'INGREDIENTS')
        self.assertContains(resp, 'HOW TO PREPARE')
        self.assertContains(resp, 'WHY THIS MEAL?')
        self.assertContains(resp, 'GOOD FOR YOUR GOAL')
        self.assertContains(resp, 'POSSIBLE SUBSTITUTIONS')
        self.assertContains(resp, 'NUTRITION TIP')

        # Nutrition values approximate disclaimer
        self.assertContains(resp, 'Nutrition values are approximate')

        # Macro cards
        self.assertContains(resp, 'modal-macro-calories')
        self.assertContains(resp, 'modal-macro-protein')
        self.assertContains(resp, 'modal-macro-carbs')
        self.assertContains(resp, 'modal-macro-fat')
        self.assertContains(resp, 'modal-macro-fiber')

        # Hydration view components
        self.assertContains(resp, 'Daily Hydration &amp; Fluid Balance')
        self.assertContains(resp, 'Keep water nearby and drink regularly throughout the day.')
        self.assertContains(resp, 'RECOMMENDED HABIT')

    def test_diet_page_across_all_five_goals(self):
        goals = ('bulk', 'cut', 'maintain', 'strength', 'fitness')
        for goal in goals:
            user = User.objects.create_user(f'diet-user-{goal}', password='password')
            UserProfile.objects.create(
                user=user, profile_completed=True, goal=goal, gender='male'
            )
            self.client.login(username=f'diet-user-{goal}', password='password')

            resp = self.client.get(reverse('workout:diet'))
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'food-modal-overlay')
            # Exactly 6 meal payloads per day
            self.assertEqual(resp.content.decode().count('meal-json-payload'), 6)


class ProgressAnalyticsRedesignTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('analytics-user', password='password')
        self.profile = UserProfile.objects.create(
            user=self.user, profile_completed=True, workout_location='gym',
            current_streak=3, longest_streak=7
        )
        self.client.login(username='analytics-user', password='password')

        self.ex_bench = Exercise.objects.create(
            name='Barbell Bench Press', body_part='Chest', equipment_type='barbell',
            category='Chest', description='Chest press', instructions='Press', muscles_targeted='Chest, Triceps'
        )
        self.ex_squat = Exercise.objects.create(
            name='Barbell Squat', body_part='Legs', equipment_type='barbell',
            category='Legs', description='Squat', instructions='Squat down', muscles_targeted='Quadriceps, Glutes'
        )
        self.ex_row = Exercise.objects.create(
            name='Dumbbell Row', body_part='Back', equipment_type='dumbbell',
            category='Back', description='Row', instructions='Pull', muscles_targeted='Back, Biceps'
        )

        from django.utils import timezone
        self.create_workout_session(self.user, timezone.localdate(), [
            (self.ex_bench, [(10, 60, True), (10, 60, True)]),
        ])

    def create_workout_session(self, user, workout_date, exercises_data, completed=True):
        from django.utils import timezone
        import datetime
        dt = timezone.make_aware(datetime.datetime.combine(workout_date, datetime.time(10, 0)))
        w = Workout.objects.create(
            user=user, date=workout_date, completed=completed,
            created_at=dt, completed_at=dt + datetime.timedelta(minutes=45) if completed else None
        )
        for order, (exercise, sets_info) in enumerate(exercises_data, 1):
            entry = WorkoutExercise.objects.create(
                workout=w, exercise=exercise, sets_planned=len(sets_info),
                reps_planned=10, weight=sets_info[0][1] if sets_info else 50, order=order
            )
            for set_num, (reps, weight, set_comp) in enumerate(sets_info, 1):
                WorkoutSet.objects.create(
                    workout_exercise=entry, set_number=set_num, reps_completed=reps,
                    weight=weight, completed=set_comp
                )
        return w

    def test_progress_view_authenticated_and_structure(self):
        resp = self.client.get(reverse('workout:progress'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'workout/progress.html')
        self.assertContains(resp, 'Your training, clearly tracked')
        self.assertContains(resp, 'A simple view of your completed workouts, consistency, and training volume.')
        self.assertContains(resp, 'TOTAL WORKOUTS')
        self.assertContains(resp, 'CURRENT STREAK')
        self.assertContains(resp, 'WORKOUT TIME')
        self.assertContains(resp, 'TOTAL SETS')
        self.assertContains(resp, 'TOTAL REPS')
        self.assertContains(resp, 'TOTAL VOLUME')
        self.assertContains(resp, '12-month workout activity')
        self.assertContains(resp, 'Workout Frequency')
        self.assertContains(resp, 'Training Volume')
        self.assertContains(resp, 'What your activity shows')
        self.assertContains(resp, 'Achievements')
        self.assertContains(resp, 'Completed workouts')
        self.assertContains(resp, 'heatmap-modal-backdrop')

    def test_analytics_kpi_and_day_details_with_real_data(self):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.localdate()

        user2 = User.objects.create_user('kpi-user', password='password')
        UserProfile.objects.create(user=user2, profile_completed=True, workout_location='gym')
        self.client.login(username='kpi-user', password='password')

        # Workout today: 3 sets Bench + 2 sets Squat
        # Volume = 3 * 10 * 60 + 2 * 10 * 80 = 1800 + 1600 = 3400 kg
        self.create_workout_session(user2, today, [
            (self.ex_bench, [(10, 60, True), (10, 60, True), (10, 60, True)]),
            (self.ex_squat, [(10, 80, True), (10, 80, True)]),
        ])

        # Workout 2 days ago: 2 sets Row
        # Volume = 2 * 12 * 25 = 600 kg
        self.create_workout_session(user2, today - timedelta(days=2), [
            (self.ex_row, [(12, 25, True), (12, 25, True)]),
        ])

        resp = self.client.get(reverse('workout:progress') + '?range=30d')
        self.assertEqual(resp.status_code, 200)

        summary = resp.context['summary']
        self.assertEqual(summary['workouts'], 2)
        self.assertEqual(summary['sets'], 7)
        self.assertEqual(summary['reps'], 74)  # 3*10 + 2*10 + 2*12 = 74 reps
        self.assertEqual(summary['volume'], '4,000')  # 3400 + 600 = 4000 kg

        # Check chart data dayDetails contains rich workout data
        chart_data = resp.context['chart_data']
        today_iso = today.isoformat()
        self.assertIn(today_iso, chart_data['dayDetails'])
        day_info = chart_data['dayDetails'][today_iso]
        self.assertEqual(day_info['workout_count'], 1)
        self.assertEqual(day_info['total_sets'], 5)
        self.assertEqual(day_info['total_volume'], '3,400')

    def test_milestones_and_streak_progress(self):
        resp = self.client.get(reverse('workout:progress'))
        milestones = resp.context['milestones']
        self.assertEqual(len(milestones), 6)
        first_workout_m = milestones[0]
        self.assertEqual(first_workout_m, (1, 'First Workout'))

    def test_empty_state_for_brand_new_user(self):
        new_user = User.objects.create_user('empty-analytics-user', password='password')
        UserProfile.objects.create(user=new_user, profile_completed=True)
        self.client.login(username='empty-analytics-user', password='password')

        resp = self.client.get(reverse('workout:progress'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Your progress will appear here')
        self.assertContains(resp, 'Start Workout')

    def test_workout_day_detail_shows_all_workouts_for_date(self):
        from decimal import Decimal
        from django.utils import timezone
        today = timezone.localdate()
        user3 = User.objects.create_user('multi-workout-user', password='password')
        UserProfile.objects.create(user=user3, profile_completed=True)
        self.client.login(username='multi-workout-user', password='password')

        # Create Workout 1 on today
        self.create_workout_session(user3, today, [
            (self.ex_bench, [(10, 60, True), (10, 60, True)]),
        ])
        # Create Workout 2 on today
        self.create_workout_session(user3, today, [
            (self.ex_squat, [(10, 80, True)]),
        ])

        today_iso = today.isoformat()
        resp = self.client.get(reverse('workout:workout_day_detail', args=[today_iso]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'workout/workout_day_detail.html')
        self.assertEqual(resp.context['workout_count'], 2)
        self.assertEqual(resp.context['completed_sets'], 3)
        self.assertEqual(resp.context['total_reps'], 30)
        self.assertEqual(resp.context['total_volume'], Decimal('2000'))
        self.assertContains(resp, '2 Completed Workouts')
        self.assertContains(resp, 'Session Breakdown')

    def test_charts_bucket_aggregation(self):
        resp_7d = self.client.get(reverse('workout:progress') + '?range=7d')
        self.assertEqual(len(resp_7d.context['chart_data']['frequency']), 7)

        resp_30d = self.client.get(reverse('workout:progress') + '?range=30d')
        self.assertEqual(len(resp_30d.context['chart_data']['frequency']), 30)

        resp_3m = self.client.get(reverse('workout:progress') + '?range=3m')
        self.assertEqual(len(resp_3m.context['chart_data']['frequency']), 13)

        resp_6m = self.client.get(reverse('workout:progress') + '?range=6m')
        self.assertEqual(len(resp_6m.context['chart_data']['frequency']), 6)

        resp_1y = self.client.get(reverse('workout:progress') + '?range=1y')
        self.assertEqual(len(resp_1y.context['chart_data']['frequency']), 12)







