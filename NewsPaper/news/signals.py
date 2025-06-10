from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Отправляет приветственное письмо новому пользователю при регистрации
    """
    if created and instance.email:  # Проверяем, что это новый пользователь и у него есть email
        context = {
            'user': instance,
            'site_url': settings.SITE_URL,
        }
        
        html_message = render_to_string('news/email/welcome_email.html', context)
        
        send_mail(
            subject='Добро пожаловать в NewsPaper!',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
        ) 