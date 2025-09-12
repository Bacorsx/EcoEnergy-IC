from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignupForm

User = get_user_model()


@login_required
def user_list(request):
    # Filtra por organización del usuario logueado (multitenancy)
    qs = User.objects.all()
    if request.user.organization_id:
        qs = qs.filter(organization_id=request.user.organization_id)

    users = qs.order_by("username")
    return render(request, "usuarios/user_list.html", {"users": users})


@login_required
def user_detail(request, pk: int):
    # Restringe el detalle a la organización actual
    qs = User.objects.all()
    if request.user.organization_id:
        qs = qs.filter(organization_id=request.user.organization_id)

    user = get_object_or_404(qs, pk=pk)
    return render(request, "usuarios/user_detail.html", {"user": user})


def signup(request):
    # Si ya está autenticado, lo mandamos al dashboard
    if request.user.is_authenticated:
        messages.info(request, "Ya tienes una sesión iniciada.")
        return redirect("dashboard")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user, org = form.save()
            login(request, user)
            messages.success(
                request,
                f"¡Registro completado! Empresa “{org.name}” creada correctamente. Bienvenido a EcoEnergy."
            )
            return redirect("dashboard")
        else:
            messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = SignupForm()

    return render(request, "usuarios/signup.html", {"form": form})
