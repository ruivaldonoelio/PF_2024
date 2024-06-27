from django.shortcuts import render, redirect, get_object_or_404
from .form import RegistroUsuarioForm, UserDetailsForm, PasswordResetForm, EmailLoginForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import smtplib
from email.mime.text import MIMEText
import random
from environ import Env

env = Env()


def index(request):
    return render(request, "main.html")


@login_required
def homepage(request):
    return render(request, "home.html")


@login_required
def perfil(request):
    return render(request, "profile.html")


@login_required
def contributions(request):
    return render(request, "mypage.html")


@login_required
def courses(request):
    cursos = Courses.objects.all()
    return render(request, "courses.html", {"cursos": cursos})


@login_required
def forum(request):
    return render(request, "forum.html")


@login_required
def resources(request):
    recursos = Recursos.objects.all()
    return render(request, "resource.html", {"recursos": recursos})


@login_required
def workshops_webinars(request):
    workshop = Workshop.objects.all()
    return render(request, "workshops.html", {"workshop": workshop})


def page_forum(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    mensagem = forum.mensagens.all().order_by('data')
    return render(request, "page_forum.html", {'forum': forum, 'mensagens': mensagem})


def page_course(request, course_id):
    curso = get_object_or_404(Courses, id=course_id)
    exercicio = curso.exercicios.all()
    return render(request, "page_course.html", {'curso': curso, 'exercicio': exercicio})


def page_exercicios(request, exercicios_id):
    exercicio = get_object_or_404(Exercicios, id=exercicios_id)
    question = exercicio.perguntas.all()
    return render(request, "exercises.html", {"exercicio": exercicio, "question": question})


def page_workshops_webinars(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    return render(request, "page_webinars.html", {'workshop': workshop})


def login_v(request):
    if request.method == 'POST':
        form = EmailLoginForm(data=request.POST)
        print(form.errors)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profdevhub:homepage')
        return render(request, 'login.html', {'form': form})
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_v(request):
    logout(request)
    return render(request, "login.html")


def registo(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            request.session['registo_form'] = form.cleaned_data
            email = form.cleaned_data['email']
            send_email(request, email)
            return render(request, 'confirmation.html')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'register.html', {'form': form})


def confirmar_email(request):
    if request.method == 'POST':
        n = request.POST.get('n1') + request.POST.get('n2') + request.POST.get('n3') + request.POST.get('n4')
        numbers = request.session.get('code')
        if n == numbers:
            del request.session['code']
            if request.session.get('user_email'):
                form = PasswordResetForm()
                return render(request, 'reset_password_2.html', {'form': form})
            else:
                form = UserDetailsForm()
            return render(request, 'register-1.html', {"form": form})
        else:
            return render(request, 'confirmation.html', {"error_message": "Código incorreto. Tente novamente."})
    else:
        return render(request, 'confirmation.html')


def registo_details(request):
    if request.method == "POST":
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            request.session['details_form'] = form.cleaned_data
            return render(request, 'up_doc.html')
    else:
        form = UserDetailsForm()
    return render(request, 'register-1.html', {'form': form})


def up_documentos(request):
    if request.method == 'POST':
        arquivo1 = request.FILES.get('arquivo1')
        arquivo2 = request.FILES.get('arquivo2')

        registo_form = request.session.get('registo_form')
        user_form = RegistroUsuarioForm(registo_form)
        user = user_form.save(commit=False)

        details_form = request.session.get('details_form')
        user_details_form = UserDetailsForm(details_form)
        user_details = user_details_form.save(commit=False)

        user_details.user = user

        if arquivo1 and arquivo2:
            user.user_details.documento = arquivo1
            user.user_details.documento2 = arquivo2

            user.save()
            user.user_details.save()
            del request.session['registo_form']
            del request.session['details_form']

            return render(request, "login.html")
        else:
            return render(request, 'up_doc.html', {'error_message': 'Por favor, envie ambos os arquivos.'})
    else:
        return render(request, 'up_doc.html')


def reset_password_email(request):
    if request.method == "POST":
        email = request.POST.get('email')
        request.session['user_email'] = email
        send_email(request, email)
        return render(request, 'confirmation.html')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'reset_password_1.html', {'form': form})


def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = request.session['user_email']
            usuario = User.objects.get(email=user_email)
            nova_senha = form.cleaned_data['password']
            usuario.set_password(nova_senha)
            usuario.save()
            del request.session['user_email']
            update_session_auth_hash(request, usuario)
            return render(request, 'login.html')
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password_2.html', {'form': form})


def send_email(request, email):
    subject = "Email Subject"
    body = str(random.randint(1000, 9999))
    request.session['code'] = body
    sender = env("email")
    recipients = [sender, email]
    password = env("email_pass")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
