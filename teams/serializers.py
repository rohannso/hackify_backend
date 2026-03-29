from rest_framework import serializers
from .models import Team, TeamInvitation
from django.contrib.auth import get_user_model

User = get_user_model()

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']

class TeamSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)
    members_detail = TeamMemberSerializer(source='members', many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_name',
            'members', 'members_detail', 'mentor', 'mentor_name',
            'max_members', 'member_count', 'is_full', 'created_at'
        ]
        read_only_fields = ['created_by']

class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description', 'max_members']

class TeamInvitationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    invited_user_name = serializers.CharField(source='invited_user.name', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.name', read_only=True)
    
    class Meta:
        model = TeamInvitation
        fields = [
            'id', 'team', 'team_name', 'invited_user', 'invited_user_name',
            'invited_by', 'invited_by_name', 'status', 'created_at'
        ]
        read_only_fields = ['invited_by', 'status']

class AssignMentorSerializer(serializers.Serializer):
    mentor_id = serializers.IntegerField()