from django.shortcuts import render, redirect, get_object_or_404
from .forms import BoardForm, SignUpForm, CommentForm, FavoriteForm, ContactForm, RegistrationForm
from .forms import ProfileForm
from .models import Board, Comment, Favorite, Profile
from django.views.generic.edit import FormView
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic.detail import DetailView
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.db import models
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from dotenv import load_dotenv
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
import os
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.db.models import Value, BooleanField

# Create your views here.
for user in User.objects.all():
    Profile.objects.get_or_create(user=user)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('app:profile')  # 適切なリダイレクト先に変更
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

#ログアウト
def logout_view(request):
    logout(request)
    return redirect("app:index")

#サインアップページのビュー
# def signup(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("app:login")
#     else:
#         form = SignUpForm()
#     return render(request, "registration/signup.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # ユーザーを一時的に非アクティブにする
            user.save()

            # メール認証リンクを生成
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            
            # リストを使わず、文字列として生成する
            link = f"http://{domain}/activate/{uid}/{token}/"
            print(type(user.email))  # デバッグ用
            print(user.email)     # 実際の値を確認

            # linkは文字列なので、rsplitが正しく動作する
            send_mail(
                'ユーザー登録ありがとうございます',
                f'メール認証リンク: {link}',
                'from@example.com',
                [user.email],
            )
            # send_mail(
            #     'Test Subject',
            #     'This is a test email.',
            #     'from@example.com',
            #     ['test@example.com'],  # ハードコードされたメールアドレスを使用
            # )

            # リダイレクト先にユーザーIDを渡す
            return render(request, 'email_sent.html', {"user_id": user.id})
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})

#プロフィールページのビュー
@login_required
def profile(request):
    user = request.user
    return render(request, "accounts/profile.html", {"user": user})

def activate(request, uidb64, token):
    try:
        # uidb64をデコードしてユーザーのPKを取得
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # アカウントを有効化
        user.is_active = True
        user.save()
        login(request, user)  # ログインさせる
        return redirect('app:index')  # ログインページにリダイレクト
    else:
        return redirect('app:activation_failed')  # 失敗時のリダイレクト
# def activate(request, uidb64, token):
#     try:
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         user = get_user_model().objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         user.is_active = True
#         user.save()
#         login(request, user)
#         return redirect('app:login')
#     else:
#         return redirect('app:activation_failed')
    
def activation_failed(request):
    return render(request, 'activation_failed.html')
    
def email_sent(request, user_id):
    # ユーザーを取得し、テンプレートに渡す
    User = get_user_model()
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'email_sent.html', {'user': user})

def resend_email(request, user_id):
    # ユーザーを取得
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # ユーザーが存在しない場合のエラーハンドリング
        return redirect('app:activation_failed')
    
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    domain = get_current_site(request).domain

    link = f"http://{domain}/activate/{uid}/{token}/"
    
    send_mail(
        'ユーザー登録ありがとうございます',
        f'メール認証リンク: {link}',
        'from@example.com',
        [user.email],
    )
    return render(request, 'email_sent.html', {"user_id": user.id})

def user_owns_board(view_func):
    @wraps(view_func)
    def wrapper(request, pk):
        board = get_object_or_404(Board, pk=pk)
        if board.user == request.user:
            return view_func(request, pk)
        else:
            return redirect("app:index")
    return wrapper

def index(request):
    user = request.user

    if user.is_authenticated:
        # ログインしている場合、お気に入りのカウントを取得
        boards_query = Board.objects.annotate(
            is_favorite=Count("favorite", filter=models.Q(favorite__user=user)),
            comment_count=Count("comments")
        ).order_by("-updated_at")
    else:
        # ログインしていない場合、お気に入りのカウントはなし
        boards_query = Board.objects.annotate(
            is_favorite=Count("favorite", filter=models.Q(favorite__user=None)),
            comment_count=Count("comments")
        ).order_by("-updated_at")

    paginator = Paginator(boards_query, 10)
    page_number = request.GET.get("page")
    boards = paginator.get_page(page_number)

    return render(request, "index.html", {"boards": boards})
    # user = request.user
    # boards = Board.objects.annotate(is_favorite=Count("favorite", filter=models.Q(favorite__user=user))).order_by("-updated_at")
    # return render(request, "index.html", {"boards": boards})

@login_required
def my_boards(request):
    user = request.user
    boards = user.boards.all()
    return render(request, "my_boards.html", {"boards": boards})

@login_required
def comment_create(request, pk):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.instance.user = request.user
            comment_form.instance.board_id = pk
            comment_form.save()
    return redirect("app:show", pk=pk)

