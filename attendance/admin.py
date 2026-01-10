from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Attendance


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'role', 'position', 'is_active')
    list_filter = ('role', 'is_active', 'position')
    search_fields = ('username', 'full_name', 'position')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'full_name', 'position')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'full_name', 'position')
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'check_in', 'check_out', 'get_work_duration', 'status')
    list_filter = ('check_in', 'is_present', 'user')
    search_fields = ('user__full_name', 'user__username')
    ordering = ('-check_in',)

    def get_work_duration(self, obj):
        return obj.get_work_duration()
    get_work_duration.short_description = 'Часы работы'
