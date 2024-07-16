from django.db import models
from django.contrib.auth.models import User
import smtplib
from email.mime.text import MIMEText
from environ import Env
from datetime import date
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from docx import Document
from docx2pdf import convert
from email import encoders
import os
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

env = Env()


class User_details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='detalhes')
    telemovel = models.CharField(max_length=80)
    nascimento = models.DateField()
    endereco = models.CharField(max_length=80)
    cidade = models.CharField(max_length=80)
    codigo_postal = models.CharField(max_length=80)
    documento = models.FileField(upload_to='pdfs/')
    documento2 = models.FileField(upload_to='pdfs2/')

    def __str__(self):
        return self.user.username


class Courses(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    inicio_inscricao = models.DateField()
    fim_inscricao = models.DateField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    limite_inscritos = models.IntegerField()
    texto = models.TextField(max_length=None)
    link_zoom = models.URLField()

    def __str__(self):
        return self.titulo

    def vaga_notificacao(self):
        if self.limite_inscritos > self.inscritos.count():
            espera = Espera.objects.filter(curso=self, vaga=True).first()
            if espera:
                CursoIncritos.objects.create(curso=self, user=espera.user)
                espera.delete()
                Notificacao.objects.create(
                    user=espera.user,
                    texto=f'Você foi inscrito no workshop {self.titulo}'
                )
                send_email(f'Você foi inscrito no curso {self.titulo}', espera.user.email, False, False)

    def inscricao_notificacao(self):
        if date.today() == self.inicio_inscricao:
            espera = Espera.objects.filter(curso=self, inscricao=True)
            if espera:
                for notificacao in espera:
                    Notificacao.objects.create(
                        user=notificacao.user,
                        texto=f'Inscrições abertas no workshop'
                              f' {self.titulo}'
                    )
                    send_email(f'Inscrições abertas no curso {self.titulo}', notificacao.user.email, False, False)
                espera.delete()

    def notas_media(self, user):
        user = get_object_or_404(User, username=user)
        numero_perguntas = self.exercicios.count()
        total = 0

        for n in self.exercicios.all():
            total += n.notas(user)

        return total / numero_perguntas

    def enviar_certificado(self, user):
        inscricao = self.inscritos.filter(user=user, certificado=None).first()
        email = user.email
        replacements = {'Nome': user.username, 'Curso': self.titulo, 'data': date.today().strftime("%d/%m/%Y"),
                        'ID': str(inscricao.id)}
        input_path = "media/169-diploma-formal-blue-landscape.docx"
        output_path = "media/certificados"
        edit_word_document(input_path, output_path, replacements, str(inscricao.id))
        inscricao.certificado = "media/certificados/" + str(inscricao.id)+".pdf"
        inscricao.save()
        send_email("ja esta", email, True, str(inscricao.id))


class CursoIncritos(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='inscritos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursos')
    certificado = models.FileField(upload_to='certificados/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} in {self.curso.titulo}'


class Conteudo(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='conteudos')
    nome = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='conteudo/')

    def __str__(self):
        return self.nome


class Questionarios(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='questionarios')
    arquivo = models.FileField(upload_to='questionario/')

    def __str__(self):
        return self.arquivo


class Exercicios(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='exercicios')
    nome = models.CharField(max_length=255)
    data_encerramento = models.DateField()

    def __str__(self):
        return self.nome

    def submissions(self, user_id):
        user = get_object_or_404(User, id=user_id)
        perguntas_do_exercicio = self.perguntas.all()
        submissoes = Submit.objects.filter(pergunta__in=perguntas_do_exercicio, student=user)
        return submissoes

    def notas(self, user):
        perguntas_do_exercicio = self.perguntas.all()
        submissoes = Submit.objects.filter(pergunta__in=perguntas_do_exercicio, student=user)
        total_notas = submissoes.aggregate(soma_notas=Sum('nota'))['soma_notas']
        return total_notas if total_notas is not None else 0


class Perguntas(models.Model):
    exercicio = models.ForeignKey(Exercicios, on_delete=models.CASCADE, related_name='perguntas')
    texto = models.CharField(max_length=200)

    def __str__(self):
        return self.texto


class Submit(models.Model):
    pergunta = models.ForeignKey(Perguntas, on_delete=models.CASCADE, related_name='submissoes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissoes', blank=True, null=True)
    resposta = models.TextField(max_length=None)
    feeback = models.TextField(max_length=None, blank=True, null=True)
    nota = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.pergunta.texto} - {self.student.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        submission = self.pergunta.exercicio.submissions(self.student.id)
        ok = True
        mensagem = ""

        for submit in submission:
            if not submit.feeback or not submit.nota:
                ok = False

        if ok:
            for submit in submission:
                mensagem += (
                    f"Pergunta:\n{submit.pergunta.texto}\n\n"
                    f"Resposta:\n{submit.resposta}\n\n"
                    f"Feedback:\n{submit.feeback}\n\n"
                    f"Nota:\n{submit.nota}\n\n"
                    "------------------------\n\n"
                )
            total_notas = self.pergunta.exercicio.notas(self.student)
            mensagem += f"Total de notas para este exercício: {total_notas}"
            send_email(mensagem, self.student.email, False, False)


class Recursos(models.Model):
    nome = models.TextField(max_length=100)
    descricao = models.TextField(max_length=255)
    data_upload = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recursos')
    arquivo = models.FileField(upload_to='recurso/')

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.owner.is_superuser:
            raise ValueError("Somente superusuários podem adicionar recurso.")
        super(Recursos, self).save(*args, **kwargs)


class Workshop(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    instrutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workshops')
    inicio_inscricao = models.DateField(blank=True, null=True)
    fim_inscricao = models.DateField()
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    limite_inscritos = models.IntegerField()
    texto = models.TextField(max_length=None)
    link_zoom = models.URLField()
    arquivo = models.FileField(upload_to='workshop/', blank=True)

    escolha = [
        ('Work', 'WorkShop'),
        ('Web', 'Webinars'),
    ]

    tipo = models.CharField(max_length=10, choices=escolha, blank=True, null=True)

    def __str__(self):
        return self.titulo

    def vaga_notificacao(self):
        if self.limite_inscritos > self.inscritos.count():
            espera = Espera.objects.filter(workshop=self, vaga=True).first()
            if espera:
                WorkshopInscritos.objects.create(workshop=self, user=espera.user)
                espera.delete()

                Notificacao.objects.create(
                    user=espera.user,
                    texto=f'Você foi inscrito no workshop {self.titulo}'
                )
                send_email(f'Você foi inscrito no workshop {self.titulo}', espera.user.email, False, False)

    def inscricao_notificacao(self):
        if date.today() == self.inicio_inscricao:
            espera = Espera.objects.filter(workshop=self, inscricao=True)
            if espera:
                for notificacao in espera:
                    Notificacao.objects.create(
                        user=notificacao.user,
                        texto=f'Inscrições abertas no workshop'
                              f' {self.titulo}'
                    )
                    send_email(f'Inscrições abertas no workshop {self.titulo}', notificacao.user.email, False, False)
                espera.delete()

    def save(self, *args, **kwargs):
        if not self.instrutor.is_superuser:
            raise ValueError("Somente superusuários podem adicionar workshops.")
        super(Workshop, self).save(*args, **kwargs)


class WorkshopInscritos(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='inscritos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workshop')

    def __str__(self):
        return f'{self.user.username} in {self.workshop.titulo}'


class Forum(models.Model):
    nome = models.CharField(max_length=255, blank=True)
    curso = models.OneToOneField(Courses, on_delete=models.CASCADE, related_name='forum', blank=True, null=True)
    descricao = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.curso and not self.nome:
            self.nome = self.curso.titulo
        elif self.nome:
            self.curso = None
        super().save(*args, **kwargs)


class ForumParticipant(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='participantes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foruns')

    def __str__(self):
        return f'{self.user.username} in {self.forum.nome}'


class Mensagens(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='mensagens')
    emissor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens')
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.emissor.username}: {self.texto[:20]}'


class Notificacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacao')
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.texto[:20]}'