@login_required
def comment_delete(request, board_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
    return redirect("app:show,", pk=board_pk)

@login_required
def new(request):
    form = BoardForm()
    return render(request, "new.html", {"form": form})

@login_required
def create(request):
    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect("app:index")
    else:
        form = BoardForm()
    return render(request, "new.html", {"form": form})

@login_required
def show(request, pk):
    board = Board.objects.get(pk=pk)
    comments = Comment.objects.filter(board=pk).order_by("-created_at")
    comment_form = CommentForm()
    
    # 閲覧数を計算・保存
    board.views += 1  # 閲覧数を1増加
    board.save(update_fields=['views'])  # 閲覧数のみを保存

    return render(request, "show.html", {"board": board, "comments": comments, "comment_form": comment_form})

@login_required
@user_owns_board
def edit(request, pk):
    board = Board.objects.get(pk=pk)
    form = BoardForm(instance=board)
    return render(request, "edit.html", {"form" : form, "board" : board})

@login_required
@user_owns_board
def update(request, pk):
    board = Board.objects.get(pk=pk)
    if request.method == "POST":
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect("app:show", pk=pk)
    else:
        form = BoardForm(instance=board)
    return render(request, "edit.html", {"form" : form, "board" : board})

@login_required
@user_owns_board
def delete(request, pk):
    board = Board.objects.get(pk=pk)
    if request.method == "POST":
        board.delete()
        messages.success(request, "投稿を削除しました。")
        return redirect("app:index")
    return redirect("app:index")


def board_search(request):
    query = request.GET.get("query")
    search_type = request.GET.get("search_type")
    boards = Board.objects.all()
    if query:
        if search_type == "partial":
            boards = boards.filter(title__icontains=query)  # 部分一致
        elif search_type == "prefix":
            boards = boards.filter(title__startswith=query)  # 前方一致
        elif search_type == "suffix":
            boards = boards.filter(title__endswith=query)  # 後方一致
        else:
            boards = boards.filter(title__icontains=query)  # デフォルトで部分一致
    else:
        boards = Board.objects.none()

    return render(request, "index.html", {"boards": boards})

def board_sort(request):
    sort_by = request.GET.get('sort')
    direction = request.GET.get('direction')

    if direction == "asc":
        next_direction = "desc"
    else:
        next_direction = "asc"
    
    if sort_by:
        if direction == "desc":
            boards = Board.objects.all().order_by(f"-{sort_by}")
        else:
            boards = Board.objects.all().order_by(sort_by)
    else:
        boards = Board.objects.all()

    context = {
        "boards": boards,
        "sort_by": sort_by,
        "direction": direction,
        "next_direction": next_direction
    }

    return render(request, "index.html", context)

@login_required
def add_favorite(request):
    if request.method == "POST":
        board_id = request.POST.get("board")
        if not board_id:
            return HttpResponseBadRequest("Board ID is required.")

        # 投稿が存在するか確認
        board = get_object_or_404(Board, id=board_id)

        # 重複を防ぐため既存のレコードを確認
        Favorite.objects.get_or_create(user=request.user, board=board)

        # 元のページにリダイレクト
        return redirect(request.META.get('HTTP_REFERER', 'app:index'))
    return HttpResponseBadRequest("Invalid request method.")

@login_required
def remove_favorite(request):
    if request.method == "POST":
        board_id = request.POST.get("board")
        if not board_id:
            return HttpResponseBadRequest("Board ID is required.")

        # 投稿が存在するか確認
        board = get_object_or_404(Board, id=board_id)

        # お気に入りを削除
        Favorite.objects.filter(user=request.user, board=board).delete()

        # 元のページにリダイレクト
        return redirect(request.META.get('HTTP_REFERER', 'app:index'))
    return HttpResponseBadRequest("Invalid request method.")

@login_required
def favorite_boards(request):
    # ユーザーのお気に入り投稿を取得
    user = request.user

    # お気に入りの投稿を取得して is_favorite を設定
    favorites = Favorite.objects.filter(user=user).select_related("board")
    boards = Board.objects.filter(id__in=[favorite.board.id for favorite in favorites]).annotate(
        is_favorite=Value(True, output_field=BooleanField()),
        comment_count=Count("comments")
    ).order_by("-updated_at")

    # ページネーション
    paginator = Paginator(boards, 10)
    page_number = request.GET.get("page")
    boards = paginator.get_page(page_number)

    # コンテキストに渡す
    context = {
        'boards': boards,
    }

    return render(request, 'favorite_boards.html', context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            #ユーザーへのメール
            
            user_subject = "お問い合わせを受け付けました"
            user_message = "お問い合わせ内容：\n\n{}".format(contact.message)
            send_mail(user_subject, user_message, settings.EMAIL_HOST_USER, [os.getenv('EMAIL_HOST_USER')])
            #運営者へのメール
            User_email = contact.email 
            admin_subject = "お問い合わせがありました"
            admin_message = (f"{User_email}"+"\n\nお問い合わせ内容：\n\n{}").format(contact.message)
            send_mail(admin_subject, admin_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            return redirect("app:contact_success")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})

def contact_success(request):
    return render(request, "contact_success.html")
# ログインページのビュー

class CustomLoginView(LoginView):
    template_name = "registration/login.html"


def option(request):
    return render(request, "option.html")

def disclaimer(request):
    return render(request, "disclaimer.html")