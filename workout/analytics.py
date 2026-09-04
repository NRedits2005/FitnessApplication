"""Queryset-backed analytics for the authenticated user's workout history."""

from collections import Counter, defaultdict
from decimal import Decimal
from datetime import date, timedelta

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


def get_muscle_group(exercise):
    """
    Map an exercise to one of the standard primary muscle groups:
    'Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Full Body', 'Cardio'
    """
    if not exercise:
        return 'Other'
    tag = (getattr(exercise, 'body_part_tag', '') or '').strip().lower()
    part = (getattr(exercise, 'body_part', '') or '').strip().lower()
    targeted = (getattr(exercise, 'muscles_targeted', '') or '').strip().lower()
    name = (getattr(exercise, 'name', '') or '').strip().lower()

    # 1. Primary body_part direct matching
    if any(k in part for k in ['chest', 'pec']):
        return 'Chest'
    if any(k in part for k in ['back', 'lats']):
        return 'Back'
    if any(k in part for k in ['leg', 'glute', 'quad', 'hamstring', 'calf', 'calves', 'thigh']):
        return 'Legs'
    if any(k in part for k in ['shoulder', 'delt']):
        return 'Shoulders'
    if any(k in part for k in ['arm', 'bicep', 'tricep', 'forearm']):
        return 'Arms'
    if any(k in part for k in ['core', 'abs', 'abdom', 'oblique', 'calisthenics']):
        return 'Core'

    # 2. Tag matching
    if any(k in tag for k in ['chest', 'pec']):
        return 'Chest'
    if any(k in tag for k in ['back', 'lats']):
        return 'Back'
    if any(k in tag for k in ['leg', 'glute', 'quad', 'hamstring', 'calf', 'calves', 'thigh', 'hip', 'inner thigh']):
        return 'Legs'
    if any(k in tag for k in ['shoulder', 'delt', 'hip flexor']):
        return 'Shoulders'
    if any(k in tag for k in ['arm', 'bicep', 'tricep', 'forearm']):
        return 'Arms'
    if any(k in tag for k in ['core', 'abs', 'abdom', 'oblique', 'lower abs']):
        return 'Core'

    # 3. Name keywords
    if any(k in name for k in ['bench press', 'push-up', 'push up', 'chest fly', 'pec fly', 'incline press', 'decline press']):
        return 'Chest'
    if any(k in name for k in ['row', 'pull-up', 'pull up', 'chin-up', 'pulldown', 'lat pulldown']):
        return 'Back'
    if any(k in name for k in ['squat', 'lunge', 'hip thrust', 'leg press', 'leg curl', 'leg extension', 'calf raise', 'step-up', 'butt kick']):
        return 'Legs'
    if any(k in name for k in ['overhead press', 'shoulder press', 'lateral raise', 'front raise', 'military press']):
        return 'Shoulders'
    if any(k in name for k in ['curl', 'bicep', 'tricep', 'kickback', 'skull crusher', 'tricep extension', 'dip']):
        return 'Arms'
    if any(k in name for k in ['plank', 'crunch', 'sit-up', 'dead bug', 'bird dog', 'russian twist', 'heel tap', 'leg raise']):
        return 'Core'

    # 4. Fallback to targeted
    if 'chest' in targeted or 'pec' in targeted:
        return 'Chest'
    if 'back' in targeted or 'lats' in targeted:
        return 'Back'
    if any(k in targeted for k in ['leg', 'glute', 'quad', 'hamstring', 'calf']):
        return 'Legs'
    if 'shoulder' in targeted or 'delt' in targeted:
        return 'Shoulders'
    if any(k in targeted for k in ['bicep', 'tricep', 'arm']):
        return 'Arms'
    if any(k in targeted for k in ['core', 'abs', 'abdom', 'oblique']):
        return 'Core'

    # Specific names or fallbacks
    if 'cardio' in part or 'cardio' in tag or 'jump' in name or 'run' in name or 'jog' in name or 'cycling' in name:
        return 'Cardio'
    if 'full body' in part or 'full body' in tag:
        return 'Full Body'
    return 'Other'


