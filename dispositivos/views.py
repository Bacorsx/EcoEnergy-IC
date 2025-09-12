# dispositivos/views.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Device, Product, Measurement, Alert, Category, Zone, ProductAlertEvent
from .forms import DeviceForm, ProductForm


@login_required
def dashboard(request):
    cat = request.GET.get("category") or ""
    zon = request.GET.get("zone") or ""

    devices = Device.objects.select_related("zone").all()
    if cat:
        devices = devices.filter(products__category_id=cat).distinct()
    if zon:
        devices = devices.filter(zone_id=zon)

    counts_by_cat = (
        Category.objects.annotate(n=Count("products"))
        .values("id", "name", "n").order_by("name")
    )
    counts_by_zone = (
        Zone.objects.annotate(n=Count("devices"))
        .values("id", "name", "n").order_by("name")
    )

    since = timezone.now() - timedelta(days=7)

    # ✅ Conteo semanal por severidad usando eventos
    events_week = (
        ProductAlertEvent.objects
        .filter(created_at__gte=since)
        .values("product_alert__alert__severity")
        .annotate(n=Count("id"))
    )
    sev_map = {"GRAVE": 0, "ALTO": 0, "MEDIANO": 0}
    for row in events_week:
        sev = row["product_alert__alert__severity"]
        if sev in sev_map:
            sev_map[sev] = row["n"]

    # Últimas mediciones (todas)
    last_measurements = (
        Measurement.objects.select_related("product", "product__device")
        .order_by("-measured_at")[:10]
    )

    # ✅ Alertas recientes = últimos eventos
    recent_events = (
        ProductAlertEvent.objects
        .select_related("product_alert__alert", "product_alert__product", "measurement", "product_alert__product__device")
        .order_by("-created_at")[:6]
    )

    context = {
        "counts_by_cat": counts_by_cat,
        "counts_by_zone": counts_by_zone,
        "sev_map": sev_map,
        "last_measurements": last_measurements,
        "recent_alerts_ms": recent_events,   # ← el template ya espera esta clave
        "categories": Category.objects.all(),
        "zones": Zone.objects.all(),
        "cat_selected": cat,
        "zone_selected": zon,
        "device_cards": devices[:6],
    }
    return render(request, "dispositivos/dashboard.html", context)

@login_required
def product_list(request):
    cat = request.GET.get("category") or ""
    device_id = request.GET.get("device") or ""
    q = request.GET.get("q") or ""

    products_qs = Product.objects.select_related("device", "category", "device__zone").all()
    if cat:
        products_qs = products_qs.filter(category_id=cat)
    if device_id:
        products_qs = products_qs.filter(device_id=device_id)
    if q:
        products_qs = products_qs.filter(name__icontains=q)

    paginator = Paginator(products_qs, 25)
    products_page = paginator.get_page(request.GET.get("page"))

    context = {
        "products": products_page,
        "categories": Category.objects.all(),
        "devices": Device.objects.select_related("zone").all(),
        "cat_selected": cat,
        "device_selected": device_id,
        "q": q,
        "is_empty_products": products_page.paginator.count == 0,
    }
    return render(request, "dispositivos/product_list.html", context)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("device", "device__zone", "device__organization", "category"),
        pk=pk
    )

    measurements = product.measurements.order_by("-measured_at")[:20]

    # ✅ eventos (alertas) del producto
    events = (
        ProductAlertEvent.objects
        .filter(product_alert__product=product)
        .select_related("product_alert__alert", "measurement")
        .order_by("-created_at")[:10]
    )

    alerts_active_count = events.filter(is_resolved=False).count()

    context = {
        "product": product,
        "measurements": measurements,
        "alerts": events,                 # el template puede llamarlas "alerts" pero son eventos
        "alerts_active_count": alerts_active_count,
    }
    return render(request, "dispositivos/product_detail.html", context)

