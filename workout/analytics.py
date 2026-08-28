"""Queryset-backed analytics for the authenticated user's workout history."""

from collections import Counter, defaultdict
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

from .models import calculate_workout_volume, format_weight_display


RANGES = {
    'today': ('Today', 1),
    '7d': ('Last 7 Days', 7),
    '30d': ('Last 30 Days', 30),
    '3m': ('Last 3 Months', 90),
    '6m': ('Last 6 Months', 182),
    '1y': ('Last Year', 365),
    'all': ('All Time', None),
}


def get_range(key, today=None):
    """Return a validated range key and its inclusive start date."""
    today = today or timezone.localdate()
    key = key if key in RANGES else '30d'
    days = RANGES[key][1]
    if days is None:
        return key, None
    if key == 'today':
        # Single calendar day: start_date == today
        return key, today
    return key, today - timedelta(days=days - 1)


def duration_label(seconds):
    if not seconds:
        return '—'
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f'{hours}h {minutes}m'
    return f'{minutes}m' if minutes else '< 1m'


def build_progress_data(workouts, today=None):
    """Build presentation-ready analytics from prefetched completed workouts."""
    today = today or timezone.localdate()
    workouts = list(workouts)
    activity = Counter()
    frequency = Counter()
    volume_by_date = defaultdict(lambda: Decimal('0'))
    history = []
    total_sets = total_reps = total_seconds = 0

    for workout in workouts:
        entries = list(workout.workout_exercises.all())
        completed_sets = [workout_set for entry in entries for workout_set in entry.sets.all() if workout_set.completed]
        volume = calculate_workout_volume(workout)
        duration = workout.duration_seconds or 0
        workout_date = getattr(workout, 'analytics_date', workout.date)
        date_key = workout_date.isoformat()
        activity[date_key] += 1
        frequency[date_key] += 1
        volume_by_date[date_key] += volume
        total_sets += len(completed_sets)
        total_reps += sum(workout_set.reps_completed for workout_set in completed_sets)
        total_seconds += duration
        history.append({
            'workout': workout,
            'exercise_count': len(entries),
            'sets': len(completed_sets),
            'reps': sum(workout_set.reps_completed for workout_set in completed_sets),
            'volume': format_weight_display(volume),
            'duration': duration_label(duration),
        })

    labels = sorted(frequency)
    return {
        'summary': {
            'workouts': len(workouts), 'sets': total_sets, 'reps': total_reps,
            'volume': format_weight_display(sum(volume_by_date.values(), Decimal('0'))),
            'duration': duration_label(total_seconds),
        },
        'frequency': [{'date': date, 'value': frequency[date]} for date in labels],
        'volume': [{'date': date, 'value': float(round(volume_by_date[date], 2))} for date in labels],
        'activity': dict(activity),
        'history': history,
        'weekday_counts': Counter(workout.date.weekday() for workout in workouts),
    }


def progress_insights(data, profile, range_days, previous_workouts=0, today=None):
    """Generate only plain-language statements supported by recorded data."""
    today = today or timezone.localdate()
    summary = data['summary']
    insights = []
    if summary['workouts']:
        if range_days == 1:
            period = 'today'
        elif range_days:
            period = f'the last {range_days} days'
        else:
            period = 'all time'
        insights.append(f"You've completed {summary['workouts']} workout{'s' if summary['workouts'] != 1 else ''} in {period}.")
    if range_days and previous_workouts and summary['workouts'] > previous_workouts:
        insights.append('You trained more consistently than in the previous period.')
    if profile.current_streak:
        insights.append(f"Your current streak is {profile.current_streak} day{'s' if profile.current_streak != 1 else ''}.")
    if data['weekday_counts']:
        weekday = max(data['weekday_counts'], key=data['weekday_counts'].get)
        insights.append(f"You complete the most workouts on {['Mondays', 'Tuesdays', 'Wednesdays', 'Thursdays', 'Fridays', 'Saturdays', 'Sundays'][weekday]}.")
    if profile.last_workout_date:
        days_away = (today - profile.last_workout_date).days
        if days_away >= 5:
            insights.append(f"You haven't trained in {days_away} days. A short workout can help you get back on track.")
    return insights[:4]
