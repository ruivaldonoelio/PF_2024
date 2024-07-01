from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from datetime import date
from .models import User_details
from django.core.exceptions import ValidationError
import re


class RegistroUsuarioForm(forms.ModelForm):
    password_confirm = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("As senhas não coincidem. Por favor, digite novamente.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso. Por favor, escolha outro.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso. Por favor, escolha outro.")
        return email

    def save(self, commit=True):
        user = super(RegistroUsuarioForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserDetailsForm(forms.ModelForm):
    documento = forms.CharField(required=False)
    documento2 = forms.CharField(required=False)

    class Meta:
        model = User_details
        fields = ['telemovel', 'nascimento', 'endereco', 'cidade', 'codigo_postal', 'documento', 'documento2']

    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento')
        idade_minima = 24
        idade = (date.today() - nascimento).days // 365  # Calcula a idade em anos

        if idade < idade_minima:
            raise ValidationError("Você deve ter pelo menos 24 anos para se cadastrar.")
        return nascimento.strftime("%Y-%m-%d")

    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        if not re.match(r'^\d{4}-\d{3}$', codigo_postal):
            raise ValidationError("O código postal deve estar no formato '1111-111'.")
        return codigo_postal


class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    re_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')

        if password != re_password:
            raise forms.ValidationError("A nova senha e a confirmação de senha não correspondem.")
        return cleaned_data


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254, required=True)

    def clean_username(self):
        email = self.cleaned_data.get('username')
        if not email:
            raise forms.ValidationError("O campo Email é obrigatório.")
        return email

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                self.user_cache = authenticate(username=user.username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError("Email ou senha inválidos.")
                elif not self.user_cache.is_active:
                    raise forms.ValidationError("Esta conta está inativa.")
            except User.DoesNotExist:
                raise forms.ValidationError("Email ou senha inválidos.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UserUpdateForm(forms.ModelForm):
    telemovel = forms.CharField(max_length=80, required=False)
    endereco = forms.CharField(max_length=80, required=False)
    cidade = forms.CharField(max_length=80, required=False)
    codigo_postal = forms.CharField(max_length=80, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def clean_codigo_postal(self):
        codigo_postal = self.cleaned_data.get('codigo_postal')
        if codigo_postal and not re.match(r'^\d{4}-\d{3}$', codigo_postal):
            raise forms.ValidationError("O formato do código postal deve ser 1111-111.")
        return codigo_postal