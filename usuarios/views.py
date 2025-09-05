# usuarios/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

def user_list(request):
    users = User.objects.all().order_by("username")
    return render(request, "usuarios/user_list.html", {"users": users})

def user_detail(request, pk: int):
    user = get_object_or_404(User, pk=pk)
    return render(request, "usuarios/user_detail.html", {"user": user})
