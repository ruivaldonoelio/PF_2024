from django.db import models
from django.contrib.auth.models import User


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


class CursoIncritos(models.Model):
    curso = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='inscritos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursos')

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


class Perguntas(models.Model):
    exercicio = models.ForeignKey(Exercicios, on_delete=models.CASCADE, related_name='perguntas')
    texto = models.CharField(max_length=200)

    def __str__(self):
        return self.texto


class Submit(models.Model):
    pergunta = models.ForeignKey(Perguntas, on_delete=models.CASCADE, related_name='submissoes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissoes')
    resposta = models.TextField(max_length=None)
    feeback = models.TextField(max_length=None, blank=True)
    nota = models.IntegerField(default=0)

    def __str__(self):
        return self.pergunta.texto


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
    curso = models.OneToOneField(Courses, on_delete=models.CASCADE, related_name='forum',  blank=True, null=True)
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
