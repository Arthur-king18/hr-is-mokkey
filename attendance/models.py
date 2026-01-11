from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('worker', 'Работник'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='worker',
        verbose_name='Роль'
    )
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    position = models.CharField(max_length=100, verbose_name='Должность')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.full_name} ({self.username})"


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Работник')
    check_in = models.DateTimeField(verbose_name='Время прихода')
    check_out = models.DateTimeField(null=True, blank=True, verbose_name='Время ухода')
    is_present = models.BooleanField(default=True, verbose_name='На работе')

    class Meta:
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        ordering = ['-check_in']

    def __str__(self):
        return f"{self.user.full_name} - {self.check_in.date()}"

    def get_work_duration(self):
        """Возвращает продолжительность работы в часах"""
        if self.check_out:
            duration = self.check_out - self.check_in
            return round(duration.total_seconds() / 3600, 2)
        return None

    @property
    def status(self):
        """Статус текущего посещения"""
        if self.is_present:
            return "На работе"
        return "Ушел"
