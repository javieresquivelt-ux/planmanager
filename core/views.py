from django.shortcuts import redirect


def home(request):
    if request.user.is_authenticated:
        return redirect("users:profile")
    return redirect("users:login")
