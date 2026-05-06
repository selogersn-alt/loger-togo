from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        if value is None:
            return "0"
        # On convertit en float puis int pour enlever les décimales
        value = int(float(value))
        # Formatage avec espace comme séparateur de milliers
        return "{:,}".format(value).replace(",", " ")
    except (ValueError, TypeError):
        return value