def get_workout_focus(workout):
    """Determine a human-friendly primary focus label for a workout."""
    entries = list(workout.workout_exercises.all())
    if not entries:
        return 'General Workout'
    groups = Counter()
    for entry in entries:
        groups[get_muscle_group(entry.exercise)] += 1
    if len(groups) == 1:
        return list(groups.keys())[0]
    # If 3 or more distinct muscle groups or contains Full Body
    if 'Full Body' in groups or len(groups) >= 3:
        return 'Full Body'
    # Return top 2 muscle groups combined
    top = [g for g, _ in groups.most_common(2)]
    return ' & '.join(top)


def build_progress_data(workouts, today=None, range_key='30d', start_date=None):
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
            'volume_raw': float(volume),
            'duration': duration_label(duration),
            'duration_seconds': duration,
        })

    # Smart chart time-series aggregation preventing overlapping labels for long ranges
    frequency_series, volume_series = build_time_series_buckets(
        workouts=workouts,
        range_key=range_key,
        start_date=start_date,
        today=today,
        frequency_counts=frequency,
        volume_by_date=volume_by_date
    )

    total_volume_dec = sum(volume_by_date.values(), Decimal('0'))

    return {
        'summary': {
            'workouts': len(workouts),
            'workouts_raw': len(workouts),
            'sets': total_sets,
            'sets_raw': total_sets,
            'reps': total_reps,
            'reps_raw': total_reps,
            'volume': format_weight_display(total_volume_dec),
            'volume_raw': float(total_volume_dec),
            'duration': duration_label(total_seconds),
            'duration_seconds': total_seconds,
        },
        'frequency': frequency_series,
        'volume': volume_series,
        'activity': dict(activity),
        'history': history,
        'weekday_counts': Counter(workout.date.weekday() for workout in workouts),
    }


