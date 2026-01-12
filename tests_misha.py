from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from attendance.models import Attendance
from attendance.forms import CustomUserCreationForm, CustomAuthenticationForm
from attendance.admin import CustomUserAdmin, AttendanceAdmin

User = get_user_model()


class MishaFormsTest(TestCase):

    def test_custom_user_creation_form_valid(self):
        """Тест валидной формы создания пользователя"""
        form_data = {
            'username': 'testuser',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'full_name': 'Тестовый Пользователь',
            'position': 'Тестировщик',
            'role': 'worker'
        }

        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Создаем пользователя через форму
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.full_name, 'Тестовый Пользователь')
        self.assertEqual(user.position, 'Тестировщик')
        self.assertEqual(user.role, 'worker')

    def test_custom_user_creation_form_invalid(self):
        """Тест невалидной формы создания пользователя"""
        form_data = {
            'username': 'testuser',
            'password1': 'pass1',
            'password2': 'pass2',  # пароли не совпадают
            'full_name': '',
            'position': '',
            'role': 'worker'
        }

        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Проверяем ошибки
        self.assertIn('password2', form.errors)
        self.assertIn('full_name', form.errors)

    def test_custom_user_creation_form_missing_fields(self):
        """Тест формы с отсутствующими обязательными полями"""
        form_data = {
            'username': 'testuser',
            # отсутствуют password1, password2, full_name, position, role
        }

        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Проверяем что есть ошибки для обязательных полей
        required_fields = ['password1', 'password2', 'full_name', 'position', 'role']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_custom_authentication_form_valid(self):
        """Тест валидной формы аутентификации"""
        # Создаем пользователя
        user = User.objects.create_user(
            username='auth_test',
            password='testpass123'
        )

        form_data = {
            'username': 'auth_test',
            'password': 'testpass123'
        }

        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_authentication_form_invalid_credentials(self):
        """Тест формы аутентификации с неверными данными"""
        form_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }

        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_field_attributes(self):
        """Тест атрибутов полей форм"""
        form = CustomUserCreationForm()

        # Проверяем что help_text пустые (как настроено Мишей)
        self.assertEqual(form.fields['username'].help_text, '')
        self.assertEqual(form.fields['full_name'].help_text, '')
        self.assertEqual(form.fields['position'].help_text, '')


class MishaAdminTest(TestCase):
    """Тесты для админ-панели, настроенной Мишей"""

    def setUp(self):
        """Настройка админ-сайта для тестирования"""
        self.site = AdminSite()
        self.user_admin = CustomUserAdmin(User, self.site)
        self.attendance_admin = AttendanceAdmin(Attendance, self.site)

        # Создаем тестовых пользователей
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.test_user = User.objects.create_user(
            username='test_user',
            full_name='Тестовый Пользователь',
            position='Тестировщик',
            role='worker'
        )

    def test_user_admin_list_display(self):
        """Тест отображения полей в списке пользователей"""
        # Проверяем что настроенные поля отображаются
        list_display = self.user_admin.list_display
        expected_fields = ['username', 'full_name', 'role', 'position', 'is_active']

        for field in expected_fields:
            self.assertIn(field, list_display)

    def test_user_admin_list_filter(self):
        """Тест фильтров списка пользователей"""
        list_filter = self.user_admin.list_filter
        expected_filters = ['role', 'is_active', 'position']

        for filter_field in expected_filters:
            self.assertIn(filter_field, list_filter)

    def test_user_admin_search_fields(self):
        """Тест полей поиска пользователей"""
        search_fields = self.user_admin.search_fields
        expected_searches = ['username', 'full_name', 'position']

        for search_field in expected_searches:
            self.assertIn(search_field, search_fields)

    def test_user_admin_fieldsets(self):
        """Тест настройки fieldsets для пользователя"""
        fieldsets = self.user_admin.fieldsets

        # Проверяем что есть дополнительные поля
        additional_fieldset = None
        for fieldset in fieldsets:
            if fieldset[0] == 'Дополнительная информация':
                additional_fieldset = fieldset
                break

        self.assertIsNotNone(additional_fieldset)
        self.assertIn('role', additional_fieldset[1]['fields'])
        self.assertIn('full_name', additional_fieldset[1]['fields'])
        self.assertIn('position', additional_fieldset[1]['fields'])

    def test_attendance_admin_list_display(self):
        """Тест отображения полей в списке посещаемости"""
        list_display = self.attendance_admin.list_display
        expected_fields = ['user', 'check_in', 'check_out', 'get_work_duration', 'status']

        for field in expected_fields:
            self.assertIn(field, list_display)

    def test_attendance_admin_list_filter(self):
        """Тест фильтров списка посещаемости"""
        list_filter = self.attendance_admin.list_filter
        expected_filters = ['check_in', 'is_present', 'user']

        for filter_field in expected_filters:
            self.assertIn(filter_field, list_filter)

    def test_attendance_admin_search_fields(self):
        """Тест полей поиска посещаемости"""
        search_fields = self.attendance_admin.search_fields
        expected_searches = ['user__full_name', 'user__username']

        for search_field in expected_searches:
            self.assertIn(search_field, search_fields)

    def test_attendance_admin_ordering(self):
        """Тест сортировки списка посещаемости"""
        ordering = self.attendance_admin.ordering
        self.assertEqual(ordering, ['-check_in'])

    def test_attendance_admin_work_duration_method(self):
        """Тест метода get_work_duration в админке"""
        # Создаем запись посещаемости
        attendance = Attendance.objects.create(
            user=self.test_user,
            check_in=timezone.now(),
            check_out=timezone.now() + timezone.timedelta(hours=8),
            is_present=False
        )

        # Проверяем работу метода в админке
        duration = self.attendance_admin.get_work_duration(attendance)
        self.assertIsInstance(duration, str)
        self.assertIn('8', duration)  # должно содержать 8 часов

    def test_admin_access_permissions(self):
        """Тест доступа к админ-панели"""
        client = Client()

        # Неавторизованный пользователь
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # редирект на логин

        # Авторизованный админ
        client.login(username='admin', password='admin123')
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_user_management(self):
        """Тест управления пользователями через админку"""
        client = Client()
        client.login(username='admin', password='admin123')

        # Проверяем доступ к списку пользователей
        response = client.get('/admin/attendance/user/')
        self.assertEqual(response.status_code, 200)

        # Проверяем отображение полей
        self.assertContains(response, 'username')
        self.assertContains(response, 'full_name')
        self.assertContains(response, 'role')
        self.assertContains(response, 'position')


