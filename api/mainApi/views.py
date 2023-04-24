# import firebase_admin
from firebase_admin import credentials, auth, firestore
from firebase_admin.credentials import Certificate
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, user as User
from .forms import CustomUserCreationForm, ClienteCreationForm, FuncionarioCreationForm , AdministradorCreationForm
from django.contrib import messages


# Initialize Firestore client
# db = firestore.client()

# Autentica o usuário usando o Google
def authenticate_with_google(request):
    id_token = request.POST.get('id_token')

    # Verify the ID token using the Firebase Admin SDK
    try:
        decoded_token = auth.verify_id_token(id_token)
    except auth.InvalidIdTokenError:
        return JsonResponse({'error': 'Invalid ID token'}, status=400)

    # Check if the user already exists in the database
    try:
        user = CustomUser.objects.get(email=decoded_token['email'])
    except CustomUser.DoesNotExist:
        # If the user doesn't exist, create a new one
        user = CustomUser(email=decoded_token['email'], username=decoded_token['email'])
        user.set_unusable_password()
        user.save()

    # Authenticate the user
    user = authenticate(request, email=decoded_token['email'])
    if user is not None:
        login(request, user)
        return JsonResponse({'redirect_url': '/'})
    else:
        return JsonResponse({'error': 'Failed to authenticate user'}, status=400)


# def signup(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'signup.html', {'form': form})

def signup_cliente(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_cliente = True
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = ClienteCreationForm()
    return render(request, 'accounts/signup_cliente.html', {'form': form})

def signup_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # autentica o usuário e faz o login
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = FuncionarioCreationForm()
    return render(request, 'accounts/signup_funcionario.html', {'form': form})

def signup_administrador(request):
    if request.method == 'POST':
        form = AdministradorCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # autentica o usuário e faz o login
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = AdministradorCreationForm()
    return render(request, 'accounts/signup_administrador.html', {'form': form})

# @login_required
def estoque(request):
    # Lógica para listar produtos em estoque
    return render(request, 'estoque.html')

# @login_required
def compras(request):
    return render(request, "compras.html")

# @login_required
def pedidos(request):
    return render(request, "pedidos.html")

# @login_required
def finaceiro(request):
    return render(request, "relFinaceiro.html")

def comanda(request):
    return render(request, "comanda.html") 

def index(request):
    return render(request, "index.html") 

def criar_conta(nome, email, senha, tipo_conta, **kwargs):
    assert tipo_conta in ['cliente', 'funcionario', 'admin'], "Tipo de conta inválido"
    
    # Cria o usuário no Firebase Authentication
    user = auth.create_user(
        email=email,
        password=senha,
        display_name=nome,
        email_verified=True  # Apenas usuários verificados podem fazer login
    )
    
    # Cria o usuário no Django User Model
    django_user = User.objects.create_user(
        username=email,
        email=email,
        password=senha,
    )
    
    # Adiciona informações adicionais ao usuário dependendo do tipo de conta
    if tipo_conta == 'cliente':
        # Exemplo de informações adicionais para conta de cliente
        endereco = kwargs.get('endereco')
        telefone = kwargs.get('telefone')
        # Adiciona informações ao Django User Model
        django_user.cliente.endereco = endereco
        django_user.cliente.telefone = telefone
        django_user.cliente.save()
    elif tipo_conta == 'funcionario':
        # Exemplo de informações adicionais para conta de funcionário
        cargo = kwargs.get('cargo')
        salario = kwargs.get('salario')
        # Adiciona informações ao Django User Model
        django_user.funcionario.cargo = cargo
        django_user.funcionario.salario = salario
        django_user.funcionario.save()
    elif tipo_conta == 'admin':
        # Não há informações adicionais para conta de admin
        pass
    
    # Retorna o ID do usuário criado no Firebase
    return user.uid

def sign_cliente(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Verifica se o usuário existe no Firebase Authentication
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            messages.error(request, 'Email ou senha inválidos')
            return redirect('login')
        
        # Verifica se o usuário está ativo
        if user.disabled:
            messages.error(request, 'Usuário bloqueado')
            return redirect('login')
        
        # Autentica o usuário no Django User Model
        django_user = authenticate(request, username=email, password=senha)
        if django_user is None:
            messages.error(request, 'Email ou senha inválidos')
            return redirect('login')
        
        # Redireciona o usuário para a página de sucesso
        messages.success(request, 'Login efetuado com sucesso')
        return redirect('home')
    
    return render(request, 'login.html')

'''exemplo de aplicação'''
# def minha_view(request):
#     # Get all documents from a collection
#     docs = db.collection('minha_colecao').get()
    
#     # Process the documents
#     for doc in docs:
#         # Do something with the document
#         pass
    
#     # Return a response
#     return HttpResponse('Success')