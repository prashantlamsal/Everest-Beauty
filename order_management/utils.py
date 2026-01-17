from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.templatetags.static import static
from django.utils import timezone


def default_estimated_delivery(delivery_method: str) -> str:
    today = timezone.localdate()
    if delivery_method == 'express':
        eta = today + timedelta(days=2)
        return eta.strftime('%b %d, %Y')
    eta = today + timedelta(days=4)
    return eta.strftime('%b %d, %Y')


def send_order_confirmation_email(order, request=None, estimated_delivery: str | None = None):
    """Send order confirmation email; swallow failures so checkout isn't blocked."""
    try:
        logo_url = None
        if request:
            try:
                logo_url = request.build_absolute_uri(static('img/brand-logo.svg'))
            except Exception:
                logo_url = None

        eta_display = estimated_delivery or default_estimated_delivery(order.payment_method)
        context = {
            'order': order,
            'user': order.user,
            'items': order.items.all(),
            'total': order.total_amount,
            'payment_method': order.payment_method,
            'order_date': order.created_at,
            'estimated_delivery': eta_display,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
            'support_phone': getattr(settings, 'SUPPORT_PHONE', None),
            'business_hours': getattr(settings, 'BUSINESS_HOURS', None),
            'logo_url': logo_url,
            'brand_name': getattr(settings, 'BRAND_NAME', 'Everest Beauty'),
            'primary_color': '#f43f5e',
            'secondary_color': '#0ea5e9',
        }

        subject = f"Order Confirmation — {context['brand_name']} #{order.order_number}"
        html_content = render_to_string('order_management/emails/order_confirmation.html', context, request=request)
        text_content = strip_tags(html_content)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@example.com'

        email = EmailMultiAlternatives(subject, text_content, from_email, [order.shipping_email])
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=getattr(settings, 'EMAIL_FAIL_SILENTLY', False))
    except Exception:
        # Do not raise; logging can be added later
        return False
    return True
