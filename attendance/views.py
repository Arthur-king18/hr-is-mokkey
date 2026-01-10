from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Attendance, User


@login_required
def dashboard(request):
    """Главная страница с информацией о посещаемости"""
    current_time = timezone.now()

    if request.user.role == 'admin':
        # Администраторы видят всех
        current_attendances = Attendance.objects.filter(is_present=True).select_related('user')
        recent_attendances = Attendance.objects.all().select_related('user')[:10]
        show_other_users = True
    else:
        # Работники видят только себя
        current_attendances = Attendance.objects.filter(
            user=request.user,
            is_present=True
        ).select_related('user')
        recent_attendances = Attendance.objects.filter(
            user=request.user
        ).select_related('user')[:10]
        show_other_users = False

    context = {
        'current_attendances': current_attendances,
        'recent_attendances': recent_attendances,
        'current_time': current_time,
        'user_role': request.user.role,
        'show_other_users': show_other_users,
    }
    return render(request, 'attendance/dashboard.html', context)


@login_required
def check_in_out(request):
    """Отметка прихода/ухода"""
    if request.user.role != 'worker':
        messages.error(request, 'Только работники могут отмечать посещаемость')
        return redirect('dashboard')

    # Проверяем текущее состояние
    current_attendance = Attendance.objects.filter(
        user=request.user,
        is_present=True
    ).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'check_in' and not current_attendance:
            # Приход на работу
            Attendance.objects.create(
                user=request.user,
                check_in=timezone.now(),
                is_present=True
            )
            messages.success(request, 'Вы отметили приход на работу')

        elif action == 'check_out' and current_attendance:
            # Уход с работы
            current_attendance.check_out = timezone.now()
            current_attendance.is_present = False
            current_attendance.save()
            messages.success(request, 'Вы отметили уход с работы')

        else:
            messages.error(request, 'Неверное действие')

    return redirect('dashboard')


@login_required
def user_detail(request, user_id):
    """Детальная информация о пользователе (только для админов)"""
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('dashboard')

    user = get_object_or_404(User, id=user_id)

    # Получаем все записи посещаемости пользователя
    attendances = Attendance.objects.filter(user=user).order_by('-check_in')

    # Статистика за текущий месяц
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_attendances = attendances.filter(check_in__gte=start_of_month)

    total_hours = sum(att.get_work_duration() or 0 for att in month_attendances)
    total_days = month_attendances.count()

    context = {
        'selected_user': user,
        'attendances': attendances,
        'total_hours': round(total_hours, 2),
        'total_days': total_days,
        'user_role': request.user.role,
    }
    return render(request, 'attendance/user_detail.html', context)


@login_required
def reports(request):
    """Отчеты (только для админов)"""
    if request.user.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('dashboard')

    # Фильтры
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user_id')

    attendances = Attendance.objects.select_related('user')

    if start_date:
        attendances = attendances.filter(check_in__date__gte=start_date)
    if end_date:
        attendances = attendances.filter(check_in__date__lte=end_date)
    if user_id:
        attendances = attendances.filter(user_id=user_id)

    # Группировка по пользователям
    users_stats = {}
    for attendance in attendances:
        user_id = attendance.user.id
        if user_id not in users_stats:
            users_stats[user_id] = {
                'user': attendance.user,
                'total_hours': 0,
                'total_days': 0,
                'attendances': []
            }
        users_stats[user_id]['attendances'].append(attendance)
        users_stats[user_id]['total_days'] += 1
        if attendance.get_work_duration():
            users_stats[user_id]['total_hours'] += attendance.get_work_duration()

    users = User.objects.filter(role='worker')

    context = {
        'users_stats': list(users_stats.values()),
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
        'user_role': request.user.role,
    }
    return render(request, 'attendance/reports.html', context)