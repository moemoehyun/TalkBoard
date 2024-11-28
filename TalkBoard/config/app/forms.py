from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from django.forms import ModelForm
from django import forms
from .models import Board, Comment, Favorite, Contact
from django.contrib.auth import get_user_model
from .models import Profile

# class BoardForm(forms.ModelForm):
#     class Meta:
#         model = Board
#         fields = ["title", "content"]

class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        max_length=20,
        required=True,
        label="ユーザー名",
        help_text="20文字以内で入力してください",
    )

    class Meta:
        model = Profile
        fields = ['avatar']  # Profileモデルのフィールドを指定

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ユーザーオブジェクトを受け取る
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username  # ユーザー名の初期値を設定

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data['username']  # ユーザー名を更新
        if commit:
            user.save()
            profile.save()
        return profile

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

# User = get_user_model()

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