@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Producto '{product.name}' creado exitosamente.")
            return redirect("dispositivos:product_detail", pk=product.pk)
        messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = ProductForm()
    return render(request, "dispositivos/product_form.html", {"form": form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Producto '{product.name}' actualizado exitosamente.")
            return redirect("dispositivos:product_detail", pk=product.pk)
        messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = ProductForm(instance=product)
    return render(request, "dispositivos/product_form.html", {"form": form, "product": product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Producto '{name}' eliminado exitosamente.")
        return redirect("dispositivos:product_list")
    return render(request, "dispositivos/product_confirm_delete.html", {"product": product})


# ------------------------ Dispositivos ------------------------
@login_required
def device_list(request):
    cat = request.GET.get("category") or ""
    zon = request.GET.get("zone") or ""
    q = request.GET.get("q") or ""

    devices_qs = Device.objects.select_related("zone").all()
    if cat:
        devices_qs = devices_qs.filter(products__category_id=cat).distinct()
    if zon:
        devices_qs = devices_qs.filter(zone_id=zon)
    if q:
        devices_qs = devices_qs.filter(name__icontains=q)

    paginator = Paginator(devices_qs, 25)
    devices_page = paginator.get_page(request.GET.get("page"))

    context = {
        "devices": devices_page,
        "categories": Category.objects.all(),
        "zones": Zone.objects.all(),
        "cat_selected": cat,
        "zone_selected": zon,
        "q": q,
        "is_empty_devices": devices_page.paginator.count == 0,
    }
    return render(request, "dispositivos/device_list.html", context)


@login_required
def device_detail(request, pk: int):
    device = get_object_or_404(
        Device.objects.select_related("zone", "organization"),
        pk=pk
    )

    products = device.products.select_related("category").all()

    recent_measurements = (
        Measurement.objects
        .select_related("product")
        .filter(product__device=device)
        .order_by("-measured_at")[:20]
    )

    recent_alerts = (
        Alert.objects
        .filter(measurements__product__device=device)
        .distinct()
        .order_by("-created_at")[:10]
    )

    context = {
        "device": device,
        "products": products,
        "measurements": recent_measurements,
        "alerts": recent_alerts,
        "is_empty_products": products.count() == 0,
        "is_empty_measurements": recent_measurements.count() == 0,
        "is_empty_alerts": recent_alerts.count() == 0,
    }
    return render(request, "dispositivos/device_detail.html", context)


@login_required
def device_create(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            messages.success(request, f"Dispositivo '{device.name}' creado exitosamente.")
            return redirect("dispositivos:device_detail", pk=device.pk)
        messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = DeviceForm()
    return render(request, "dispositivos/device_form.html", {"form": form, "title": "Nuevo Dispositivo"})


@login_required
def device_update(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            messages.success(request, f"Dispositivo '{device.name}' actualizado exitosamente.")
            return redirect("dispositivos:device_detail", pk=device.pk)
        messages.error(request, "Por favor corrige los errores indicados.")
    else:
        form = DeviceForm(instance=device)
    return render(request, "dispositivos/device_form.html", {"form": form, "device": device, "title": "Editar Dispositivo"})


@login_required
def device_delete(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        name = device.name
        device.delete()
        messages.success(request, f"Dispositivo '{name}' eliminado exitosamente.")
        return redirect("dispositivos:device_list")
    return render(request, "dispositivos/device_confirm_delete.html", {"device": device})


# ------------------------ Zonas / Categorías ------------------------
@login_required
def zone_list(request):
    zones = Zone.objects.select_related("organization").all()
    return render(request, "dispositivos/zone_list.html", {
        "zones": zones,
        "is_empty_zones": not zones.exists(),
    })


@login_required
def zone_detail(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    devices = zone.devices.all()
    return render(request, "dispositivos/zone_detail.html", {
        "zone": zone,
        "devices": devices,
        "is_empty_zone_devices": not devices.exists(),
    })


@login_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count("products")).all()
    return render(request, "dispositivos/category_list.html", {
        "categories": categories,
        "is_empty_categories": not categories.exists(),
    })


@login_required
def measurement_list(request):
    qs = (
        Measurement.objects
        .select_related("product", "product__device", "product__category")
        .prefetch_related("alert_events__product_alert__alert")  # eventos de alerta
        .order_by("-measured_at")
    )

    paginator = Paginator(qs, 50)
    page = request.GET.get("page")
    measurements = paginator.get_page(page)

    context = {
        "measurements": measurements,
        "is_empty_measurements": measurements.paginator.count == 0,
    }
    return render(request, "dispositivos/measurement_list.html", context)

@login_required
def alert_list(request):
    qs = (
        ProductAlertEvent.objects
        .select_related("product_alert__alert", "product_alert__product", "product_alert__product__device", "measurement")
        .order_by("-created_at")
    )
    return render(request, "dispositivos/alert_list.html", {"events": qs})

@login_required
@require_POST
def resolve_event(request, pk):
    event = get_object_or_404(ProductAlertEvent, pk=pk)
    if not event.is_resolved:
        event.is_resolved = True
        event.resolved_at = timezone.now()
        event.save(update_fields=["is_resolved", "resolved_at", "updated_at"])
        messages.success(request, "Alerta marcada como resuelta.")
    return redirect(request.META.get("HTTP_REFERER", "dispositivos:alert_list"))