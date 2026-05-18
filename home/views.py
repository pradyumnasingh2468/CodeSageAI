"""
views.py

Clean version:
- Authentication
- Dashboard (Chat system)
- Profile & Settings
- File upload (AI analysis)
"""

# =========================
# IMPORTS
# =========================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Chat, Message, Profile
from .register import validate_signup
from home.upload import analyze_with_langchain, is_code


# =========================
# 🔐 AUTHENTICATION
# =========================

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        error = validate_signup(username, email, password, confirm_password)

        if error:
            messages.error(request, error)
            return redirect('signup')

        User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 📊 DASHBOARD (CHAT SYSTEM)
# =========================

@login_required
def dashboard(request, chat_id=None):
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')

    current_chat = None
    messages_list = []

    if chat_id:
        current_chat = get_object_or_404(Chat, id=chat_id, user=request.user)

        if request.method == "POST":
            content = request.POST.get("message")

            if content:
                # Load last 9 messages as per-chat context BEFORE saving the new one
                history_qs = current_chat.messages.order_by('-timestamp')[:9]
                chat_history = [
                    {"role": m.sender, "content": m.content}
                    for m in reversed(list(history_qs))
                ]

                # Save user message
                user_msg = Message.objects.create(
                    chat=current_chat,
                    sender='user',
                    content=content
                )

                # Auto-title on first message
                if current_chat.title == "New Chat":
                    clean_title = content.strip().split('\n')[0][:40]
                    current_chat.title = clean_title if clean_title else "New Chat"
                    current_chat.save()

                # Detect file extension hint from content if code block present
                ext = "txt"
                if content.startswith("```") and "\n" in content:
                    first_line = content.split("\n")[0].strip("`").strip()
                    if first_line:
                        ext = first_line

                # Call AI with per-chat history (no global session leakage)
                reply = analyze_with_langchain(content, ext, chat_history)

                ai_msg = Message.objects.create(
                    chat=current_chat,
                    sender='ai',
                    content=reply
                )

                return JsonResponse({
                    "user": user_msg.content,
                    "ai": ai_msg.content
                })

        messages_list = current_chat.messages.all()

    return render(request, 'dashboard.html', {
        'chats': chats,
        'messages': messages_list,
        'current_chat': current_chat
    })


# =========================
# 🆕 NEW CHAT
# =========================

@login_required
def new_chat(request):
    chat = Chat.objects.create(user=request.user)
    return redirect('dashboard_chat', chat_id=chat.id)


# =========================
# 🧹 CLEAR CHAT
# =========================

@login_required
def clear_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.messages.all().delete()
    return redirect('dashboard_chat', chat_id=chat.id)


# =========================
# 👤 PROFILE
# =========================

@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':

        # Remove profile image
        if 'remove_photo' in request.POST:
            if profile.image and profile.image.name != 'profile_pics/default.png':
                profile.image.delete(save=False)

            profile.image = 'profile_pics/default.png'
            profile.save()
            return redirect('profile')

        # Upload new image
        if request.FILES.get('image'):
            if profile.image and profile.image.name != 'profile_pics/default.png':
                profile.image.delete(save=False)

            profile.image = request.FILES['image']
            profile.save()
            return redirect('profile')

    return render(request, 'profile.html', {'profile': profile})


# =========================
# ⚙️ SETTINGS
# =========================

@login_required
def setting(request):
    user = request.user

    if request.method == "POST":

        # Delete account
        if 'delete_account' in request.POST:
            confirm = request.POST.get('confirm_text')

            if confirm != "DELETE":
                messages.error(request, "Type DELETE to confirm account deletion")
                return redirect('settings')

            user.delete()
            messages.success(request, "Account deleted successfully")
            return redirect('login')

        # Update profile
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Check duplicates
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('settings')

        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, "Email already used")
            return redirect('settings')

        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Profile updated successfully")
        return redirect('settings')

    return render(request, 'settings.html')


# =========================
# 📂 FILE UPLOAD (AI ANALYSIS)
# =========================

@login_required
def upload_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    file = request.FILES.get("file")

    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    try:
        code = file.read().decode("utf-8")
        ext = file.name.split('.')[-1]

        # File uploads have no prior context — analyzed as standalone
        result = analyze_with_langchain(code, ext, chat_history=None)

        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =========================
# 📄 STATIC PAGES
# =========================

@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def helps(request):
    return render(request, 'help.html')


@login_required
def contact(request):
    return render(request, 'contact.html')

@login_required
def delete_chat(request, chat_id):
    if request.method == "POST":
        chat = get_object_or_404(Chat, id=chat_id, user=request.user)
        chat.delete()
        return JsonResponse({"success": True})


# =========================
# 💬 GET MESSAGES (API)
# =========================

@login_required
def get_messages(request, chat_id):
    """Return all messages for a chat as JSON (used by dashboard.js)."""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    msgs = chat.messages.order_by('timestamp').values('sender', 'content', 'timestamp')
    return JsonResponse({
        "messages": [
            {"role": m["sender"], "content": m["content"]}
            for m in msgs
        ]
    })