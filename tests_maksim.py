from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from attendance.models import Attendance
import datetime

User = get_user_model()


class MaksimModelsTest(TestCase):

    def test_user_model_creation(self):
        """Тест создания пользователя с расширенными полями"""
        user = User.objects.create_user(
            username='maksim_test',
            full_name='Максим Тестовый',
            position='Разработчик',
            role='admin'
        )

        self.assertEqual(user.username, 'maksim_test')
        self.assertEqual(user.full_name, 'Максим Тестовый')
        self.assertEqual(user.position, 'Разработчик')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_active)

    def test_user_model_str_method(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            username='str_test',
            full_name='Тест Строки',
            position='Тестер',
            role='worker'
        )

        expected_str = "Тест Строки (str_test)"
        self.assertEqual(str(user), expected_str)

    def test_user_roles(self):
        """Тест ролей пользователя"""
        admin_user = User.objects.create_user(
            username='admin_role',
            role='admin'
        )
        worker_user = User.objects.create_user(
            username='worker_role',
            role='worker'
        )

        self.assertEqual(admin_user.role, 'admin')
        self.assertEqual(worker_user.role, 'worker')

        # Проверяем verbose_name ролей
        self.assertEqual(admin_user.get_role_display(), 'Администратор')
        self.assertEqual(worker_user.get_role_display(), 'Работник')

    def test_attendance_model_creation(self):
        """Тест создания записи посещаемости"""
        user = User.objects.create_user(username='attendance_user', role='worker')
        check_in_time = timezone.now()

        attendance = Attendance.objects.create(
            user=user,
            check_in=check_in_time,
            is_present=True
        )

        self.assertEqual(attendance.user, user)
        self.assertEqual(attendance.check_in, check_in_time)
        self.assertIsNone(attendance.check_out)
        self.assertTrue(attendance.is_present)

    def test_attendance_model_str_method(self):
        """Тест строкового представления записи посещаемости"""
        user = User.objects.create_user(
            username='str_attendance',
            full_name='Пользователь Строки',
            role='worker'
        )
        today = timezone.now().date()
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )

        expected_str = f"Пользователь Строки - {today}"
        self.assertEqual(str(attendance), expected_str)

    def test_attendance_work_duration_calculation(self):
        """Тест расчета продолжительности работы"""
        user = User.objects.create_user(username='duration_test', role='worker')
        check_in_time = timezone.now()
        check_out_time = check_in_time + datetime.timedelta(hours=8, minutes=30)

        attendance = Attendance.objects.create(
            user=user,
            check_in=check_in_time,
            check_out=check_out_time,
            is_present=False
        )

        duration = attendance.get_work_duration()
        self.assertAlmostEqual(duration, 8.5, places=1)  # 8.5 часов

    def test_attendance_work_duration_without_checkout(self):
        """Тест расчета продолжительности без времени ухода"""
        user = User.objects.create_user(username='no_checkout', role='worker')
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )

        duration = attendance.get_work_duration()
        self.assertIsNone(duration)

    def test_attendance_status_property_present(self):
        """Тест свойства status для присутствующего сотрудника"""
        user = User.objects.create_user(username='status_present', role='worker')
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )

        self.assertEqual(attendance.status, "На работе")

    def test_attendance_status_property_away(self):
        """Тест свойства status для отсутствующего сотрудника"""
        user = User.objects.create_user(username='status_away', role='worker')
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            check_out=timezone.now(),
            is_present=False
        )

        self.assertEqual(attendance.status, "Ушел")

    def test_user_attendance_relationship(self):
        """Тест связи пользователь - записи посещаемости"""
        user = User.objects.create_user(username='relationship_test', role='worker')

        # Создаем несколько записей для пользователя
        attendance1 = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )
        attendance2 = Attendance.objects.create(
            user=user,
            check_in=timezone.now() - datetime.timedelta(days=1),
            check_out=timezone.now() - datetime.timedelta(days=1, hours=-8),
            is_present=False
        )

        # Проверяем связь
        user_attendances = Attendance.objects.filter(user=user)
        self.assertEqual(user_attendances.count(), 2)

        # Проверяем что все записи принадлежат правильному пользователю
        for attendance in user_attendances:
            self.assertEqual(attendance.user, user)

    def test_attendance_model_ordering(self):
        """Тест сортировки записей посещаемости"""
        user = User.objects.create_user(username='ordering_test', role='worker')

        # Создаем записи в разном порядке времени
        old_time = timezone.now() - datetime.timedelta(days=2)
        new_time = timezone.now()

        attendance_old = Attendance.objects.create(
            user=user,
            check_in=old_time,
            is_present=False
        )
        attendance_new = Attendance.objects.create(
            user=user,
            check_in=new_time,
            is_present=True
        )

        # Проверяем порядок сортировки (новые записи должны быть первыми)
        attendances = Attendance.objects.filter(user=user)
        self.assertEqual(attendances.first(), attendance_new)
        self.assertEqual(attendances.last(), attendance_old)

    def test_attendance_foreign_key_constraint(self):
        """Тест ограничений внешнего ключа"""
        user = User.objects.create_user(username='fk_test', role='worker')

        # Создаем запись с существующим пользователем
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )
        self.assertIsNotNone(attendance.id)

        # Проверяем связь
        self.assertEqual(attendance.user, user)

    def test_attendance_model_fields_validation(self):
        """Тест валидации полей модели Attendance"""
        user = User.objects.create_user(username='validation_test', role='worker')

        # Проверяем что обязательные поля требуются
        with self.assertRaises(Exception):  # user is required
            Attendance.objects.create(check_in=timezone.now())

        with self.assertRaises(Exception):  # check_in is required
            Attendance.objects.create(user=user)

        # Проверяем что валидные данные создают запись
        attendance = Attendance.objects.create(
            user=user,
            check_in=timezone.now(),
            is_present=True
        )
        self.assertIsNotNone(attendance.id)

    def test_user_model_fields_validation(self):
        """Тест валидации полей модели User"""
        # Проверяем создание пользователя с минимальными данными
        user = User.objects.create_user(username='minimal_user')
        self.assertIsNotNone(user.id)
        self.assertEqual(user.role, 'worker')  # default role

        # Проверяем что username уникален
        with self.assertRaises(Exception):
            User.objects.create_user(username='minimal_user')  # duplicate username

    def test_attendance_multiple_records_per_user(self):
        """Тест создания нескольких записей для одного пользователя"""
        user = User.objects.create_user(username='multi_record', role='worker')

        # Создаем несколько записей для разных дней
        for i in range(5):
            check_in_time = timezone.now() - datetime.timedelta(days=i)
            Attendance.objects.create(
                user=user,
                check_in=check_in_time,
                check_out=check_in_time + datetime.timedelta(hours=8),
                is_present=False
            )

        # Проверяем количество записей
        user_records = Attendance.objects.filter(user=user)
        self.assertEqual(user_records.count(), 5)

    def test_attendance_different_users_isolation(self):
        """Тест изоляции данных между разными пользователями"""
        user1 = User.objects.create_user(username='user1', role='worker')
        user2 = User.objects.create_user(username='user2', role='worker')

        # Создаем записи для каждого пользователя
        Attendance.objects.create(user=user1, check_in=timezone.now(), is_present=True)
        Attendance.objects.create(user=user2, check_in=timezone.now(), is_present=True)

        # Проверяем что записи изолированы
        user1_records = Attendance.objects.filter(user=user1)
        user2_records = Attendance.objects.filter(user=user2)

        self.assertEqual(user1_records.count(), 1)
        self.assertEqual(user2_records.count(), 1)
        self.assertNotEqual(user1_records.first().user, user2_records.first().user)
