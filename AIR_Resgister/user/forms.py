from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput({
        'class':'form-control',
        'placeholder':'请输入用户名'
    }))
    password = forms.CharField(widget=forms.TextInput({
        'class':'form-control',
        'placeholder':'请输入密码'
    }))
    initial_tag_0 = forms.CharField(widget=forms.TextInput({
        'class':'form-control',
        'placeholder':'请输入您感兴趣的领域，用逗号隔开'
    }))

    class Meta:
        model = User
        fields =  ('username','password','initial_tag_0')