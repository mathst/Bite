# import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from firebase_admin.credentials import Certificate
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, user as User
from .forms import ClienteCreationForm, FuncionarioCreationForm , AdministradorCreationForm
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect

# Initialize Firestore client
# db = firestore.client()

# Autentica o usuário usando o Google
def authenticate_with_google(request):
    id_token = request.POST.get('id_token')

    # Verify the ID token using the Firebase Admin SDK
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
    except firebase_auth.InvalidIdTokenError:
        return JsonResponse({'error': 'Invalid ID token'}, status=400)

    # Check if the user already exists in the database
    try:
        user = CustomUser.objects.get(email=decoded_token['email'])
    except CustomUser.DoesNotExist:
        # If the user doesn't exist, create a new one
        user = CustomUser(email=decoded_token['email'], username=decoded_token['email'])
        user.set_unusable_password()
        user.save()

    # authenticate the user
    user = authenticate(request, email=decoded_token['email'])
    if user is not None:
        login(request, user)
        return JsonResponse({'redirect_url': '/cardapio/'})
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

@cache_page(60 * 15)
@csrf_protect
def signup_cliente(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_cliente = True
            user.save()
            login(request, user)
            return redirect('cardapio')
    else:
        form = ClienteCreationForm()
    return render(request, 'accounts/signup_cliente.html', {'form': form})

@cache_page(60 * 15)
@csrf_protect
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
            return redirect('cardapio')
    else:
        form = FuncionarioCreationForm()
    return render(request, 'accounts/signup_funcionario.html', {'form': form})


@cache_page(60 * 15)
@csrf_protect
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
            return redirect('cardapio')
    else:
        form = AdministradorCreationForm()
    return render(request, 'accounts/signup_administrador.html', {'form': form})


def cardapio(request):
    # Lógica para listar produtos em estoque
    return render(request, 'cardapio.html')
# @login_required
def estoque(request):
    # Lógica para listar produtos em estoque
    return render(request, 'estoque.html')

# @login_required
def pedidos(request):
    return render(request, "pedidos.html")

# @login_required
def finaceiro(request):
    return render(request, "relFinaceiro.html")
# @login_required
def comanda(request):
    return render(request, "comanda.html") 

def index(request):
    return render(request, "index.html") 

def criar_conta(nome, email, senha, tipo_conta, **kwargs):
    assert tipo_conta in ['cliente', 'funcionario', 'admin'], "Tipo de conta inválido"
    
    # Cria o usuário no Firebase Authentication
    user = firebase_auth.create_user(
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

def signup_cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        telefone = request.POST.get('telefone')
        
        try:
            # Cria o usuário no Firebase Authentication
            user = firebase_auth.create_user(
                email=email,
                password=senha,
                display_name=nome,
                email_verified=True
            )
            
            # Cria o usuário no Django User Model
            django_user = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
            )
            
            # Adiciona informações adicionais ao usuário
            django_user.cliente.endereco = endereco
            django_user.cliente.telefone = telefone
            django_user.cliente.save()
            
            # Autentica o usuário no Django User Model
            user = authenticate(request, username=email, password=senha)
            login(request, user)
            
            # Redireciona o usuário para a página de sucesso
            messages.success(request, 'Conta criada com sucesso')
            return redirect('cardapio')
        
        except firebase_auth.EmailAlreadyExistsError:
            messages.error(request, 'Este email já está em uso')
            return redirect('signup_cliente')
        
        except ValueError as e:
            messages.error(request,e)
            return redirect('signup_cliente')
            
    else:
        form = ClienteCreationForm()
    return render(request, 'accounts/signup_cliente.html', {'form': form})

def sign_cliente(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Verifica se o usuário existe no Firebase Authentication
        try:
            user = firebase_auth.get_user_by_email(email)
        except firebase_auth.UserNotFoundError:
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
        return redirect('cardapio')
    
    return render(request, 'login.html')

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        try:
            user = firebase_auth.get_user_by_email(email)
        except firebase_auth.UserNotFoundError:
            messages.error(request, 'Email ou senha inválidos')
            return redirect('login')

        if user.disabled:
            messages.error(request, 'Usuário bloqueado')
            return redirect('login')

        try:
            user_token = request.POST.get('uid')
            decoded_token = firebase_auth.verify_id_token(user_token)
            
        except:
            messages.error(request, 'Erro ao verificar token de autenticação')
            return redirect('login')

        # user_type = decoded_token.get('user_type')
        uid = request.POST.get('uid')
        user_type = firebase_auth.verify_id_token(uid)

        if user_type == 'cliente':
            user = authenticate(request, username=email, password=password)
            if user is None:
                messages.error(request, 'Email ou senha inválidos')
                return redirect('login')

            messages.success(request, 'Login efetuado com sucesso')
            login(request, user)
            return redirect('cardapio')

        elif user_type == 'funcionario':
            try:
                funcionario = Funcionario.objects.get(email=email)
            except Funcionario.DoesNotExist:
                messages.error(request, 'Email ou senha inválidos')
                return redirect('login')

            if funcionario.senha != password:
                messages.error(request, 'Email ou senha inválidos')
                return redirect('login')

            messages.success(request, 'Login efetuado com sucesso')
            login(request, funcionario)
            return redirect('dashboard_funcionario')

        elif user_type == 'admin':
            try:
                admin = Administrador.objects.get(email=email)
            except Administrador.DoesNotExist:
                messages.error(request, 'Email ou senha inválidos')
                return redirect('login')

            if admin.senha != password:
                messages.error(request, 'Email ou senha inválidos')
                return redirect('login')

            messages.success(request, 'Login efetuado com sucesso')
            login(request, admin)
            return redirect('dashboard_admin')

        else:
            messages.error(request, 'Tipo de conta inválido')
            return redirect('login')

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