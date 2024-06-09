from django.db import models
from django.contrib.auth.models import User


class User_details(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    descrição = models.CharField(max_length=255)
    inicio_inscricao = models.DateField()
    fim_inscricao = models.DateField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    limite_inscritos = models.IntegerField()
    texto = models.CharField(max_length=500)

    def __str__(self):
        return self.titulo


class Conteudo(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='conteudos')
    arquivo = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.curso.titulo


class Exercicio(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='exercicios')
    arquivo = models.FileField(upload_to='arquivo/')

    def __str__(self):
        return self.curso.titulo


class QuestionText(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='questions')
    number = models.CharField(max_length=200)
    data_encerramento = models.DateField()

    def __str__(self):
        return self.curso.titulo


class Text(models.Model):
    question = models.ForeignKey(QuestionText, on_delete=models.CASCADE, related_name='questions')
    texto = models.CharField(max_length=200)

    def __str__(self):
        return self.question.number

