from django.shortcuts import render, redirect, get_object_or_404
from .forms import BoardForm, SignUpForm, CommentForm, FavoriteForm, ContactForm
from .models import Board, Comment, Favorite
from django.views.generic.edit import FormView
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic.detail import DetailView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.db.models import Count
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count

# Create your views here.
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

    return render(request, "index.html", {"board": boards})

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
        form = FavoriteForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect("app:index")
    return redirect("app:index")

@login_required
def remove_favorite(request):
    if request.method == "POST":
        favorite = Favorite.objects.get(user=request.user, board=request.POST.get("board"))
        favorite.delete()
        return redirect("app:index")
    return redirect("app:index")

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            #ユーザーへのメール
            user_subject = "お問い合わせを受け付けました"
            user_message = "お問い合わせ内容：\n\n{}".format(contact.message)
            send_mail(user_subject, user_message, settings.EMAIL_HOST_USER, [contact.email])
            #運営者へのメール
            admin_subject = "お問い合わせがありました"
            admin_message = "お問い合わせ内容：\n\n{}".format(contact.message)
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

#ログアウト
def logout_view(request):
    logout(request)
    return redirect("app:index")

#サインアップページのビュー
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("app:login")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

#プロフィールページのビュー
@login_required
def profile(request):
    user = request.user
    return render(request, "accounts/profile.html", {"user": user})

# class SignInView(FormView):
#     template_name = "renz_app/accounts/sign_in.html"
#     form_class = RenzUserCreationForm
#     success_url = "/accounts/comp_login"  # FIXME: 登録完了画面に遷移させるのが適切かもしれない

#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
        
#         data = form.cleaned_data

#         password1 = data["password1"]
#         password2 = data["password2"]
#         username = data["username"]

#         try:
#             validate_password(password1)
#         except ValidationError:
#             print("Validation Error")
#             return redirect("/accounts/sign_in")

#         if password1 != password2:
#             print("Password Incorrect")
#             return redirect("/accounts/sign_in")
        
#         user = User.objects.create_user(username, password=password1)
#         return super().form_valid(form)


# class LoginView(auth_views.LoginView):
#     authentication_form = RenzAuthenticationForm

# def CompLogin(request):
#     return render(request,"renz_app/accounts/comp_login.html")


# def user_detail(request, username):
#     user_queryset = User.objects.filter(username=username)
#     if not user_queryset.exists():
#         raise Http404("Specified user is not found")
    
#     user = user_queryset.first()
#     student_group_members = user.studentgroupmember_set.all()
#     company_members = user.companymember_set.all()

#     context = { "user": user, "student_group_members": student_group_members, "company_members": company_members, "is_mypage": request.user == user }

#     return render(request,"hurrays_app/users/detail.html", context)

# class UserDetailView(DetailView):
#     model = User

#     def get_context_data(self, **kwargs):
#         username = kwargs.get("username")
#         if username is None:
#             return None

#         user_queryset = self.model.objects.filter(username=username)
#         if not user_queryset.exists():
#             return None

#         return {
#             "object": user_queryset.first(),
#             "context_object_name": self.get_context_object_name()
#         }


# def sign_in(request):
#     return render(request, "renz_app/accounts/sign_in.html")


# def game_select(request):
#     return render(request, "renz_app/game/game_select.html")

# def blackjack(request):
#     return render(request, "renz_app/game/blackjack.html") #ブラックジャック

