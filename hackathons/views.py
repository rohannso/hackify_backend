from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Hackathon, Submission, Feedback
from .serializers import (
    HackathonSerializer, 
    SubmissionSerializer,
    SubmissionDetailSerializer,
    FeedbackSerializer
)

# ============ ADMIN: Hackathon Management ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_hackathon(request):
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can create hackathons'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    serializer = HackathonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_hackathons(request):
    hackathons = Hackathon.objects.all()
    serializer = HackathonSerializer(hackathons, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def hackathon_detail(request, pk):
    try:
        hackathon = Hackathon.objects.get(pk=pk)
    except Hackathon.DoesNotExist:
        return Response({'error': 'Hackathon not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = HackathonSerializer(hackathon)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = HackathonSerializer(hackathon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        hackathon.delete()
        return Response({'message': 'Hackathon deleted'}, status=status.HTTP_204_NO_CONTENT)

# ============ STUDENT: Submission ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_solution(request, hackathon_id):
    if request.user.role != 'student':
        return Response({'error': 'Only students can submit'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        hackathon = Hackathon.objects.get(pk=hackathon_id)
    except Hackathon.DoesNotExist:
        return Response({'error': 'Hackathon not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubmissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(student=request.user, hackathon=hackathon)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_submissions(request):
    if request.user.role != 'student':
        return Response({'error': 'Only for students'}, status=status.HTTP_403_FORBIDDEN)
    
    submissions = Submission.objects.filter(student=request.user)
    serializer = SubmissionDetailSerializer(submissions, many=True)
    return Response(serializer.data)

# ============ FACULTY: Review & Feedback ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mentor_submissions(request):
    if request.user.role != 'faculty':
        return Response({'error': 'Only for faculty'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get submissions from teams mentored by this faculty
    submissions = Submission.objects.filter(team__mentor=request.user)
    serializer = SubmissionDetailSerializer(submissions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def provide_feedback(request, submission_id):
    if request.user.role != 'faculty':
        return Response({'error': 'Only faculty can provide feedback'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        submission = Submission.objects.get(pk=submission_id)
    except Submission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(mentor=request.user, submission=submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_submission_status(request, submission_id):
    if request.user.role != 'faculty':
        return Response({'error': 'Only faculty can update status'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        submission = Submission.objects.get(pk=submission_id)
    except Submission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status in ['approved', 'rejected', 'pending']:
        submission.status = new_status
        submission.save()
        return Response({'message': f'Status updated to {new_status}'})
    return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)