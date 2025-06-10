from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.forms import ModelForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
# Create your models here.

User = get_user_model()


class Author(models.Model):
    rating_author = models.IntegerField(default=0)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def update_rating(self):
        # суммарный рейтинг каждой статьи автора умножается на 3
        rating_post = self.posts.all().aggregate(Sum('rating_post'))['rating_post__sum'] or 0
        rating_post *= 3

        # суммарный рейтинг всех комментариев автора
        rating_comments = self.user.users.all().aggregate(Sum('rating_comment'))['rating_comment__sum'] or 0

        # суммарный рейтинг всех комментариев к статьям автора
        rating_comments_articles = 0
        for post in self.posts.all():
            post_comments_rating = post.posts.all().aggregate(Sum('rating_comment'))['rating_comment__sum'] or 0
            rating_comments_articles += post_comments_rating

        self.rating_author = rating_post + rating_comments + rating_comments_articles
        return self.rating_author

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name} ({self.user.username})"
        return self.user.username

class Category(models.Model):
    topic = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.topic

    @property
    def has_subscribers(self):
        return self.subscribers.exists()

    @property
    def subscribers(self):
        return User.objects.filter(category_subscriptions__category=self)

    def is_subscribed(self, user=None):
        if not user or not user.is_authenticated:
            return False
        try:
            return CategorySubscriber.objects.filter(user=user, category=self).exists()
        except Exception as e:
            print(f"Error checking subscription: {str(e)}")
            return False

    def get_subscription_status(self, user):
        if not user or not user.is_authenticated:
            return False
        try:
            return CategorySubscriber.objects.filter(user=user, category=self).exists()
        except Exception as e:
            print(f"Error getting subscription status: {str(e)}")
            return False

class Post(models.Model):
    AR = 'AR'
    NE = 'NE'
    ARTICLE_OR_NEWS_SELECTION_FIELD = {
        AR: 'Статья',
        NE: 'Новость',
    }
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_status =  models.CharField(
        max_length=2,
        choices=ARTICLE_OR_NEWS_SELECTION_FIELD,
        default=AR
    )
    post_category = models.CharField(max_length=20)
    date_time_creation = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(
        Category,
        through="PostCategory"
    )

    heading = models.CharField(
        max_length=64,
    )
    text_post = models.TextField()
    rating_post = models.IntegerField(default=0)

    def like(self):
        self.rating_post += 1
        return self.rating_post
    def dislike(self):
        if self.rating_post > 0:
            self.rating_post -= 1
            return self.rating_post
        return self.rating_post

    def preview(self):
        if len(self.text_post)>125:
            result = f'{self.text_post[0:125]}...'
            return result
        return self.text_post

    def get_absolute_url(self):
        return f'/news/{self.id}'

    def __str__(self):

        return (f'Дата создания: {self.date_time_creation.strftime('%d.%b.%Y %H:%M')}\n'
                f'Автор: {self.author.user.username}\n'
                f'Рейтинг автора: {self.author.rating_author}\n'
                f'Заголовок: {self.heading}\n'
                f'Превью: {self.preview()}')

    def notify_subscribers(self):
        # Получаем всех подписчиков категорий этой публикации
        for category in self.category.all():
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                # Формируем контекст для шаблона
                context = {
                    'subscriber': subscriber,
                    'category': category,
                    'post': self,
                    'site_url': settings.SITE_URL,  # Добавьте SITE_URL в settings.py
                }
                
                # Рендерим HTML-шаблон письма
                html_message = render_to_string(
                    'news/email/new_post_notification.html',
                    context
                )
                
                # Формируем тему письма
                subject = f'Новая публикация в категории {category.topic}'
                
                # Отправляем письмо
                send_mail(
                    subject=subject,
                    message='',  # Пустое текстовое сообщение
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Добавьте DEFAULT_FROM_EMAIL в settings.py
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=True,  # Не вызывать исключение при ошибке отправки
                )

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)




class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users')
    text_comment = models.TextField()
    date_time_comment = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        return self.rating_comment

    def dislike(self):
        if self.rating_comment > 0:
            self.rating_comment -= 1
            return self.rating_comment
        return self.rating_comment

    def __str__(self):
        return (f'Дата создания коментария: {self.date_time_comment.strftime('%d.%b.%Y %H:%M')}\n'
                f'Имя пользователя: {self.user.username}\n'
                f'Рейтинг: {self.rating_comment}\n'
                f'Текст коментария: {self.text_comment}')

class CategorySubscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subscribers')
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')  # Предотвращает дублирование подписок

class PostForm(ModelForm):
    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            post.notify_subscribers()  # Отправляем уведомления после сохранения
        return post

