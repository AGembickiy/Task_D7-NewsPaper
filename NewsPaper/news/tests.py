from django.test import TestCase
import logging

# Получаем логгеры
django_logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')
server_logger = logging.getLogger('django.server')
template_logger = logging.getLogger('django.template')
db_logger = logging.getLogger('django.db.backends')
security_logger = logging.getLogger('django.security')

class LoggingTest(TestCase):
    def test_logging(self):
        # Тестируем основной логгер django
        django_logger.debug('Debug message from django logger')
        django_logger.info('Info message from django logger')
        django_logger.warning('Warning message from django logger')
        django_logger.error('Error message from django logger')
        django_logger.critical('Critical message from django logger')

        # Тестируем логгер запросов
        request_logger.error('Error in request processing')

        # Тестируем логгер сервера
        server_logger.error('Server error occurred')

        # Тестируем логгер шаблонов
        template_logger.error('Template error occurred')

        # Тестируем логгер базы данных
        db_logger.error('Database error occurred')

        # Тестируем логгер безопасности
        security_logger.info('Security event occurred')
        security_logger.warning('Security warning occurred')
        security_logger.error('Security error occurred')
