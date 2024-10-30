from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from django.forms import ModelForm
from django import forms
from .models import Board, Comment, Favorite, Contact

# class BoardForm(forms.ModelForm):
#     class Meta:
#         model = Board
#         fields = ["title", "content"]

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'content', 'image', "video"] #"video"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length= 254, help_text = "emailアドレスは必須項目です。")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ["board"]

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ["title", "message", "email"]