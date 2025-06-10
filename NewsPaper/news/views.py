from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django import forms
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
from .models import Post, CategorySubscriber, Category, Author
from .filters import PostFilter
from .forms import PostForm
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


class PostList(ListView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
    ordering = ['-date_time_creation']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        
        # Применяем фильтры
        queryset = self.filterset.qs
        
        # Фильтрация по типу публикации
        post_type = self.request.GET.get('type')
        if post_type == 'NE':
            queryset = queryset.filter(post_status='NE')
        elif post_type == 'AR':
            queryset = queryset.filter(post_status='AR')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_type'] = self.request.GET.get('type', '')
        context['filter'] = self.filterset
        
        # Получаем все категории
        categories = Category.objects.all()
        
        # Если пользователь авторизован, добавляем информацию о подписках
        if self.request.user.is_authenticated:
            subscribed_categories = set(
                CategorySubscriber.objects.filter(
                    user=self.request.user
                ).values_list('category_id', flat=True)
            )
            context['subscribed_categories'] = subscribed_categories
        
        context['categories'] = categories
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'news/newid.html'
    context_object_name = 'newid'


class Posts(View):

    def get(self, request):
        posts = Post.objects.order_by('-date_time_creation')
        p = Paginator(posts, 1)
        posts = p.get_page(request.GET.get('page', 1))
        data = {'posts': posts, }

        return render(request, 'news/paginator.html', data)


class PostSearch(ListView):
    model = Post
    template_name = 'news/search.html'
    form_class = PostFilter
    context_object_name = 'search'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostFilter()
        return context
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


def send_notification_email(post, category):
    subscribers = CategorySubscriber.objects.filter(category=category)
    for subscriber in subscribers:
        user = subscriber.user
        if user.email:  # Проверяем, что у пользователя есть email
            context = {
                'user': user,
                'post': post,
                'category': category,
                'site_url': settings.SITE_URL,  # Добавляем URL сайта в контекст
            }
            html_message = render_to_string('news/email/new_post_notification.html', context)
            send_mail(
                subject=f'Новая статья в категории {category.topic}',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
            )


class PostAdd(PermissionRequiredMixin, CreateView):
    template_name = 'news/add.html'
    form_class = PostForm
    permission_required = 'news.add_post'
    login_url = '/accounts/login/'

    def get_initial(self):
        initial = super().get_initial()
        author, created = Author.objects.get_or_create(user=self.request.user)
        initial['author'] = author
        return initial

    def form_valid(self, form):
        author, created = Author.objects.get_or_create(user=self.request.user)
        form.instance.author = author
        response = super().form_valid(form)
        
        # Отправляем уведомления подписчикам категорий
        for category in form.instance.category.all():
            send_notification_email(form.instance, category)
            
        return response


class UpdatePost(PermissionRequiredMixin, UpdateView):
    template_name = 'news/add.html'
    form_class = PostForm
    permission_required = 'news.change_post'
    login_url = '/accounts/login/'

    def get_queryset(self):
        # Получаем только посты текущего автора
        return Post.objects.filter(author__user=self.request.user)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return get_object_or_404(Post, pk=id, author__user=self.request.user)


class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/delete.html'
    context_object_name = 'newid'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news:home')
    permission_required = 'news.delete_post'
    login_url = '/accounts/login/'


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
        print(f"User {user.username} added to authors group")  # Отладочная информация
    else:
        print(f"User {user.username} is already in authors group")  # Отладочная информация
    return redirect('/news/')


@login_required
@require_POST
def subscribe_to_category(request, pk):
    print("="*50)
    print("DEBUG: subscribe_to_category called")
    print(f"Request method: {request.method}")
    print(f"Request POST data: {request.POST}")
    print(f"Request user: {request.user}")
    print(f"Category ID: {pk}")
    
    try:
        category = get_object_or_404(Category, pk=pk)
        print(f"Found category: {category.topic}")
        
        # Проверяем существующую подписку
        is_subscribed = category.get_subscription_status(request.user)
        print(f"Current subscription status: {is_subscribed}")
        
        if not is_subscribed:
            try:
                subscriber = CategorySubscriber.objects.create(
                    user=request.user,
                    category=category
                )
                print(f"Created new subscription: {subscriber}")
            except Exception as e:
                print(f"Error creating subscription: {str(e)}")
                # Если произошла ошибка при создании, проверяем, возможно подписка уже существует
                is_subscribed = category.get_subscription_status(request.user)
                print(f"Subscription status after error: {is_subscribed}")
        else:
            print("Subscription already exists")
        
        # Проверяем результат
        final_status = category.get_subscription_status(request.user)
        print(f"Final subscription status: {final_status}")
        print("="*50)
        
        return redirect('news:category_detail', pk=pk)
    except Exception as e:
        print(f"ERROR in subscribe_to_category: {str(e)}")
        print("="*50)
        raise

@login_required
@require_POST
def unsubscribe_from_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    deleted, _ = CategorySubscriber.objects.filter(user=request.user, category=category).delete()
    print(f"User {request.user.username} unsubscribed from category {category.topic}, deleted: {deleted}")
    return redirect('news:category_detail', pk=pk)


class CategoryDetail(DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.post_set.all().order_by('-date_time_creation')
        if self.request.user.is_authenticated:
            context['is_subscribed'] = self.object.get_subscription_status(self.request.user)
        return context


@login_required
@require_POST
@ensure_csrf_cookie
def like_post(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)
        post.like()
        post.save()
        # Обновляем рейтинг автора
        post.author.update_rating()
        post.author.save()
        return JsonResponse({
            'rating': post.rating_post,
            'author_rating': post.author.rating_author
        })
    except Exception as e:
        logger.error(f"Error in like_post: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)

@login_required
@require_POST
@ensure_csrf_cookie
def dislike_post(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)
        post.dislike()
        post.save()
        # Обновляем рейтинг автора
        post.author.update_rating()
        post.author.save()
        return JsonResponse({
            'rating': post.rating_post,
            'author_rating': post.author.rating_author
        })
    except Exception as e:
        logger.error(f"Error in dislike_post: {str(e)}")
        return JsonResponse({
            'error': str(e)
        }, status=500)


