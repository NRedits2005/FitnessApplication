from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from .models import Exercise, UserProfile

# Maximum profile image size: 5 MB
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


class StartWorkoutForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.none(), empty_label='Select an exercise')
    sets = forms.IntegerField(min_value=1, max_value=50, initial=3)
    repetitions = forms.IntegerField(min_value=1, max_value=500, initial=10)
    weight = forms.DecimalField(min_value=0, max_digits=7, decimal_places=2, required=False, initial=0, label='Equipment / Weight')
    exercise_minutes = forms.IntegerField(min_value=0, max_value=59, initial=0, label='Exercise minutes')
    exercise_seconds = forms.IntegerField(min_value=0, max_value=59, initial=30, label='Exercise seconds')
    rest_minutes = forms.IntegerField(min_value=0, max_value=59, initial=1, label='Rest minutes')
    rest_seconds = forms.IntegerField(min_value=0, max_value=59, initial=0, label='Rest seconds')

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if profile is None:
            self.fields['exercise'].queryset = Exercise.objects.order_by(Lower('name'), 'name', 'pk')
        else:
            from .recommendations import get_available_exercises
            self.fields['exercise'].queryset = get_available_exercises(profile).order_by(Lower('name'), 'name', 'pk')

    def clean(self):
        cleaned = super().clean()
        exercise = cleaned.get('exercise')
        weight = cleaned.get('weight')
        if exercise and not exercise.is_bodyweight and weight is None:
            self.add_error('weight', 'Please enter a weight, or use 0 kg if you are not adding weight today.')
        if cleaned.get('exercise_minutes', 0) * 60 + cleaned.get('exercise_seconds', 0) < 1:
            self.add_error('exercise_seconds', 'Exercise time must be at least 1 second.')
        if cleaned.get('rest_minutes', 0) * 60 + cleaned.get('rest_seconds', 0) < 1:
            self.add_error('rest_seconds', 'Rest time must be at least 1 second.')
        return cleaned


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    EQUIPMENT = [('bodyweight','No equipment'),('dumbbell','Dumbbells'),('band','Resistance bands'),('pullup_bar','Pull-up bar'),('kettlebell','Kettlebell'),('bench','Bench'),('mat','Yoga mat'),('jump_rope','Jump rope')]
    gender = forms.ChoiceField(
        choices=[('', 'Select gender'), ('male', 'Male'), ('female', 'Female')],
        required=True,
    )
    home_equipment = forms.MultipleChoiceField(choices=EQUIPMENT, required=False, widget=forms.CheckboxSelectMultiple)
    # Profile image upload field
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp', 'id': 'id_profile_image'}),
        label='Profile Image',
    )
    # Flag to remove the existing photo
    remove_photo = forms.BooleanField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = UserProfile
        fields = ('name', 'age', 'gender', 'height_cm', 'weight_kg', 'goal', 'workout_location', 'experience_level', 'home_equipment')
        widgets = {
            'age': forms.NumberInput(attrs={'min': 13, 'max': 100}),
            'height_cm': forms.NumberInput(attrs={'min': 100, 'max': 250}),
            'weight_kg': forms.NumberInput(attrs={'min': 25, 'max': 400}),
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image:
            return image

        # Check file size
        if image.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError(
                f'Your image is too large ({image.size // (1024*1024):.1f} MB). '
                'Please choose an image under 5 MB.'
            )

        # Check file extension
        import os
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                'Only JPG, PNG, and WEBP images are allowed. '
                f'You uploaded a "{ext or "unknown"}" file.'
            )

        # Verify the file is actually a valid image using Pillow
        try:
            from PIL import Image
            img = Image.open(image)
            img.verify()           # raises if corrupt
            image.seek(0)          # reset after verify
            # Re-open to check format after verify (verify() closes the fp)
            image.seek(0)
            img2 = Image.open(image)
            fmt = (img2.format or '').upper()
            if fmt not in ('JPEG', 'PNG', 'WEBP'):
                raise forms.ValidationError(
                    f'The uploaded file does not appear to be a valid image (detected format: {fmt or "unknown"}). '
                    'Please upload a JPG, PNG, or WEBP image.'
                )
            image.seek(0)
        except forms.ValidationError:
            raise
        except Exception:
            raise forms.ValidationError(
                'The uploaded file could not be read as an image. '
                'Please make sure it is a valid JPG, PNG, or WEBP file.'
            )

        return image

    def clean(self):
        data = super().clean()
        age, height, weight = data.get('age'), data.get('height_cm'), data.get('weight_kg')
        if age is None or not 13 <= age <= 100:
            self.add_error('age', 'Enter an age from 13 to 100.')
        if height is None or not 100 <= height <= 250:
            self.add_error('height_cm', 'Enter a height from 100 to 250 cm.')
        if weight is None or not 25 <= weight <= 400:
            self.add_error('weight_kg', 'Enter a weight from 25 to 400 kg.')
        return data
