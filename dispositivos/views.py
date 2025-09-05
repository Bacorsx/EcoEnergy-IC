from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Device, Measurement, Alert, Category, Zone
from .forms import DeviceForm


def dashboard(request):
    # Filtros de tarjetas inferiores (dispositivos)
    cat = request.GET.get("category") or ""
    zon = request.GET.get("zone") or ""

    devices = Device.objects.select_related("category", "zone").all()
    if cat:
        devices = devices.filter(category_id=cat)
    if zon:
        devices = devices.filter(zone_id=zon)

    # KPIs superiores
    counts_by_cat = (
        Category.objects.annotate(n=Count("devices"))
        .values("id", "name", "n")
        .order_by("name")
    )
    counts_by_zone = (
        Zone.objects.annotate(n=Count("devices"))
        .values("id", "name", "n")
        .order_by("name")
    )

    # Alertas de la semana (por severidad)
    since = timezone.now() - timedelta(days=7)
    alerts_week = (
        Alert.objects.filter(created_at__gte=since)
        .values("severity")
        .annotate(n=Count("id"))
    )
    sev_map = {"critical": 0, "high": 0, "medium": 0}
    for row in alerts_week:
        sev_map[row["severity"]] = row["n"]

    last_measurements = (
        Measurement.objects.select_related("device")
        .order_by("-measured_at")[:10]
    )
    recent_alerts = (
        Alert.objects.select_related("device")
        .order_by("-created_at")[:6]
    )

    # combos
    categories = Category.objects.all()
    zones = Zone.objects.all()

    # Dispositivos tipo “cards” (muestra primeros 6)
    device_cards = devices[:6]

    context = {
        "counts_by_cat": counts_by_cat,
        "counts_by_zone": counts_by_zone,
        "sev_map": sev_map,
        "last_measurements": last_measurements,
        "recent_alerts": recent_alerts,
        "categories": categories,
        "zones": zones,
        "cat_selected": cat,
        "zone_selected": zon,
        "device_cards": device_cards,
    }
    return render(request, "dashboard.html", context)

def device_list(request):
    cat = request.GET.get("category") or ""
    zon = request.GET.get("zone") or ""
    q = request.GET.get("q", "").strip()

    qs = Device.objects.select_related("category", "zone").all()
    if cat:
        qs = qs.filter(category_id=cat)
    if zon:
        qs = qs.filter(zone_id=zon)
    if q:
        qs = qs.filter(name__icontains=q)

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    devices = paginator.get_page(page)

    return render(request, "dispositivos/device_list.html", {
        "devices": devices,
        "categories": Category.objects.all(),
        "zones": Zone.objects.all(),
        "cat_selected": cat,
        "zone_selected": zon,
        "q": q,
    })

def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    measurements = device.measurements.order_by("-measured_at")[:20]
    alerts = device.alerts.order_by("-created_at")[:10]
    return render(request, "dispositivos/device_detail.html", {
        "device": device, "measurements": measurements, "alerts": alerts
    })

def device_create(request):
    form = DeviceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dispositivo creado.")
        return redirect("device_list")
    return render(request, "dispositivos/device_form.html", {"form": form, "title": "Nuevo dispositivo"})

def device_update(request, pk):
    device = get_object_or_404(Device, pk=pk)
    form = DeviceForm(request.POST or None, instance=device)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dispositivo actualizado.")
        return redirect("device_detail", pk=device.pk)
    return render(request, "dispositivos/device_form.html", {"form": form, "title": "Editar dispositivo"})

def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        device.delete()
        messages.success(request, "Dispositivo eliminado.")
        return redirect("device_list")
    return render(request, "dispositivos/device_confirm_delete.html", {"device": device})

def measurement_list(request):
    qs = Measurement.objects.select_related("device").order_by("-measured_at")[:100]
    return render(request, "dispositivos/measurement_list.html", {"measurements": qs})

def alert_list(request):
    qs = Alert.objects.select_related("device").order_by("-created_at")[:100]
    return render(request, "dispositivos/alert_list.html", {"alerts": qs})