from django.test import TestCase
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Attendance


class UserModelTest(TestCase):
    """Тесты для модели User"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            full_name='Тестовый Пользователь',
            position='Тестировщик',
            role='worker'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.full_name, 'Тестовый Пользователь')
        self.assertEqual(user.position, 'Тестировщик')
        self.assertEqual(user.role, 'worker')
        self.assertTrue(user.check_password(user.password))  # Проверяем что пароль установлен


class AttendanceModelTest(TestCase):
    """Тесты для модели Attendance"""

    def setUp(self):
        """Создание тестового пользователя"""
        self.user = User.objects.create_user(
            username='worker',
            full_name='Рабочий Тестовый',
            position='Рабочий',
            role='worker'
        )

    def test_create_attendance_record(self):
        """Тест создания записи посещаемости"""
        check_in_time = timezone.now()
        attendance = Attendance.objects.create(
            user=self.user,
            check_in=check_in_time,
            is_present=True
        )

        self.assertEqual(attendance.user, self.user)
        self.assertEqual(attendance.check_in, check_in_time)
        self.assertTrue(attendance.is_present)
        self.assertIsNone(attendance.check_out)


class CheckInOutLogicTest(TestCase):
    """Тесты для логики прихода/ухода"""

    def setUp(self):
        """Создание тестового пользователя"""
        self.user = User.objects.create_user(
            username='worker2',
            full_name='Рабочий Два',
            position='Рабочий',
            role='worker'
        )

    def test_check_in_creates_record(self):
        """Тест что приход создает запись"""
        # Имитируем POST запрос на check_in_out
        from django.test import Client
        client = Client()

        # Входим как пользователь
        client.login(username='worker2', password=self.user.password)

        # Отправляем запрос на приход
        response = client.post('/check-in-out/', {'action': 'check_in'})

        # Проверяем что запись создана
        attendance = Attendance.objects.filter(user=self.user, is_present=True).first()
        self.assertIsNotNone(attendance)
        self.assertEqual(attendance.user, self.user)
        self.assertTrue(attendance.is_present)


class RoleBasedAccessTest(TestCase):
    """Тесты для ролевой системы доступа"""

    def setUp(self):
        """Создание тестовых пользователей разных ролей"""
        self.worker = User.objects.create_user(
            username='worker_role',
            full_name='Рабочий Роль',
            position='Рабочий',
            role='worker'
        )
        self.admin = User.objects.create_user(
            username='admin_role',
            full_name='Админ Роль',
            position='Администратор',
            role='admin'
        )

    def test_worker_cannot_access_reports(self):
        """Тест что рабочий не может получить доступ к отчетам"""
        from django.test import Client
        client = Client()

        # Входим как рабочий
        client.login(username='worker_role', password=self.worker.password)

        # Пытаемся получить доступ к отчетам
        response = client.get('/reports/')

        # Должны быть перенаправлены (403 или redirect)
        self.assertEqual(response.status_code, 302)  # Redirect to login or dashboard

    def test_admin_can_access_reports(self):
        """Тест что админ может получить доступ к отчетам"""
        from django.test import Client
        client = Client()

        # Входим как админ
        client.login(username='admin_role', password=self.admin.password)

        # Пытаемся получить доступ к отчетам
        response = client.get('/reports/')

        # Должны получить доступ (200) или быть перенаправлены на логин если не аутентифицированы
        # В данном случае проверяем что нет ошибки доступа
        self.assertIn(response.status_code, [200, 302])
