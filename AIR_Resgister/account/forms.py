from django import forms
from django.contrib.auth.models import User
import re


def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    # email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', max_length=50,widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    initial_tag_0 = forms.CharField(label='initial_tag_0', max_length=500,widget=forms.TextInput)
    initial_tag_1 = forms.CharField(label='initial_tag_0', max_length=500,widget=forms.TextInput)

    ## TODO: check for safety


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)