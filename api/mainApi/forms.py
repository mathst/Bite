from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Email',
            'data-validate': 'Email é necessario: ex@abc.xyz'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input100',
            'placeholder': 'Senha',
            'data-validate': 'Senha é necessaria'
        })
    )
    
class CadastroClienteForm(forms.Form):
    nome = forms.CharField(
        label='nome',
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Nome',
            'data-validate': 'Nome é necessaria'
        })
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Email',
            'data-validate': 'Email é necessário: ex@abc.xyz'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'input100',
            'placeholder': 'Senha',
            'data-validate': 'Senha é necessária'
        })
    )
    password1 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={
            'class': 'input100',
            'placeholder': 'Confirme sua senha'
        })
    )
    telefone = forms.CharField(
        label='Telefone',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Telefone'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não são iguais.")
        return cleaned_data