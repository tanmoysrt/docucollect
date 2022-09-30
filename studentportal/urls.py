from django.urls import path, include
from . import views


urlpatterns = [
    path("login/", views.login_page, name="student_login_page"),
    path("register/", views.register_page, name="student_register_page"),
    path("forget-password/", views.forget_password_page, name="student_forget_password_page"),
    path("", views.dashboard_page, name="student_dashboard_page"),
    path("profile/", views.profile_page, name="student_profile_page"),
    # List pages
    path("list/internship", views.internship_list_page, name="student_internship_list_page"),
    path("list/placement", views.placement_list_page, name="student_placement_list_page"),
    path("list/hackathon", views.hackathon_list_page, name="student_hackathon_list_page"),
    path("list/course", views.online_course_list_page, name="student_online_course_list_page"),
    # Add pages
    path("add/internship", views.add_internship_page, name="student_internship_add_page"),
    path("add/placement", views.add_placement_page, name="student_placement_add_page"),
    path("add/hackathon", views.add_hackathon_page, name="student_hackathon_add_page"),
    path("add/course", views.add_online_course_page, name="student_online_course_add_page"),

    path("download/", views.download_file),
    path("delete/", views.delete_record),

    path("report/generate/", views.generate_report),
    path("report/download/", views.download_report),

    path("backup/generate/", views.generate_backup),
    path("backup/download/", views.download_backup),  
]
