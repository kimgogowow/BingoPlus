from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from bingo_plus.models import Profile
import re

SPECIAL_CHARACTERS = ['!', '#', '$', '%', '^', '&', '*', '(', ')', '+', '-', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '?', '/']
pattern = '[~!#$%^&*()+{}\\[\\]:;,<>/?-]'

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput())

    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if re.search(pattern, username):
            raise forms.ValidationError("Username can't contain any special characters")

        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput())
    confirm_password =forms.CharField(max_length = 200, widget=forms.PasswordInput())
    email = forms.CharField(max_length=50,widget = forms.EmailInput())
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)

    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm_password')

        username = cleaned_data.get('username')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if re.search(pattern, username):
            raise forms.ValidationError("Username can't contain any special characters")

        if re.search(pattern, first_name):
            raise forms.ValidationError("First name can't contain any special characters")

        if re.search(pattern, last_name):
            raise forms.ValidationError("Last name can't contain any special characters")



        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

