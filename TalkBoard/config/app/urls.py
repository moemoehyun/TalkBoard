from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings

from django.views.static import serve
from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static


app_name = 'app'
urlpatterns = [
    # 他のパス設定...
    path('favorite-toggle/<int:board_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('email_sent/<int:user_id>/', views.email_sent, name='email_sent'),
    path('activation_failed/', views.activation_failed, name='activation_failed'),
    re_path(r'^favicon\.ico$', serve, {'path': 'favicon.ico', 'document_root': settings.STATIC_ROOT}),
    path('resend_email/<int:user_id>/', views.resend_email, name='resend_email'),


    path("", views.index, name = "index"),
    # path('cropped-image/<int:board_id>/', views.serve_cropped_image, name='cropped_image'),
    path("new/", login_required(views.new), name = "new"),
    path("create/", login_required(views.create), name = "create"),
    path("show/<int:pk>/", login_required(views.show), name = "show"),
    path("show/<int:pk>/edit", login_required(views.edit), name = "edit"),
    path("show/<int:pk>/update", login_required(views.update), name = "update"),
    path("show/<int:pk>/delete", login_required(views.delete), name = "delete"),
    path("show/<int:pk>/comment/", login_required(views.comment_create), name="comment_create"),
    path("show/<int:board_pk>/comment/<int:comment_pk>/delete/", login_required(views.comment_delete), name="comment_delete"),
    path("my_board/", login_required(views.my_boards), name = "my_boards" ),
    path("search/", views.board_search, name="search"),
    path("sort/", views.board_sort, name="sort"),
    path("add_favorite/", views.add_favorite, name="add_favorite"),
    path("remove_favorite/", views.remove_favorite, name="remove_favorite"),
    path('favorites_boards/', views.favorite_boards, name='favorite_boards'),  # お気に入りページの URL
    path("contact/", views.contact, name="contact"),
    path("contact/success", views.contact_success, name="contact_success"),


    path("option", views.option, name="option"),

    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/profile/", views.profile, name="my_profile"),
    path('accounts/profile/<int:user_id>/', views.profile, name='profile'),
    path("accounts/edit_profile", views.edit_profile, name="edit_profile"),

    path("disclaimer", views.disclaimer, name="disclaimer"),
    path("privacypolicy", views.privacypolicy, name="privacypolicy")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
    # urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)