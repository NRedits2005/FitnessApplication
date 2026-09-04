from django.urls import path
from . import views

app_name = 'workout'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('diet/', views.diet, name='diet'),
    path('diet/meal/<int:meal_id>/fallback.svg', views.diet_meal_fallback, name='diet_meal_fallback'),
    path('', views.dashboard, name='dashboard'),
    path('start/', views.start_workout, name='start_workout'),
    path('session/<int:entry_id>/', views.workout_session, name='workout_session'),
    path('session/<int:entry_id>/complete-set/', views.complete_set, name='complete_set'),
    path('complete/<int:workout_id>/', views.workout_complete, name='workout_complete'),
    path('history/<int:workout_id>/delete/', views.delete_workout, name='delete_workout'),
    path('history/<int:workout_id>/', views.workout_history_detail, name='workout_history_detail'),
    path('history/', views.history, name='history'),
    path('progress/day/<str:date_str>/', views.workout_day_detail, name='workout_day_detail'),
    path('progress/', views.progress, name='progress'),
    path('exercise-library/', views.exercise_library, name='exercise_library'),
    path('exercise-library/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    path('exercise/<int:exercise_id>/visual.svg', views.exercise_visual, name='exercise_visual'),
]
