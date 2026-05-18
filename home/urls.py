"""
URL Configuration for CodeSageAI app

Clean version:
- Authentication
- Dashboard (Chat system)
- Profile & static pages
- File upload
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [

    # ================= AUTHENTICATION =================
    path('', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),


    # ================= DASHBOARD (CHAT SYSTEM) =================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<int:chat_id>/', views.dashboard, name='dashboard_chat'),

    path('new-chat/', views.new_chat, name='new_chat'),
    path('clear-chat/<int:chat_id>/', views.clear_chat, name='clear_chat'),


    # ================= MAIN PAGES =================
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('settings/', views.setting, name='settings'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.helps, name='help'),


    # ================= FILE UPLOAD =================
    path('upload/', views.upload_file, name='upload_file'),


    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),

    # ================= MESSAGES API =================
    path('get-messages/<int:chat_id>/', views.get_messages, name='get_messages'),
]


# ================= MEDIA FILES (DEV ONLY) =================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )