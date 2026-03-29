from django.urls import path
from . import views

urlpatterns = [
    # Admin - Hackathon Management
    path('create/', views.create_hackathon, name='create-hackathon'),
    path('list/', views.list_hackathons, name='list-hackathons'),
    path('<int:pk>/', views.hackathon_detail, name='hackathon-detail'),
    
    # Student - Submissions
    path('<int:hackathon_id>/submit/', views.submit_solution, name='submit-solution'),
    path('my-submissions/', views.my_submissions, name='my-submissions'),
    
    # Faculty - Review & Feedback
    path('mentor/submissions/', views.mentor_submissions, name='mentor-submissions'),
    path('submission/<int:submission_id>/feedback/', views.provide_feedback, name='provide-feedback'),
    path('submission/<int:submission_id>/status/', views.update_submission_status, name='update-submission-status'),
]