class MishaGeneralTests(TestCase):
    """Общие тесты системы, написанные Мишей"""

    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='general_test',
            full_name='Общий Тест',
            position='Тестировщик',
            role='worker'
        )

    def test_user_creation_and_authentication(self):
        """Тест создания пользователя и аутентификации"""
        # Проверяем создание
        self.assertEqual(self.user.username, 'general_test')
        self.assertEqual(self.user.role, 'worker')

        # Проверяем аутентификацию
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(
            username='general_test',
            password=self.user.password  # пароль по умолчанию
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)

    def test_form_integration_with_model(self):
        """Тест интеграции форм с моделью"""
        # Создаем пользователя через форму
        form_data = {
            'username': 'form_integration',
            'password1': 'integration123',
            'password2': 'integration123',
            'full_name': 'Интеграция Форм',
            'position': 'Интегратор',
            'role': 'worker'
        }

        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()

        # Проверяем что данные сохранились в модели
        saved_user = User.objects.get(username='form_integration')
        self.assertEqual(saved_user.full_name, 'Интеграция Форм')
        self.assertEqual(saved_user.position, 'Интегратор')
        self.assertEqual(saved_user.role, 'worker')

    def test_admin_functionality_complete_flow(self):
        """Тест полного цикла работы админки"""
        client = Client()

        # Создаем админа
        admin = User.objects.create_superuser(
            username='flow_admin',
            email='flow@test.com',
            password='flow123'
        )

        # Входим в админку
        client.login(username='flow_admin', password='flow123')

        # Проверяем доступ к главной админки
        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)

        # Проверяем доступ к пользователям
        response = client.get('/admin/attendance/user/')
        self.assertEqual(response.status_code, 200)

        # Проверяем доступ к записям посещаемости
        response = client.get('/admin/attendance/attendance/')
        self.assertEqual(response.status_code, 200)

    def test_security_form_validation(self):
        """Тест безопасности валидации форм"""
        # Пытаемся создать пользователя с небезопасными данными
        dangerous_data = {
            'username': '<script>alert("xss")</script>',
            'password1': 'pass',
            'password2': 'pass',
            'full_name': 'Имя',
            'position': 'Должность',
            'role': 'worker'
        }

        form = CustomUserCreationForm(data=dangerous_data)

        # Даже если форма валидна, данные должны быть экранированы в шаблонах
        # Проверяем что форма требует нормальные пароли
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)  # слишком короткий пароль

    def test_admin_bulk_operations(self):
        """Тест массовых операций в админке"""
        client = Client()

        # Создаем админа и тестовых пользователей
        admin = User.objects.create_superuser(
            username='bulk_admin',
            email='bulk@test.com',
            password='bulk123'
        )

        # Создаем несколько пользователей для тестирования
        for i in range(3):
            User.objects.create_user(
                username=f'bulk_user_{i}',
                full_name=f'Массовый Пользователь {i}',
                position='Работник',
                role='worker'
            )

        client.login(username='bulk_admin', password='bulk123')

        # Проверяем что все пользователи отображаются в списке
        response = client.get('/admin/attendance/user/')
        self.assertEqual(response.status_code, 200)

        # Проверяем отображение нескольких пользователей
        for i in range(3):
            self.assertContains(response, f'bulk_user_{i}')

    def test_form_field_customization(self):
        """Тест кастомизации полей форм"""
        form = CustomUserCreationForm()

        # Проверяем что поля имеют правильные виджеты
        username_field = form.fields['username']
        full_name_field = form.fields['full_name']
        position_field = form.fields['position']
        role_field = form.fields['role']

        # Проверяем что поля существуют
        self.assertIsNotNone(username_field)
        self.assertIsNotNone(full_name_field)
        self.assertIsNotNone(position_field)
        self.assertIsNotNone(role_field)

        # Проверяем choices для поля role
        expected_choices = [
            ('admin', 'Администратор'),
            ('worker', 'Работник')
        ]
        self.assertEqual(role_field.choices, expected_choices)
