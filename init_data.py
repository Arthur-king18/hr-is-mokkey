#!/usr/bin/env python
"""
Скрипт для инициализации тестовых данных
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import User, Attendance

def create_test_data():
    # Создаем админа
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'full_name': 'Администратор Системы',
            'position': 'Администратор',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("Создан администратор: admin/admin123")

    # Создаем тестовых работников
    workers_data = [
        {'username': 'ivanov', 'full_name': 'Иванов Иван Иванович', 'position': 'Бригадир'},
        {'username': 'petrov', 'full_name': 'Петров Петр Петрович', 'position': 'Рабочий'},
        {'username': 'sidorov', 'full_name': 'Сидоров Сидор Сидорович', 'position': 'Технолог'},
        {'username': 'smirnov', 'full_name': 'Смирнов Алексей Викторович', 'position': 'Лаборант'},
    ]

    for worker_data in workers_data:
        worker, created = User.objects.get_or_create(
            username=worker_data['username'],
            defaults={
                'full_name': worker_data['full_name'],
                'position': worker_data['position'],
                'role': 'worker'
            }
        )
        if created:
            worker.set_password('worker123')
            worker.save()
            print(f"Создан работник: {worker_data['username']}/worker123")

    # Создаем тестовые записи посещаемости
    workers = User.objects.filter(role='worker')
    import random
    from django.utils import timezone

    for i in range(30):  # За последние 30 дней
        date = timezone.now().date() - timedelta(days=i)
        for worker in workers:
            # Случайно пропускаем некоторые дни (прогулы)
            if random.random() < 0.1:  # 10% шанс прогула
                continue

            # Случайное время прихода (8:00-9:30)
            check_in_hour = random.randint(8, 9)
            check_in_minute = random.randint(0, 59) if check_in_hour == 8 else random.randint(0, 30)
            check_in = datetime.combine(date, datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute))

            # Случайное время ухода (17:00-19:00)
            check_out_hour = random.randint(17, 19)
            check_out_minute = random.randint(0, 59)
            check_out = datetime.combine(date, datetime.min.time().replace(hour=check_out_hour, minute=check_out_minute))

            # Для сегодняшнего дня - может быть еще на работе
            is_present = False
            if date == timezone.now().date() and random.random() < 0.3:  # 30% шанс быть на работе сегодня
                check_out = None
                is_present = True

            Attendance.objects.get_or_create(
                user=worker,
                check_in=check_in,
                defaults={
                    'check_out': check_out,
                    'is_present': is_present
                }
            )

    print("Тестовые данные созданы успешно!")

if __name__ == '__main__':
    create_test_data()