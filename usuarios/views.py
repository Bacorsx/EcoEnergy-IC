from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignupForm

User = get_user_model()

@login_required
def user_list(request):
    users = User.objects.all().order_by("username")
    return render(request, "usuarios/user_list.html", {"users": users})

@login_required
def user_detail(request, pk: int):
    user = get_object_or_404(User, pk=pk)
    return render(request, "usuarios/user_detail.html", {"user": user})

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user, org = form.save()
            login(request, user)
            messages.success(request, f"¡Registro completado! Empresa “{org.name}” creada.")
            return redirect("dashboard")
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = SignupForm()

    return render(request, "usuarios/signup.html", {"form": form})
