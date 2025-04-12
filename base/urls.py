from django.urls import path
from . import views



urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/complete/', views.profile_complete, name='profile_complete'),
    # Location APIs
    path('update-location/', views.update_location, name='update_location'),
    path('location-history/<int:pk>/', views.location_history, name='location_history'),
    
    # Geofencing
    path('geofence-violations/', views.geofence_violations, name='geofence_violations'),
    path('intern/<int:intern_id>/geofence-violations/', views.geofence_violations, name='intern_geofence_violations'),

    
    # Intern Management
    path('interns/', views.intern_list, name='intern_list'),
    path('interns/<int:pk>/', views.intern_detail, name='intern_detail'),
    path('organization/', views.edit_organization, name='edit_organization'),


    # otp
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('otp-success/', views.otp_success, name='otp_success'),
]