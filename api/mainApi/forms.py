from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class ClienteCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='*')
    name = forms.CharField(max_length=30, required=True, help_text='*')
    telefone = forms.CharField(max_length=10, required=True)
    class Meta:
        model = Usuario
        fields = ('email', 'password1', 'password2', 'name', 'telefone')

class FuncionarioCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    nivel_acesso = forms.CharField(max_length=10)
    cargo = forms.CharField(max_length=50)

    class Meta:
        model = Usuario
        fields = ('email', 'password1', 'password2', 'name', 'nivel_acesso', 'cargo')


class AdministradorCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    nivel_acesso = forms.CharField(max_length=10)
    historico_login = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Usuario
        fields = ('email', 'password1', 'password2', 'name', 'nivel_acesso', 'historico_login')
