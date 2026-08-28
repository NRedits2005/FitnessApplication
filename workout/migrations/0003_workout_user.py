from django.conf import settings
from django.db import migrations, models


def assign_existing_workouts(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Workout = apps.get_model('workout', 'Workout')
    owner, _ = User.objects.get_or_create(username='legacy-owner', defaults={'email': 'legacy@example.invalid'})
    Workout.objects.filter(user__isnull=True).update(user=owner)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workout', '0002_alter_exercise_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, related_name='workouts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(assign_existing_workouts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='workouts', to=settings.AUTH_USER_MODEL),
        ),
    ]
