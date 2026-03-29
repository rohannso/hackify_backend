from django.contrib import admin
from .models import Hackathon, Submission, Feedback

@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ('title', 'week_number', 'status', 'start_date', 'end_date', 'created_by')
    list_filter = ('status', 'week_number')
    search_fields = ('title', 'description')
    ordering = ('-week_number',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'hackathon', 'team', 'status', 'submitted_at')
    list_filter = ('status', 'hackathon')
    search_fields = ('student__name', 'student__email')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'mentor', 'rating', 'created_at')
    list_filter = ('rating',)