from django.contrib import admin
from .models import Team, TeamInvitation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'mentor', 'member_count', 'max_members', 'created_at')
    search_fields = ('name', 'created_by__name')
    filter_horizontal = ('members',)

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'invited_user', 'invited_by', 'status', 'created_at')
    list_filter = ('status',)