from django_filters import FilterSet, DateFilter, CharFilter, ModelMultipleChoiceFilter, ChoiceFilter
from django.forms.widgets import TextInput, Select, CheckboxSelectMultiple
from django.db.models import Value, CharField, F, Q
from django.db.models.functions import Concat
from .models import Post, Category, Author


class PostFilter(FilterSet):
    date_time_creation = DateFilter(
        field_name='date_time_creation',
        lookup_expr='gte',
        widget=TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Дата публикации (от)'
    )
    
    post_status = ChoiceFilter(
        field_name='post_status',
        choices=[('', 'Все типы'), ('AR', 'Статья'), ('NE', 'Новость')],
        widget=Select(attrs={'class': 'form-control'}),
        label='Тип публикации'
    )
    
    author__user__username = ChoiceFilter(
        field_name='author__user__username',
        choices=lambda: Author.objects.annotate(
            display_name=Concat(
                'user__username',
                Value(' '),
                F('user__first_name'),
                Value(' '),
                F('user__last_name'),
                output_field=CharField()
            )
        ).values_list('user__username', 'display_name').order_by('user__username'),
        empty_label='Все авторы',
        widget=Select(attrs={'class': 'form-control'}),
        label='Автор'
    )
    
    category = ChoiceFilter(
        field_name='category',
        choices=lambda: Category.objects.exclude(
            topic__startswith='Автор:'
        ).values_list('id', 'topic').order_by('topic'),
        empty_label='Все категории',
        widget=Select(attrs={'class': 'form-control'}),
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['date_time_creation', 'post_status', 'author__user__username', 'category']





