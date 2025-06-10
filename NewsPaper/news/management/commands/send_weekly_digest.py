from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from news.models import CategorySubscriber, Post

class Command(BaseCommand):
    help = 'Отправляет еженедельную рассылку подписчикам'

    def handle(self, *args, **options):
        # Получаем дату неделю назад
        week_ago = timezone.now() - timedelta(days=7)
        
        # Получаем всех подписчиков
        subscribers = CategorySubscriber.objects.select_related('user', 'category').all()
        
        # Для каждого подписчика
        for subscriber in subscribers:
            user = subscriber.user
            if not user.email:
                continue
                
            # Получаем все категории пользователя
            user_categories = CategorySubscriber.objects.filter(user=user).values_list('category', flat=True)
            
            # Получаем новые посты за неделю для категорий пользователя
            category_posts = {}
            for category_id in user_categories:
                posts = Post.objects.filter(
                    category=category_id,
                    date_time_creation__gte=week_ago
                ).order_by('-date_time_creation')
                
                if posts.exists():
                    category = posts.first().category.all().get(id=category_id)
                    category_posts[category] = posts
            
            # Если есть новые посты, отправляем письмо
            if category_posts:
                context = {
                    'user': user,
                    'category_posts': category_posts,
                    'site_url': settings.SITE_URL,
                }
                
                html_message = render_to_string('news/email/weekly_digest.html', context)
                
                send_mail(
                    subject='Еженедельная рассылка новых публикаций',
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Отправлена рассылка пользователю {user.username}')
                ) 