def build_time_series_buckets(workouts, range_key, start_date, today, frequency_counts, volume_by_date):
    """
    Generate appropriately aggregated time series (daily, weekly, or monthly)
    based on the selected time range so charts remain readable and never overlap.
    Preserves zero-activity intervals.
    """
    freq_series = []
    vol_series = []

    if range_key == 'today':
        iso_str = today.isoformat()
        freq_series.append({'date': iso_str, 'label': 'Today', 'value': frequency_counts.get(iso_str, 0)})
        vol_series.append({'date': iso_str, 'label': 'Today', 'value': float(round(volume_by_date.get(iso_str, Decimal('0')), 2))})
        return freq_series, vol_series

    if range_key in ['7d', '30d']:
        days = 7 if range_key == '7d' else 30
        range_start = today - timedelta(days=days - 1)
        for i in range(days):
            cur_date = range_start + timedelta(days=i)
            iso_str = cur_date.isoformat()
            label = cur_date.strftime('%b %d')
            freq_series.append({
                'date': iso_str,
                'label': label,
                'value': frequency_counts.get(iso_str, 0)
            })
            vol_series.append({
                'date': iso_str,
                'label': label,
                'value': float(round(volume_by_date.get(iso_str, Decimal('0')), 2))
            })
        return freq_series, vol_series

    if range_key == '3m':
        # 13 weekly buckets across 91 days
        range_start = today - timedelta(days=90)
        for w in range(13):
            w_start = range_start + timedelta(days=w * 7)
            w_end = min(today, w_start + timedelta(days=6))
            w_freq = sum(frequency_counts.get((w_start + timedelta(days=d)).isoformat(), 0) for d in range((w_end - w_start).days + 1))
            w_vol = sum(volume_by_date.get((w_start + timedelta(days=d)).isoformat(), Decimal('0')) for d in range((w_end - w_start).days + 1))
            label = w_start.strftime('%b %d')
            iso_str = w_start.isoformat()
            freq_series.append({'date': iso_str, 'label': label, 'value': w_freq})
            vol_series.append({'date': iso_str, 'label': label, 'value': float(round(w_vol, 2))})
        return freq_series, vol_series

    if range_key in ['6m', '1y']:
        months_count = 6 if range_key == '6m' else 12
        for m_offset in reversed(range(months_count)):
            # Calculate target year and month
            year = today.year
            month = today.month - m_offset
            while month <= 0:
                month += 12
                year -= 1
            m_start = date(year, month, 1)
            # Find last day of month
            if month == 12:
                next_month_start = date(year + 1, 1, 1)
            else:
                next_month_start = date(year, month + 1, 1)
            m_end = next_month_start - timedelta(days=1)
            if m_end > today:
                m_end = today

            m_freq = 0
            m_vol = Decimal('0')
            cur = m_start
            while cur <= m_end:
                iso = cur.isoformat()
                m_freq += frequency_counts.get(iso, 0)
                m_vol += volume_by_date.get(iso, Decimal('0'))
                cur += timedelta(days=1)

            label = m_start.strftime('%b')
            iso_str = m_start.isoformat()
            freq_series.append({'date': iso_str, 'label': label, 'value': m_freq})
            vol_series.append({'date': iso_str, 'label': label, 'value': float(round(m_vol, 2))})
        return freq_series, vol_series

    # All Time Range
    if not start_date:
        if workouts:
            earliest = min(getattr(w, 'analytics_date', w.date) for w in workouts)
            start_date = earliest
        else:
            start_date = today - timedelta(days=29)

    total_days = (today - start_date).days + 1
    if total_days <= 35:
        # Daily
        for i in range(total_days):
            cur = start_date + timedelta(days=i)
            iso = cur.isoformat()
            label = cur.strftime('%b %d')
            freq_series.append({'date': iso, 'label': label, 'value': frequency_counts.get(iso, 0)})
            vol_series.append({'date': iso, 'label': label, 'value': float(round(volume_by_date.get(iso, Decimal('0')), 2))})
    elif total_days <= 180:
        # Weekly
        num_weeks = (total_days + 6) // 7
        for w in range(num_weeks):
            w_start = start_date + timedelta(days=w * 7)
            w_end = min(today, w_start + timedelta(days=6))
            w_freq = sum(frequency_counts.get((w_start + timedelta(days=d)).isoformat(), 0) for d in range((w_end - w_start).days + 1))
            w_vol = sum(volume_by_date.get((w_start + timedelta(days=d)).isoformat(), Decimal('0')) for d in range((w_end - w_start).days + 1))
            label = w_start.strftime('%b %d')
            iso = w_start.isoformat()
            freq_series.append({'date': iso, 'label': label, 'value': w_freq})
            vol_series.append({'date': iso, 'label': label, 'value': float(round(w_vol, 2))})
    else:
        # Monthly
        cur_year = start_date.year
        cur_month = start_date.month
        while True:
            m_start = date(cur_year, cur_month, 1)
            if m_start > today:
                break
            if cur_month == 12:
                next_m = date(cur_year + 1, 1, 1)
            else:
                next_m = date(cur_year, cur_month + 1, 1)
            m_end = min(today, next_m - timedelta(days=1))

            m_freq = 0
            m_vol = Decimal('0')
            cur = m_start
            while cur <= m_end:
                iso = cur.isoformat()
                m_freq += frequency_counts.get(iso, 0)
                m_vol += volume_by_date.get(iso, Decimal('0'))
                cur += timedelta(days=1)

            label = m_start.strftime("%b '%y") if (today.year != start_date.year) else m_start.strftime('%b')
            iso = m_start.isoformat()
            freq_series.append({'date': iso, 'label': label, 'value': m_freq})
            vol_series.append({'date': iso, 'label': label, 'value': float(round(m_vol, 2))})

            if cur_month == 12:
                cur_year += 1
                cur_month = 1
            else:
                cur_month += 1

    return freq_series, vol_series


