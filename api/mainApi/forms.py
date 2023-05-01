from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Cliente,Funcionario,Administrador


class ClienteCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='*.')
    name = forms.CharField(max_length=30, required=True, help_text='*')

    class Meta:
        model = Cliente
        fields = ('email', 'password1', 'password2', 'name')

class FuncionarioCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    nivel_acesso = forms.CharField(max_length=10)
    salario = forms.DecimalField(max_digits=10, decimal_places=2)
    cargo = forms.CharField(max_length=50)

    class Meta:
        model = Funcionario
        fields = ('email', 'password1', 'password2', 'name', 'nivel_acesso', 'salario', 'cargo')


class AdministradorCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    nivel_acesso = forms.CharField(max_length=10)
    historico_login = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Administrador
        fields = ('email', 'password1', 'password2', 'name', 'nivel_acesso', 'historico_login')
