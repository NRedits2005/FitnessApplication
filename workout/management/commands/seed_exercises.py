from django.core.management.base import BaseCommand
from workout.models import Exercise


EXERCISES = {
    'Chest': 'Bench Press,Incline Bench Press,Decline Bench Press,Dumbbell Bench Press,Incline Dumbbell Press,Dumbbell Fly,Chest Fly Machine,Push-Up,Wide Push-Up,Diamond Push-Up,Decline Push-Up,Incline Push-Up,Chest Fly,Cable Crossover',
    'Back': 'Pull-Up,Chin-Up,Lat Pulldown,Seated Cable Row,Barbell Row,Dumbbell Row,Deadlift,Face Pull',
    'Legs': 'Squat,Back Squat,Goblet Squat,Front Squat,Leg Press,Romanian Deadlift,Lunges,Walking Lunges,Bulgarian Split Squat,Leg Curl,Leg Extension,Calf Raise,Hip Thrust,Glute Bridge',
    'Shoulders': 'Overhead Press,Dumbbell Shoulder Press,Arnold Press,Lateral Raise,Front Raise,Rear Delt Fly,Pike Push-Up,Handstand Push-Up',
    'Arms': 'Bicep Curl,Dumbbell Curl,Hammer Curl,Preacher Curl,Concentration Curl,Tricep Pushdown,Overhead Tricep Extension,Skull Crushers,Dips,Close-Grip Push-Up',
    'Core': 'Plank,Side Plank,Crunch,Sit-Up,Bicycle Crunch,Leg Raise,Hanging Leg Raise,Mountain Climbers,Russian Twist,Dead Bug',
    'Calisthenics': 'Push-Up,Wide Push-Up,Diamond Push-Up,Pull-Up,Chin-Up,Dips,Bodyweight Squat,Pistol Squat,Bulgarian Split Squat,Pike Push-Up,Handstand,Handstand Push-Up,L-Sit,Hollow Body Hold,Arch Hold,Muscle-Up,Front Lever,Back Lever',
    'Cardio': 'Running,Walking,Cycling,Jump Rope,Jumping Jacks,High Knees,Burpees,Mountain Climbers',
    'Full Body': "Kettlebell Swing,Thruster,Clean and Press,Turkish Get-Up,Bear Crawl,Band Row,Band Chest Press,Band Bicep Curl,Band Tricep Extension,Band Shoulder Press,Band Lateral Raise,Band Squat,Band Glute Bridge,Dead Hang,Hanging Knee Raise",
    'Beginner': 'Wall Push-Up,Knee Push-Up,Bodyweight Squat,Glute Bridge,Step-Up,Standing Calf Raise,Plank,Bird Dog,Dead Bug',
}
BODYWEIGHT = {'Push-Up','Wide Push-Up','Diamond Push-Up','Incline Push-Up','Decline Push-Up','Close-Grip Push-Up','Pull-Up','Chin-Up','Dips','Pike Push-Up','Handstand Push-Up','Plank','Side Plank','Crunch','Sit-Up','Bicycle Crunch','Leg Raise','Hanging Leg Raise','Mountain Climbers','Russian Twist','Dead Bug','Pistol Squat','Handstand','L-Sit','Hollow Body Hold','Arch Hold','Muscle-Up','Front Lever','Back Lever','Running','Walking','Cycling','Jump Rope','Jumping Jacks','High Knees','Burpees','Wall Push-Up','Knee Push-Up','Bodyweight Squat','Step-Up','Standing Calf Raise','Bird Dog','Glute Bridge','Lunges','Walking Lunges','Bulgarian Split Squat','Bear Crawl'}
PHOTO_OVERRIDES = {
    'Squat': '/static/workout/images/squat-photo.png',
    'Bench Press': '/static/workout/images/fitness-plus/bench_press.jpg',
    'Bicep Curl': '/static/workout/images/fitness-plus/bicep_curl.gif',
    'Deadlift': '/static/workout/images/fitness-plus/deadlift.jpg',
    'Dumbbell Row': '/static/workout/images/fitness-plus/dumbbell_row.jpg',
    'Kettlebell Swing': '/static/workout/images/fitness-plus/kettlebell_swing.jpg',
    'Leg Press': '/static/workout/images/fitness-plus/leg_press.gif',
    'Lunges': '/static/workout/images/fitness-plus/lunges.gif',
    'Mountain Climbers': '/static/workout/images/fitness-plus/mountain_climbers.gif',
    'Plank': '/static/workout/images/fitness-plus/plank.gif',
    'Pull-Up': '/static/workout/images/fitness-plus/pull_up.gif',
    'Push-Up': '/static/workout/images/fitness-plus/push_up.gif',
    'Running': '/static/workout/images/fitness-plus/running.gif',
    'Dumbbell Shoulder Press': '/static/workout/images/fitness-plus/shoulder_press.jpg',
    'Tricep Pushdown': '/static/workout/images/fitness-plus/tricep_extension.gif',
}


def equipment_for(name, bodyweight):
    if bodyweight:
        return 'bodyweight'
    lowered = name.lower()
    if 'band' in lowered:
        return 'resistance_band'
    if any(word in lowered for word in ('kettlebell', 'goblet', 'turkish get-up')):
        return 'kettlebell'
    if any(word in lowered for word in ('cable', 'pushdown', 'face pull')):
        return 'cable'
    if any(word in lowered for word in ('leg press', 'leg extension', 'leg curl', 'lat pulldown', 'machine')):
        return 'machine'
    if any(word in lowered for word in ('dumbbell', 'bicep curl', 'hammer curl', 'lateral raise', 'rear delt fly', 'arnold')):
        return 'dumbbell'
    if any(word in lowered for word in ('bench press', 'squat', 'deadlift', 'barbell', 'overhead press')):
        return 'barbell'
    return 'other'


class Command(BaseCommand):
    help = 'Populate the built-in exercise library.'

    def handle(self, *args, **options):
        created = 0
        for category, names in EXERCISES.items():
            for name in names.split(','):
                bodyweight = name in BODYWEIGHT
                body_part = {'Chest': 'Chest', 'Back': 'Back', 'Legs': 'Legs', 'Shoulders': 'Shoulders', 'Arms': 'Biceps', 'Core': 'Core', 'Calisthenics': 'Calisthenics', 'Cardio': 'Cardio', 'Full Body': 'Full Body', 'Beginner': 'Full Body'}[category]
                image = PHOTO_OVERRIDES.get(name, f'/static/workout/images/exercise-photo-grid.png#exercise-{category.lower()}-{name.lower().replace(" ", "-")}')
                exercise, was_created = Exercise.objects.update_or_create(name=name, defaults={
                    'category': category, 'description': f'{name} is a straightforward {category.lower()} exercise you can fit into today’s workout.',
                    'instructions': 'Move slowly with control, keep a comfortable range of motion, and stop if you feel sharp pain.',
                    'muscles_targeted': category, 'beginner_tips': 'Start light, focus on smooth technique, and take the rest you need.',
                    'body_part': body_part, 'is_bodyweight': bodyweight,
                    'equipment_type': equipment_for(name, bodyweight), 'image': image,
                })
                created += was_created
        images = list(Exercise.objects.values_list('image', flat=True))
        if len(images) != len(set(images)):
            raise RuntimeError('Duplicate exercise image references found; seed data was not accepted.')
        self.stdout.write(self.style.SUCCESS(f'Exercise library ready: {Exercise.objects.count()} exercises ({created} new, {len(images)} unique image references).'))
