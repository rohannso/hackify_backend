from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, StudentProfile, FacultyProfile

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'role', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.register(OTP)
admin.site.register(StudentProfile)
admin.site.register(FacultyProfile)