from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Exercise, UserProfile


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
        self.assertEqual(len(response.context['plan']['exercises']), 4)
        self.assertContains(response, "Recommended exercises")
