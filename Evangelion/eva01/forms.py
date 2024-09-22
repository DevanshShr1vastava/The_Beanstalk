from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Subject


class SignUpForm(UserCreationForm):
    username = forms.CharField(required=True,help_text='Required. Provide a valid username.')
    email = forms.EmailField(required=True, help_text='Required. Provide a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['location', 'avatar']

class userSubjectSelectionForm(forms.ModelForm):
    selected_subjects = forms.ModelMultipleChoiceField(
        queryset = Subject.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = False
    )

    class Meta:
        model = UserProfile
        fields = ['selected_subjects']