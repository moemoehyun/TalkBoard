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
from django.db.models import Count, Q, Exists, OuterRef, Subquery
from PIL import Image
from io import BytesIO
from django.urls import reverse
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Repost

# Create your views here.
@login_required
def repost(request, board_id):
    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponse({"error": "Board not found"}, status=404)

    # リポストのトグル処理
    repost, created = Repost.objects.get_or_create(user=request.user, original_post=board)

    if not created:  # リポストを解除
        repost.delete()
        is_reposted = False
    else:  # 新たにリポスト
        is_reposted = True

    # リポスト数のカウント
    repost_count = Repost.objects.filter(original_post=board).count()

    return JsonResponse({
        "repost_count": repost_count,
        "is_reposted": is_reposted,
    })

for user in User.objects.all():
    Profile.objects.get_or_create(user=user)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@login_required
def edit_profile(request):
    profile = request.user.profile  # ログイン中のユーザーのプロフィールを取得
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "プロフィールが更新されました！")
            return redirect('app:edit_profile')  # 編集画面に留まる
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# @login_required
# def edit_profile(request):
#     profile = request.user.profile  # ログイン中のユーザーのプロフィールを取得
#     if request.method == "POST":
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('app:profile', user_id=request.user.id)
#     else:
#         form = ProfileForm(instance=profile)
#     return render(request, 'accounts/edit_profile.html', {'form': form})

#ログアウト
def logout_view(request):
    logout(request)
    return redirect("app:index")

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

@login_required
def profile(request, user_id=None):
    user = request.user

    # 特定のユーザー情報を取得
    if user_id is None:
        profile_user = user  # 自分のプロフィール情報
    else:
        profile_user = get_object_or_404(User, id=user_id)  # 他ユーザーのプロフィール情報

    # 自分または指定したユーザーの投稿に、お気に入りの有無とコメント数を含めて取得
    boards = (
        Board.objects.filter(user=profile_user)
        .annotate(
            is_favorite=Count("favorite", filter=Q(favorite__user=user)),  # 現在のユーザーのお気に入り状態
            comment_count=Count("comments"),
        )
        .order_by("-updated_at")
    )

    return render(request, "accounts/profile.html", {
        "profile_user": profile_user,
        "logged_in_user": request.user,
        "boards": boards
    })

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

# def serve_cropped_image(request, board_id):
#     # Boardモデルを取得
#     board = get_object_or_404(Board, id=board_id)

#     if board.image:
#         try:
#             # S3上の画像URLを取得
#             image_url = board.image.url  # MEDIA_URL + ファイル名で構築されるURL

#             # S3から画像を取得
#             response = requests.get(image_url)
#             response.raise_for_status()

#             # 画像を開いてトリミング処理
#             print(f"Fetching image from: {image_url}")
#             print(f"Response status: {response.status_code}, Content: {response.content[:100]}")

#             img = Image.open(BytesIO(response.content))
#             width, height = img.size
#             min_dimension = min(width, height)
#             left = (width - min_dimension) / 2
#             top = (height - min_dimension) / 2
#             right = (width + min_dimension) / 2
#             bottom = (height + min_dimension) / 2
#             cropped_img = img.crop((left, top, right, bottom))

#             # 出力用のバッファを準備
#             buffer = BytesIO()
#             cropped_img.save(buffer, format="PNG")  # JPEG形式で保存
#             buffer.seek(0)

#             # HTTPレスポンスとして画像を返す
#             return HttpResponse(buffer, content_type="image/jpeg")
#         except requests.exceptions.RequestException as e:
#             # S3からの取得エラーをログに記録
#             print(f"Error fetching image from S3 for board {board_id}: {e}")
#             return HttpResponse(status=500)
#         except Exception as e:
#             # トリミングエラーをログに記録
#             print(f"Error processing image for board {board_id}: {e}")
#             return HttpResponse(status=500)

#     return HttpResponse(status=404)

@login_required
def toggle_favorite(request, board_id):
    if request.method == "POST":
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return JsonResponse({"error": "Board not found"}, status=404)

        # Favorite のトグル処理
        favorite, created = Favorite.objects.get_or_create(user=request.user, board=board)
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True

        # いいね数を取得
        favorite_count = board.favorite_set.count()

        return JsonResponse({"is_favorite": is_favorite, "favorite_count": favorite_count})

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def index(request):
    user = request.user

    boards_query = Board.objects.annotate(
        is_favorite=Count("favorite", filter=Q(favorite__user=user)),
        comment_count=Count("comments"),
        repost_count=Count("reposts"),
        is_reposted=Exists(
            Repost.objects.filter(user=user, original_post=OuterRef("id"))
        ),
        reposted_by=Subquery(
            Repost.objects.filter(original_post=OuterRef("id"))
            .order_by("-created_at")  # 最新のリポストユーザーを取得
            .values("user__username")[:1]
        ),
    ).order_by("-is_reposted", "-updated_at")  # リポストを優先表示

    paginator = Paginator(boards_query, 10)
    page_number = request.GET.get("page")
    boards = paginator.get_page(page_number)

    return render(request, "index.html", {"boards": boards})

@login_required
def my_boards(request):
    user = request.user

    # 自分の投稿に、お気に入りの有無とコメント数を含めて取得
    boards = (
        user.boards.annotate(
            is_favorite=Count("favorite", filter=Q(favorite__user=user)),
            comment_count=Count("comments"),
        )
        .order_by("-updated_at")
    )

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
    # リポスト済みかを判定
    is_reposted = Repost.objects.filter(user=request.user, original_post=board).exists()
    
    
    # 閲覧数を計算・保存
    board.views += 1  # 閲覧数を1増加
    board.save(update_fields=['views'])  # 閲覧数のみを保存

    return render(request, "show.html", {
        "board": board, 
        "comments": comments, 
        "comment_form": comment_form, 
        "is_reposted": is_reposted})

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

def privacypolicy(request):
    return render(request, "privacypolicy.html")