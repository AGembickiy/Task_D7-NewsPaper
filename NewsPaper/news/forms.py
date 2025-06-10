from django.forms import ModelForm, TextInput, Textarea, HiddenInput, CharField
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from .models import Post, Category, Author
from django import forms

class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user

class PostForm(ModelForm):
    category_input = CharField(
        required=True,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите категории через запятую'
        }),
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['author', 'post_status', 'heading', 'text_post']
        widgets = {
            'author': HiddenInput(),
            'text_post': Textarea(attrs={'cols': 150, 'rows': 10, 'class': 'form-control'}),
            'post_status': forms.Select(attrs={'class': 'form-control'}),
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'post_status': 'Тип публикации',
            'heading': 'Заголовок',
            'text_post': 'Текст публикации',
        }

    def clean(self):
        cleaned_data = super().clean()
        category_names = cleaned_data.get('category_input', '').strip()
        
        if not category_names:
            raise forms.ValidationError('Введите хотя бы одну категорию')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Очищаем существующие категории
            instance.category.clear()
            
            # Обработка введенных категорий
            category_names = self.cleaned_data.get('category_input', '').strip()
            if category_names:
                for name in category_names.split(','):
                    name = name.strip()
                    if name:
                        try:
                            category, created = Category.objects.get_or_create(topic=name)
                            instance.category.add(category)
                        except Exception as e:
                            print(f"Error creating category {name}: {e}")
            
            self.save_m2m()
        
        return instance



