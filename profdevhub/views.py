from django.shortcuts import render, redirect, get_object_or_404
from .form import RegistroUsuarioForm, UserDetailsForm, PasswordResetForm, EmailLoginForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .models import *
from django.urls import reverse
from datetime import date
from django.contrib import messages
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
    user = request.user
    detalhes = get_object_or_404(User_details, id=user.id)

    if request.method == "POST":

        if request.POST.get("first_name"):
            user.first_name = request.POST.get("first_name")

        if request.POST.get("last_name"):
            user.last_name = request.POST.get("last_name")

        if request.POST.get("email"):
            user.email = request.POST.get("email")

        if request.POST.get("telemovel"):
            detalhes.telemovel = request.POST.get("telemovel")

        if request.POST.get("endereco"):
            detalhes.endereco = request.POST.get("endereco")

        if request.POST.get("cidade"):
            detalhes.cidade = request.POST.get("cidade")

        if request.POST.get("codigo_postal"):
            codigo_postal = request.POST.get("codigo_postal")

        try:
            user.save()
            detalhes.save()
        except:
            return redirect(reverse('profdevhub:page_forum'))

    return render(request, "profile.html", {"user": request.user})


@login_required
def courses(request):
    cursos = Courses.objects.all()
    today = date.today()
    return render(request, "courses.html", {"cursos": cursos, "today": today})


@login_required
def workshops_webinars(request):
    if request.method == 'POST':
        search = request.POST.get("search")
        tipo = request.POST.get("tipo")

        if search and tipo != "Categoria":
            workshop = Workshop.objects.filter(titulo__icontains=search, tipo=tipo)
        elif search and tipo == "Categoria":
            workshop = Workshop.objects.filter(titulo__icontains=search)
        elif tipo != "Categoria" and not search:
            workshop = Workshop.objects.filter(tipo=tipo)
        elif tipo == "Categoria":
            workshop = Workshop.objects.all()
    else:
        workshop = Workshop.objects.all()

    today = date.today()
    return render(request, "workshops.html", {"workshop": workshop, "today": today})


@login_required
def forum(request):
    chat = Forum.objects.all().filter(curso_id=None)
    return render(request, "forum.html", {"chat": chat})


@login_required
def resources(request):
    if request.method == "POST":
        search = request.POST.get("search")
        if search:
            recursos = Recursos.objects.filter(nome__icontains=search)
        else:
            recursos = Recursos.objects.all()
    else:
        recursos = Recursos.objects.all()

    return render(request, "resource.html", {"recursos": recursos})


def page_forum(request, forum_id):
    try:
        forum = get_object_or_404(Forum, id=forum_id)
    except:
        return redirect('profdevhub:forum')
    else:
        if request.method == 'POST':
            message = request.POST.get('message')

            if message:
                enviar = Mensagens(forum=forum, emissor=request.user, texto=message)
                enviar.save()
                return redirect(reverse('profdevhub:page_forum', args=[forum_id]))

        mensagem = forum.mensagens.all().order_by('data')

        if forum.curso_id is None:
            return render(request, "page_forum.html", {'forum': forum, 'mensagens': mensagem})
        else:
            inscrito = forum.curso.inscritos.all().filter(user_id=request.user.id).exists()
            if inscrito:
                return render(request, "page_forum.html", {'forum': forum, 'mensagens': mensagem})
            else:
                return redirect('profdevhub:forum')


def page_course(request, course_id):
    try:
        curso = get_object_or_404(Courses, id=course_id)
    except:
        return redirect('profdevhub:courses')

    inscrito = curso.inscritos.filter(user_id=request.user.id).exists()
    today = date.today()
    return render(request, "page_course.html", {'curso': curso, "inscrito": inscrito, "today": today})


def page_exercicios(request, exercicios_id):
    try:
        exercicio = get_object_or_404(Exercicios, id=exercicios_id)
    except:
        return redirect('profdevhub:courses')
    else:

        inscrito = exercicio.curso.inscritos.filter(user_id=request.user.id).exists()

        if request.method == 'POST':
            for perguntas in exercicio.perguntas.all():
                if request.POST.get(str(perguntas.id)):
                    Submit.objects.create(pergunta=perguntas, student=request.user, resposta=request.POST.get(str(perguntas.id)))

            curso_id = exercicio.curso.id
            return redirect(reverse('profdevhub:page_courses', args=[curso_id]))

        if inscrito:
            return render(request, "exercises.html", {"exercicio": exercicio})
        else: return redirect('profdevhub:courses')


def page_workshops_webinars(request, workshop_id):
    try:
        workshop = get_object_or_404(Workshop, id=workshop_id)
    except:
        return redirect('profdevhub:workshops_webinars')

    inscrito = workshop.inscritos.filter(user_id=request.user.id).exists()
    today = date.today()
    return render(request, "page_webinars.html", {'workshop': workshop, 'inscrito': inscrito, 'today': today})


def inscricao_anular_curso(request, curso_id):
    user = request.user
    curso = get_object_or_404(Courses, id=curso_id)

    inscrito = curso.inscritos.filter(user_id=user.id).exists()
    tempo = curso.inicio_inscricao <= date.today() and curso.fim_inscricao >= date.today()
    vaga = curso.limite_inscritos != curso.inscritos.count()

    if not inscrito and vaga and tempo:
        inscricao = CursoIncritos(curso=curso, user=user)
        inscricao.save()
        messages.success(request, 'Inscrição realizada com sucesso!')
    elif inscrito or tempo:
        inscricao = get_object_or_404(CursoIncritos, curso_id=curso.id, user_id=user.id)
        inscricao.delete()
        messages.success(request, 'Inscrição removida com sucesso.')
    else:
        messages.warning(request, 'Você já está inscrito neste curso.')

    return redirect(reverse('profdevhub:page_courses', args=[curso_id]))


def inscricao_anular_workshop(request, workshop_id):
    user = request.user
    workshop = get_object_or_404(Workshop, id=workshop_id)

    inscrito = workshop.inscritos.filter(user_id=user.id).exists()
    tempo = workshop.inicio_inscricao <= date.today() and workshop.fim_inscricao >= date.today()
    vaga = workshop.limite_inscritos != workshop.inscritos.count()

    if not inscrito and vaga and tempo:
        inscricao = WorkshopInscritos(workshop=workshop, user=user)
        inscricao.save()
        messages.success(request, 'Inscrição realizada com sucesso!')
    elif inscrito or tempo:
        inscricao = get_object_or_404(WorkshopInscritos, workshop=workshop.id, user_id=user.id)
        inscricao.delete()
        messages.success(request, 'Inscrição removida com sucesso.')
    else:
        messages.warning(request, 'Ja não da')

    return redirect(reverse('profdevhub:page_workshops_webinars', args=[workshop_id]))


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
            if request.session['user_email']:
                user_email = request.session['user_email']
            if request.user.email:
                user_email = request.user.email

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