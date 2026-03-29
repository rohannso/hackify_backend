from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Team, TeamInvitation
from .serializers import (
    TeamSerializer, 
    TeamCreateSerializer,
    TeamInvitationSerializer,
    AssignMentorSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

# ============ STUDENT: Team Management ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_team(request):
    if request.user.role != 'student':
        return Response({'error': 'Only students can create teams'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = TeamCreateSerializer(data=request.data)
    if serializer.is_valid():
        team = serializer.save(created_by=request.user)
        team.members.add(request.user)
        return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_teams(request):
    teams = Team.objects.all()
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_teams(request):
    if request.user.role != 'student':
        return Response({'error': 'Only for students'}, status=status.HTTP_403_FORBIDDEN)
    
    teams = request.user.teams.all()
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_detail(request, pk):
    try:
        team = Team.objects.get(pk=pk)
        serializer = TeamSerializer(team)
        return Response(serializer.data)
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

# ============ STUDENT: Team Invitations ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invitation(request, team_id):
    if request.user.role != 'student':
        return Response({'error': 'Only students can send invitations'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is team member
    if request.user not in team.members.all():
        return Response({'error': 'You are not a member of this team'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Check if team is full
    if team.is_full:
        return Response({'error': 'Team is full'}, status=status.HTTP_400_BAD_REQUEST)
    
    invited_user_id = request.data.get('invited_user_id')
    try:
        invited_user = User.objects.get(pk=invited_user_id, role='student')
    except User.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if already invited
    if TeamInvitation.objects.filter(team=team, invited_user=invited_user, 
                                    status='pending').exists():
        return Response({'error': 'Invitation already sent'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    invitation = TeamInvitation.objects.create(
        team=team,
        invited_user=invited_user,
        invited_by=request.user
    )
    serializer = TeamInvitationSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_invitations(request):
    if request.user.role != 'student':
        return Response({'error': 'Only for students'}, status=status.HTTP_403_FORBIDDEN)
    
    invitations = TeamInvitation.objects.filter(invited_user=request.user, status='pending')
    serializer = TeamInvitationSerializer(invitations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_invitation(request, invitation_id):
    if request.user.role != 'student':
        return Response({'error': 'Only students can respond'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        invitation = TeamInvitation.objects.get(pk=invitation_id, invited_user=request.user)
    except TeamInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')  # 'accept' or 'reject'
    
    if action == 'accept':
        if invitation.team.is_full:
            return Response({'error': 'Team is full'}, status=status.HTTP_400_BAD_REQUEST)
        
        invitation.status = 'accepted'
        invitation.save()
        invitation.team.members.add(request.user)
        return Response({'message': 'Invitation accepted'})
    
    elif action == 'reject':
        invitation.status = 'rejected'
        invitation.save()
        return Response({'message': 'Invitation rejected'})
    
    return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

# ============ ADMIN: Assign Mentor ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_mentor(request, team_id):
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can assign mentors'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AssignMentorSerializer(data=request.data)
    if serializer.is_valid():
        mentor_id = serializer.validated_data['mentor_id']
        try:
            mentor = User.objects.get(pk=mentor_id, role='faculty')
            team.mentor = mentor
            team.save()
            return Response({'message': f'Mentor {mentor.name} assigned to team {team.name}'})
        except User.DoesNotExist:
            return Response({'error': 'Faculty not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============ FACULTY: View Mentored Teams ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mentored_teams(request):
    if request.user.role != 'faculty':
        return Response({'error': 'Only for faculty'}, status=status.HTTP_403_FORBIDDEN)
    
    teams = Team.objects.filter(mentor=request.user)
    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data)