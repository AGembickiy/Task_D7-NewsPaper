from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Post

class Command(BaseCommand):
    help = 'Создает группы common и authors с необходимыми правами'

    def handle(self, *args, **options):
        # Создаем группу common
        common_group, created = Group.objects.get_or_create(name='common')
        
        # Создаем группу authors
        authors_group, created = Group.objects.get_or_create(name='authors')
        
        # Получаем все разрешения для модели Post
        content_type = ContentType.objects.get_for_model(Post)
        post_permissions = Permission.objects.filter(content_type=content_type)
        
        # Добавляем все разрешения для модели Post в группу authors
        authors_group.permissions.set(post_permissions)
        
        self.stdout.write(self.style.SUCCESS('Группы успешно созданы')) 