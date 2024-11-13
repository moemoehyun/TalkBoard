from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from django.forms import ModelForm
from django import forms
from .models import Board, Comment, Favorite, Contact
from django.contrib.auth import get_user_model

# class BoardForm(forms.ModelForm):
#     class Meta:
#         model = Board
#         fields = ["title", "content"]

class BoardForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タイトル'})
    )
    content = forms.CharField(
    widget=forms.Textarea(attrs={
        'class': 'form-control', 
        'placeholder': '内容',
        'rows': 5  # 行数を増やしたい数に設定
    })
)
    class Meta:
        model = Board
        fields = ['title', 'content', 'image', "video"] #"video"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text="emailアドレスは必須項目です。",
        error_messages={'invalid': "メールアドレスを入力してください"},
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'メールアドレス'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード（確認用）'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ["board"]

class ContactForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タイトル'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'メッセージ', 'rows': 4})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'メールアドレス'})
    )

    class Meta:
        model = Contact
        fields = ["title", "message", "email"]

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user