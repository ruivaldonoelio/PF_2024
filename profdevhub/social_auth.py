from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


def check_user_exists_and_login(backend, details, request, *args, **kwargs):
    email = details.get('email')
    print(email)
    print(backend.name)

    if not email:
        raise ValidationError("Email não encontrado nas informações do usuário.")

        # Verificar se o email está registrado na base de dados
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError("Conta ainda não foi registrada.")
    print(user)
        # Fazer o login do usuário, já que ele existe
    login(request, user, backend=backend.name)