def build_chart_buckets(workouts, range_key, start_date, today, volume_by_date, frequency_by_date):
    """
    Build multi-point continuous time-series buckets (weekly / daily / monthly)
    so charts show meaningful trends across the entire selected range.
    """
    freq_points = []
    vol_points = []

    if range_key == 'today':
        # Single day point
        key = today.isoformat()
        freq_points.append({'label': 'Today', 'date': key, 'value': frequency_by_date.get(key, 0)})
        vol_points.append({'label': 'Today', 'date': key, 'value': float(round(volume_by_date.get(key, Decimal('0')), 2))})

    elif range_key == '7d':
        # 7 daily buckets (e.g. Mon .. Sun)
        for d in range(7):
            cur_date = today - timedelta(days=6 - d)
            key = cur_date.isoformat()
            label = cur_date.strftime('%a')  # Mon, Tue, ...
            sublabel = cur_date.strftime('%b %d')
            freq_points.append({'label': label, 'sublabel': sublabel, 'date': key, 'value': frequency_by_date.get(key, 0)})
            vol_points.append({'label': label, 'sublabel': sublabel, 'date': key, 'value': float(round(volume_by_date.get(key, Decimal('0')), 2))})

    elif range_key in ['30d', '3m', '6m']:
        # Group by 7-day weeks spanning from start_date to today
        if not start_date:
            days = RANGES[range_key][1]
            start_date = today - timedelta(days=days - 1)

        # Slice the date range into ~weekly intervals
        total_days = (today - start_date).days + 1
        num_weeks = max(4, (total_days + 6) // 7)
        chunk_days = 7

        for w in range(num_weeks):
            w_start = start_date + timedelta(days=w * chunk_days)
            w_end = min(today, w_start + timedelta(days=chunk_days - 1))
            if w_start > today:
                break

            # Sum frequency and volume in this window
            w_freq = 0
            w_vol = Decimal('0')
            cur = w_start
            while cur <= w_end:
                k = cur.isoformat()
                w_freq += frequency_by_date.get(k, 0)
                w_vol += volume_by_date.get(k, Decimal('0'))
                cur += timedelta(days=1)

            if num_weeks <= 6:
                label = f"W{w+1}"
                sublabel = f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}"
            else:
                label = w_start.strftime('%b %d')
                sublabel = f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}"

            freq_points.append({
                'label': label,
                'sublabel': sublabel,
                'date': w_start.isoformat(),
                'value': w_freq
            })
            vol_points.append({
                'label': label,
                'sublabel': sublabel,
                'date': w_start.isoformat(),
                'value': float(round(w_vol, 2))
            })

    elif range_key in ['1y', 'all']:
        # Group by month (up to 12 months)
        if range_key == '1y' or not workouts:
            months_back = 12
        else:
            earliest = min(getattr(w, 'analytics_date', w.date) for w in workouts)
            months_back = max(6, min(24, ((today.year - earliest.year) * 12 + today.month - earliest.month + 1)))

        # Build monthly start/end dates
        month_anchors = []
        cur_year = today.year
        cur_month = today.month
        for _ in range(months_back):
            month_anchors.append((cur_year, cur_month))
            cur_month -= 1
            if cur_month < 1:
                cur_month = 12
                cur_year -= 1
        month_anchors.reverse()

        for y, m in month_anchors:
            m_start = date(y, m, 1)
            # End of month
            if m == 12:
                next_m = date(y + 1, 1, 1)
            else:
                next_m = date(y, m + 1, 1)
            m_end = min(today, next_m - timedelta(days=1))

            m_freq = 0
            m_vol = Decimal('0')
            cur = m_start
            while cur <= m_end:
                k = cur.isoformat()
                m_freq += frequency_by_date.get(k, 0)
                m_vol += volume_by_date.get(k, Decimal('0'))
                cur += timedelta(days=1)

            label = m_start.strftime('%b')
            sublabel = m_start.strftime('%b %Y')
            freq_points.append({
                'label': label,
                'sublabel': sublabel,
                'date': m_start.isoformat(),
                'value': m_freq
            })
            vol_points.append({
                'label': label,
                'sublabel': sublabel,
                'date': m_start.isoformat(),
                'value': float(round(m_vol, 2))
            })

    return {'frequency': freq_points, 'volume': vol_points}