class Espera(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='espera')
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='lista_w', blank=True, null=True)
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='lista_c', blank=True, null=True)
    vaga = models.BooleanField(blank=True, null=True)
    inscricao = models.BooleanField(blank=True, null=True)

    def __str__(self):
        if self.workshop:
            return f'{self.user.username} Esperando {self.workshop}'
        if self.curso:
            return f'{self.user.username} Esperando {self.curso}'


def send_email(texto, email, certificado, nome):
    subject = "Email Subject"
    body = texto
    sender = env("email")
    recipients = [sender, email]
    password = env("email_pass")

    # Criando a mensagem como uma instância de MIMEMultipart
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    # Adicionando o corpo do email
    msg.attach(MIMEText(body, 'plain'))

    # Verificando se há um certificado para anexar
    if certificado:
        filename = "documento.pdf"  # Nome do arquivo que será anexado
        attachment = open("media/certificados/"+nome+".pdf", "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={filename}")
        msg.attach(part)

    # Enviando o email usando SMTP_SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())


def edit_word_document(input_path, output_path, replacements, nome):
    # Abra o documento existente
    doc = Document(input_path)

    # Faça as substituições necessárias
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for key, value in replacements.items():
                if key in run.text:
                    run.text = run.text.replace(key, value)

    # Salve a edição em um novo arquivo .docx
    edited_path = nome + '.docx'
    doc.save(edited_path)

    # Converta o documento editado para PDF
    convert(edited_path, output_path)
