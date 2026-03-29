from django.urls import path
from . import views

urlpatterns = [
    # Student - Team Management
    path('create/', views.create_team, name='create-team'),
    path('list/', views.list_teams, name='list-teams'),
    path('my-teams/', views.my_teams, name='my-teams'),
    path('<int:pk>/', views.team_detail, name='team-detail'),
    
    # Student - Invitations
    path('<int:team_id>/invite/', views.send_invitation, name='send-invitation'),
    path('invitations/', views.my_invitations, name='my-invitations'),
    path('invitations/<int:invitation_id>/respond/', views.respond_invitation, name='respond-invitation'),
    
    # Admin - Assign Mentor
    path('<int:team_id>/assign-mentor/', views.assign_mentor, name='assign-mentor'),
    
    # Faculty - Mentored Teams
    path('mentored/', views.mentored_teams, name='mentored-teams'),
]