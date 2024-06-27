from django.urls import path
from . import views


app_name = 'profdevhub'

urlpatterns = [
    path('', views.index, name='index'),
    path('homepage/', views.homepage, name='homepage'),
    path('perfil/', views.perfil, name='perfil'),
    path('contributions/', views.contributions, name='contributions'),
    path('login/', views.login_v, name='login'),
    path('logout/', views.logout_v, name='logout'),
    path('reset_password_1/', views.reset_password_email, name='reset_password1'),
    path('reset_password_2/', views.reset_password, name='reset_password2'),
    path('registo/details_1/', views.registo, name='registo1'),
    path('registo/confirmacao/', views.confirmar_email, name='confirmar_email'),
    path('registo/details_2/', views.registo_details, name='resgito2'),
    path('resgito/documentos/', views.up_documentos, name='up_documentos'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>', views.page_course, name='page_courses'),
    path('courses/perguntas/<int:exercicios_id>', views.page_exercicios, name='exercicios'),
    path('resources/', views.resources, name='resources'),
    path('forum/', views.forum, name='forum'),
    path('forum/<int:forum_id>', views.page_forum, name='page_forum'),
    path('workshops_webinars/', views.workshops_webinars, name='workshops_webinars'),
    path('workshops_webinars/<int:workshop_id>', views.page_workshops_webinars, name='page_workshops_webinars'),
]
