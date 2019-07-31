from djongo import models

# Create your models here.
from django import forms
from django.contrib.auth.models import User


class Interests(models.Model):
    domain = models.CharField('user domain',max_length=50) # store tags as json 
    weight = models.FloatField()
    class Meta:
        abstract = True
    def __str__(self):
        return self.domain.__str__()

class UserInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    # degree = models.CharField('user degree',max_length=50) # store tags as json 
    # interests = models.ArrayModelField(
    #     model_container=Interests,
    # )
    # interests = models.CharField('initial interets',max_length=500) # store tags as json array, which means in the database, it will be just a string that can be easily dumped into a json array [Django: List field in model? - Stack Overflow](https://stackoverflow.com/questions/22340258/django-list-field-in-model)
    
    # initial_tag_1 = models.CharField('initial subdomain tag',max_length=500)

    class Meta:
        verbose_name='User Profile'
    def __str__(self):
        return self.user.__str__()

class UserProfile(models.Model):
    uid = models.IntegerField(unique=True,primary_key = True)#unique=True,primary_key = True
    degree = models.CharField('user degree',max_length=50) # store tags as json 
    interests = models.ArrayModelField(
        model_container=Interests,
    )
    collections = models.ArrayModelField(
        model_container=models.IntegerField()
    )

    def __str__(self):
        return self.interests.__str__()

# class UserForm(forms.ModelForm):
#     username = forms.CharField(widget=forms.TextInput({
#         'class':'form-control',
#         'placeholder':'请输入用户名'
#     }))
#     password = forms.CharField(widget=forms.TextInput({
#         'class':'form-control',
#         'placeholder':'请输入密码'
#     }))
#     initial_tag_0 = forms.CharField(widget=forms.TextInput({
#         'class':'form-control',
#         'placeholder':'请输入您感兴趣的领域，用逗号隔开'
#     }))
    # initial_tag_1 = forms.CharField(widget=forms.TextInput({
    #     'class':'form-control',
    #     'placeholder':'请输入您感兴趣的子领域，用逗号隔开'
    # }))

    # class Meta:
    #     model = User
    #     fields =  ('username','password','initial_tag_0')