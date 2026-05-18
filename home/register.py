import re
from django.contrib.auth.models import User


def validate_signup(username, email, password, confirm_password):

    # Password match
    if password != confirm_password:
        return "Passwords do not match"

    # Username exists
    if User.objects.filter(username=username).exists():
        return "Username already exists"

    # Email exists
    if User.objects.filter(email=email).exists():
        return "Email already registered"

    # Email format
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return "Invalid email format"

    # Password rules
    if len(password) < 8:
        return "Password must be at least 8 characters"

    if not re.search(r'[A-Z]', password):
        return "Password must contain an uppercase letter"

    if not re.search(r'[a-z]', password):
        return "Password must contain a lowercase letter"

    if not re.search(r'[0-9]', password):
        return "Password must contain a number"

    if not re.search(r'[@$!%*?&]', password):
        return "Password must contain a special character"

    return None  # ✅ No error