def calculate_period_comparisons(current_summary, prev_workouts, range_key, range_days):
    """
    Calculate reliable period-over-period comparison metrics for KPI cards.
    Returns comparison data only if a valid prior period can be compared.
    """
    if not range_days or range_key == 'all':
        return {'has_comparison': False}

    prev_workouts = list(prev_workouts)
    prev_count = len(prev_workouts)
    prev_sets = 0
    prev_reps = 0
    prev_seconds = 0
    prev_vol_dec = Decimal('0')

    for w in prev_workouts:
        entries = list(w.workout_exercises.all())
        completed_sets = [s for e in entries for s in e.sets.all() if s.completed]
        prev_sets += len(completed_sets)
        prev_reps += sum(s.reps_completed for s in completed_sets)
        prev_seconds += (w.duration_seconds or 0)
        prev_vol_dec += calculate_workout_volume(w)

    curr_count = current_summary.get('workouts_raw', current_summary.get('workouts', 0))
    curr_vol = Decimal(str(current_summary.get('volume_raw', 0)))
    curr_seconds = current_summary.get('duration_seconds', 0)
    curr_sets = current_summary.get('sets_raw', current_summary.get('sets', 0))
    curr_reps = current_summary.get('reps_raw', current_summary.get('reps', 0))

    workouts_diff = curr_count - prev_count
    volume_diff = curr_vol - prev_vol_dec
    duration_diff = curr_seconds - prev_seconds
    sets_diff = curr_sets - prev_sets
    reps_diff = curr_reps - prev_reps

    period_name = 'prev period' if range_days > 1 else 'yesterday'

    def format_diff(val, unit='', is_weight=False):
        if val > 0:
            formatted = format_weight_display(val) if is_weight else f"{val:,}"
            return f"+{formatted}{unit} vs {period_name}", 'positive'
        elif val < 0:
            abs_val = abs(val)
            formatted = format_weight_display(abs_val) if is_weight else f"{abs_val:,}"
            return f"-{formatted}{unit} vs {period_name}", 'negative'
        else:
            return f"Same as {period_name}", 'neutral'

    w_text, w_type = format_diff(workouts_diff)
    v_text, v_type = format_diff(volume_diff, ' kg', is_weight=True)
    s_text, s_type = format_diff(sets_diff)
    r_text, r_type = format_diff(reps_diff)

    # Duration diff text
    if duration_diff > 60:
        d_mins = duration_diff // 60
        d_text = f"+{duration_label(duration_diff)} vs {period_name}"
        d_type = 'positive'
    elif duration_diff < -60:
        d_mins = abs(duration_diff) // 60
        d_text = f"-{duration_label(abs(duration_diff))} vs {period_name}"
        d_type = 'negative'
    else:
        d_text = f"Same as {period_name}"
        d_type = 'neutral'

    return {
        'has_comparison': True,
        'workouts': {'text': w_text, 'type': w_type, 'diff': workouts_diff},
        'volume': {'text': v_text, 'type': v_type, 'diff': float(volume_diff)},
        'duration': {'text': d_text, 'type': d_type, 'diff': duration_diff},
        'sets': {'text': s_text, 'type': s_type, 'diff': sets_diff},
        'reps': {'text': r_text, 'type': r_type, 'diff': reps_diff},
    }


def build_heatmap_day_details(heatmap_workouts, today=None):
    """
    Build rich day-by-day workout data mapping YYYY-MM-DD -> details dictionary
    to power real modal popups when clicking any cell in the 12-month heatmap.
    """
    today = today or timezone.localdate()
    days_map = defaultdict(list)

    for w in heatmap_workouts:
        w_date = getattr(w, 'analytics_date', w.date)
        days_map[w_date.isoformat()].append(w)

    details = {}
    for date_iso, w_list in days_map.items():
        total_exercises = 0
        total_sets = 0
        total_reps = 0
        total_volume = Decimal('0')
        total_seconds = 0
        workout_items = []

        for w in w_list:
            entries = list(w.workout_exercises.all())
            completed_sets = [s for e in entries for s in e.sets.all() if s.completed]
            w_volume = calculate_workout_volume(w)
            w_duration = w.duration_seconds or 0
            w_reps = sum(s.reps_completed for s in completed_sets)

            total_exercises += len(entries)
            total_sets += len(completed_sets)
            total_reps += w_reps
            total_volume += w_volume
            total_seconds += w_duration

            # Format workout time
            time_str = ''
            if w.completed_at:
                local_time = timezone.localtime(w.completed_at)
                time_str = local_time.strftime('%I:%M %p').lstrip('0')
            elif w.created_at:
                local_time = timezone.localtime(w.created_at)
                time_str = local_time.strftime('%I:%M %p').lstrip('0')

            focus = get_workout_focus(w)

            workout_items.append({
                'id': w.id,
                'name': f"Workout #{w.id}",
                'time': time_str,
                'focus': focus,
                'duration': duration_label(w_duration),
                'duration_seconds': w_duration,
                'exercise_count': len(entries),
                'sets': len(completed_sets),
                'reps': w_reps,
                'volume': format_weight_display(w_volume),
                'detail_url': f"/history/{w.id}/",
            })

        date_obj = date.fromisoformat(date_iso)
        date_formatted = date_obj.strftime('%b %d, %Y')

        details[date_iso] = {
            'date': date_iso,
            'date_formatted': date_formatted,
            'workout_count': len(w_list),
            'total_duration': duration_label(total_seconds),
            'total_exercises': total_exercises,
            'total_sets': total_sets,
            'total_reps': total_reps,
            'total_volume': format_weight_display(total_volume),
            'workouts': workout_items,
            'primary_detail_url': f"/progress/day/{date_iso}/",
        }

    return details


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

