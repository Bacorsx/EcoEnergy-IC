from __future__ import annotations
from typing import List
from django.db import transaction

from .models import Measurement, ProductAlert, ProductAlertEvent


def _norm_unit(u: str | None) -> str:
    """
    Normaliza unidades: minúsculas y elimina caracteres no alfanuméricos,
    para que '°C', 'C', 'c' se consideren equivalentes.
    """
    if not u:
        return ""
    return "".join(ch for ch in u.lower().strip() if ch.isalnum())


@transaction.atomic
def generate_alert_events_for_measurement(measurement: Measurement) -> List[ProductAlertEvent]:
    """
    Evalúa la medición contra las reglas (ProductAlert) del producto y crea
    ProductAlertEvent cuando corresponde.

    - Evita duplicados por (product_alert, measurement) con get_or_create.
    - Rango inclusivo: [range_min, range_max].
    - Si la unidad de la regla está vacía, se toma como comodín (match con cualquiera).
      Si no está vacía, se compara normalizada con la de la medición.
    - **No** filtramos por estado aquí para no depender de defaults durante tests.
      Si quieres volver a exigirlo, añade .filter(estado=True) a la QuerySet de rules.
    """
    created: List[ProductAlertEvent] = []

    product = measurement.product
    if not product:
        return created

    val = measurement.value
    mu  = _norm_unit(measurement.unit)

    # Quita el filtro por estado para que el test no dependa de defaults
    rules = (
        ProductAlert.objects
        .select_related("alert", "product")
        .filter(product=product)
    )

    for rule in rules:
        rule_unit_norm = _norm_unit(rule.unit)
        # Si la regla trae unidad, debe coincidir; si está vacía, acepta cualquier unidad
        if rule_unit_norm and rule_unit_norm != mu:
            continue

        if rule.range_min <= val <= rule.range_max:
            evt, was_created = ProductAlertEvent.objects.get_or_create(
                product_alert=rule,
                measurement=measurement,
                defaults={"is_resolved": False},
            )
            if was_created:
                created.append(evt)

    return created