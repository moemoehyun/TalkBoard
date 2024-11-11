# signals.py
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def send_verification_email(sender, instance, created, **kwargs):
    if created and not instance.email_verified:
        subject = "メールアドレスの確認"
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        verification_link = reverse('email_verification', args=[uid, token])
        email_body = render_to_string('registration/verification_email.html', {
            'user': instance,
            'verification_link': verification_link,
        })
        send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [instance.email])
