from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class Command(BaseCommand):
    help = 'Отправляет приветственные письма всем существующим пользователям'

    def handle(self, *args, **options):
        # Получаем всех пользователей с email
        users = User.objects.exclude(email='')
        
        self.stdout.write(f'Найдено {users.count()} пользователей с email')
        
        for user in users:
            try:
                context = {
                    'user': user,
                    'site_url': settings.SITE_URL,
                }
                
                html_message = render_to_string('news/email/welcome_email.html', context)
                
                send_mail(
                    subject='Добро пожаловать в NewsPaper!',
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Отправлено приветственное письмо пользователю {user.username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при отправке письма пользователю {user.username}: {str(e)}')
                ) 