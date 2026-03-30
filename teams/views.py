from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Team, TeamInvitation
from .serializers import (
    TeamSerializer, 
    TeamCreateSerializer,
    TeamInvitationSerializer,
    AssignMentorSerializer,
    SendInvitationSerializer
)
from django.contrib.auth import get_user_model
from .utils import send_team_invitation_email


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
    
    # Validate email input
    serializer = SendInvitationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Find user by email
    try:
        invited_user = User.objects.get(email=email, role='student')
    except User.DoesNotExist:
        return Response({'error': 'Student with this email not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is already a member
    if invited_user in team.members.all():
        return Response({'error': 'User is already a team member'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already invited
    if TeamInvitation.objects.filter(team=team, invited_user=invited_user, 
                                    status='pending').exists():
        return Response({'error': 'Invitation already sent to this email'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Create invitation
    invitation = TeamInvitation.objects.create(
        team=team,
        invited_user=invited_user,
        invited_by=request.user
    )
    
    # Send email notification
    try:
        send_team_invitation_email(invitation)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to send invitation email: {str(e)}")
    
    serializer = TeamInvitationSerializer(invitation)
    return Response({
        'message': f'Invitation sent to {email}',
        'invitation': serializer.data
    }, status=status.HTTP_201_CREATED)

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
        email = serializer.validated_data['email']
        try:
            mentor = User.objects.get(email=email, role='faculty', is_verified=True)
            team.mentor = mentor
            team.save()
            return Response({
                'message': f'Mentor {mentor.name} assigned to team {team.name}',
                'mentor': {
                    'id': mentor.id,
                    'name': mentor.name,
                    'email': mentor.email
                }
            })
        except User.DoesNotExist:
            return Response({'error': 'Faculty with this email not found'}, 
                           status=status.HTTP_404_NOT_FOUND)
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