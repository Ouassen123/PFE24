from django.urls import path, include
from django.contrib import admin
from . import views

# Django Admin header Customization
from .views import SearchView
admin.site.site_header = "Login for admin dashboard"
apps_name = 'mysite'

urlpatterns = [
    path('', views.index, name="index"),
    path("login.html", views.login, name="login"),
    path("register.html", views.register, name="register"),
    path("logout.html", views.logout, name="logout"),
    path("about.html", views.about, name="about"),
    path("job-listings.html", views.job_listings, name="job-listings"),
    path("job-single/<int:id>/", views.job_single, name="job_single"),
    path("post-job.html", views.post_job, name="post-job"),
    path("contact.html", views.contact, name="contact"),
    path("applyjob/<int:id>/", views.applyjob, name="applyjob"),
    path("ranking/<int:id>/", views.ranking, name="ranking"),
    path('search/', SearchView.as_view(), name='search'),
    path('login/', views.LoginAPIView.as_view(), name='login-api'),
    path('api/job_list/', views.JobListAPIView.as_view(), name='api_job_list'),
    path('api/site_stats/', views.SiteStatsAPIView.as_view(), name='site_stats_api'),
    path('api/search-jobs/', views.SearchJobsAPIView.as_view(), name='search-jobs'),
    path('signup/', views.SignupAPIView.as_view(), name='signup'),
    path('post_job_api/', views.post_job_api, name='post_job_api'),
    path('api/apply/', views.job_application_api, name='job_application_api'),
    path('api/job_rank/<int:job_id>/', views.job_rank_api, name='job_rank_api'),
    path('send_contact_email/', views.send_contact_email, name='send_contact_email'),

]
