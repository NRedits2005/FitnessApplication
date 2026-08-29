# FITNESS+

![Django](https://img.shields.io/badge/Django-5.2.17-0b7d53?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-183153?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local_DB-2563eb?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

FITNESS+ is a Django fitness web app for building personalized workout sessions, browsing gender-aware exercise libraries, tracking progress, and managing a fitness profile with biometric data, goals, equipment, and profile photos.

The app focuses on a practical training flow: set up a profile, get compatible recommendations, start a workout, complete sets, and watch your progress build over time.

## Highlights

- Personalized dashboard with streaks, BMI, weight, total lifted weight, and daily workout recommendations.
- Male and female exercise experiences with profile-compatible exercise filtering.
- Alphabetical Exercise Library with search, category/body-part filters, detail pages, and generated fallback visuals.
- Start Workout flow with searchable custom dropdown, exercise preview, sets, reps, weight, duration, and rest timing.
- Workout session tracking with completed sets and per-set persistence.
- Progress analytics based only on completed workouts and completed sets.
- Diet page with goal-based meal suggestions and generated food visuals.
- Profile setup and edit flow with photo upload/removal, BMI feedback, home equipment selection, and validation.

## Preview

The interface includes:

- Dashboard: personalized stats and today's workout card.
- Exercise Library: searchable cards with exercise images and filters.
- Start Workout: custom exercise dropdown with live movement guidance.
- Progress: training history and workout analytics.
- Profile: biometric details, goals, equipment, and profile image controls.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 5.2.17 |
| Language | Python 3.11 |
| Database | SQLite |
| Images | Pillow |
| Frontend | Django templates, CSS, vanilla JavaScript |
| Auth | Django authentication |

## Project Structure

```text
fitness2/
|-- config/                     # Active Django project settings and URLs
|-- workout/                    # Main application
|   |-- management/commands/    # Seed and cleanup commands
|   |-- migrations/             # Database migrations
|   |-- static/workout/         # CSS, JavaScript, and image assets
|   |-- templates/workout/      # Django templates
|   |-- analytics.py            # Progress chart and insight helpers
|   |-- forms.py                # Profile and workout forms
|   |-- image_utils.py          # Exercise image matching/fallback generation
|   |-- diet_image_utils.py     # Diet image matching/fallback generation
|   |-- models.py               # Exercise, profile, workout, diet models
|   |-- recommendations.py      # Exercise filtering and recommendation logic
|   |-- tests.py                # App test suite
|   |-- urls.py                 # App routes
|   `-- views.py                # Request handlers
|-- media/                      # Uploaded profile photos
|-- db.sqlite3                  # Local development database
`-- manage.py                   # Django command entrypoint
```

## Getting Started

### 1. Clone or open the project

```bash
cd "D:\Cognizant Project\fitness2"
```

### 2. Create a virtual environment

```bash
py -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
py -m pip install django pillow
```

### 4. Apply migrations

```bash
py manage.py migrate
```

### 5. Seed app data

```bash
py manage.py seed_exercises
py manage.py seed_womens_exercises
py manage.py seed_diet_meals
```

### 6. Run the development server

```bash
py manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Useful Commands

| Task | Command |
| --- | --- |
| Run server | `py manage.py runserver` |
| Create migrations | `py manage.py makemigrations` |
| Apply migrations | `py manage.py migrate` |
| Run tests | `py manage.py test` |
| Django system check | `py manage.py check` |
| Create admin user | `py manage.py createsuperuser` |
| Seed base exercises | `py manage.py seed_exercises` |
| Seed women's exercises | `py manage.py seed_womens_exercises` |
| Seed diet meals | `py manage.py seed_diet_meals` |
| Clean exercise data | `py manage.py cleanup_exercises` |

## Core Features

### Profile Personalization

Users configure their name, age, gender, height, weight, primary goal, preferred workout location, experience level, home equipment, and profile photo. The app uses this profile to decide which exercises should appear and what recommendations are most relevant.

### Exercise Library

The library shows only exercises compatible with the user's profile. Male/default users browse by body part, while female users get a dedicated Women's Fitness experience with category-based browsing. Search works across name, body part, muscle targets, category, equipment, and description.

### Workout Builder

The Start Workout page uses a searchable dropdown that stays aligned with the Exercise Library. After selecting an exercise, users can configure sets, reps, weight, exercise duration, and rest duration before starting the session.

### Progress Tracking

Completed workouts and completed sets drive the progress analytics. Planned but unfinished workout values are not counted toward total lifted volume, keeping the statistics honest.

### Image Handling

Exercise and diet cards use existing static assets when available. If an image is missing, the app can generate a clean fallback visual through Pillow so the interface remains complete.

## Routes

| Page | URL |
| --- | --- |
| Dashboard | `/` |
| Login | `/login/` |
| Register | `/register/` |
| Profile | `/profile/` |
| Edit Profile | `/profile/edit/` |
| Diet | `/diet/` |
| Start Workout | `/start/` |
| History | `/history/` |
| Progress | `/progress/` |
| Exercise Library | `/exercise-library/` |

## Testing

Run the full suite:

```bash
py manage.py test
```

The tests cover profile-aware exercise filtering, male/female library behavior, workout dropdown consistency, progress analytics, dashboard totals, set completion persistence, and recommendation counts.

## Notes

- This project is configured for local development with SQLite and `DEBUG = True`.
- Uploaded profile photos are stored in `media/profile_images/`.
- Static exercise assets live under `workout/static/workout/images/`.
- For production deployment, move secrets into environment variables and update `ALLOWED_HOSTS`, `DEBUG`, static files, media handling, and database settings.

## License

This project is currently private/internal. Add a license file before publishing or distributing it.
