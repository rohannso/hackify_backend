from rest_framework import serializers
from .models import Hackathon, Submission, Feedback
from django.contrib.auth import get_user_model

User = get_user_model()

class HackathonSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Hackathon
        fields = [
            'id', 'title', 'description', 'problem_statement',
            'start_date', 'end_date', 'week_number', 'status',
            'created_by', 'created_by_name', 'submission_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    hackathon_title = serializers.CharField(source='hackathon.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'hackathon', 'hackathon_title', 'student', 'student_name',
            'team', 'team_name', 'solution_description', 'github_link',
            'demo_link', 'status', 'submitted_at'
        ]
        read_only_fields = ['student', 'status']

class FeedbackSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'submission', 'mentor', 'mentor_name',
            'comments', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['mentor']

class SubmissionDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'hackathon', 'student', 'student_name', 'team', 'team_name',
            'solution_description', 'github_link', 'demo_link',
            'status', 'submitted_at', 'feedbacks'
        ]