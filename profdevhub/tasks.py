from celery import shared_task
from .models import Workshop, Courses


@shared_task
def check_vaga():
    for workshop in Workshop.objects.all():
        workshop.vaga_notificacao()


@shared_task
def check_inscricao():
    for course in Courses.objects.all():
        course.inscricao_notificacao()
