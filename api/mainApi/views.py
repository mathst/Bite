import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.credentials import Certificate
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
# from api.mainApi.models import CustomUser
from .models import CustomUser
from .forms import CustomUserCreationForm, ClienteCreationForm, FuncionarioCreationForm , AdministradorCreationForm

import json
import os
import requests

# Inicializando o SDK do Firebase usando credenciais do arquivo JSON
with open('../credentials/credentials.json', 'r') as f:
    credentials = json.load(f)
cred = Certificate(credentials)
firebase_admin.initialize_app(cred)

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


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

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
    return render(request, 'signup_cliente.html', {'form': form})

def funcionario_signup(request):
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
    return render(request, 'signup.html', {'form': form})

def administrador_signup(request):
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
    return render(request, 'signup.html', {'form': form})

@login_required
def estoque(request):
    # Lógica para listar produtos em estoque
    return render(request, 'estoque.html')

@login_required
def compras(request):
    return render(request, "compras.html")

@login_required
def pedidos(request):
    return render(request, "pedidos.html")

@login_required
def finaceiro(request):
    return render(request, "relFinaceiro.html")

def comanda(request):
    return render(request, "comanda.html") 


# def Firebase_validation(id_token):
#    """
#    This function receives id token sent by Firebase and
#    validate the id token then check if the user exist on
#    Firebase or not if exist it returns True else False
#    """
#    try:
#        decoded_token = auth.verify_id_token(id_token)
#        uid = decoded_token['uid']
#        provider = decoded_token['firebase']['sign_in_provider']
#        image = None
#        name = None
#        if "name" in decoded_token:
#            name = decoded_token['name']
#        if "picture" in decoded_token:
#            image = decoded_token['picture']
#        try:
#            user = auth.get_user(uid)
#            email = user.email
#            if user:
#                return {
#                    "status": True,
#                    "uid": uid,
#                    "email": email,
#                    "name": name,
#                    "provider": provider,
#                    "image": image
#                }
#            else:
#                return False
#        except UserNotFoundError:
#            print("user not exist")
#    except ExpiredIdTokenError:
#        print("invalid token")



# @api_view(["GET", "POST"])

# It takes a request, and an id, and returns the Pedido object with that id.
# class PedidoDetailView(APIView):
#     def post(self, request):
#         """
#         HttpResponsees the request data, validates it, saves it, and returns a success response
        
#         :param request: The request object is the first parameter to the view. It contains the request data,
#         including the request body, query parameters, and headers
#         :return: The serializer.data is being returned.
#         """
#         serializer = PedidoSerializer(
#             data=request.data,
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"status": "success", "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"status": "error", "data": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     def put(self, request, id=None):
#         """
#         It gets the object with the id passed in the URL, then it updates the object with the data passed in
#         the request body, and finally it returns the updated object
        
#         :param request: The request object
#         :param id: The id of the object you want to update
#         :return: The serializer.data is being returned.
#         """
#         Pedido = Pedido.objects.get(id=id)
#         serializer = PedidoSerializer(Pedido, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"status": "success", "data": serializer.data})
#         else:
#             return Response({"status": "error", "data": serializer.errors})

#     """
#     The above function is a patch function that updates the data of a specific object.
    
#     :param request: The request object
#     :param id: The id of the object you want to update
#     :return: The serializer.data is being returned.
#     """
#     def patch(self, request, id=None):
#         Pedido = Pedido.objects.get(id=id)
#         serializer = PedidoSerializer(Pedido, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"status": "success", "data": serializer.data})
#         else:
#             return Response({"status": "error", "data": serializer.errors})

#     def delete(self, request, id=None):
#         """
#         It takes a request, and an id, and deletes the item with that id
        
#         :param request: The request object
#         :param id: The id of the object to be deleted
#         :return: The response is being returned in JSON format.
#         """
#         item = get_object_or_404(Pedido, id=id)
#         item.delete()
#         return Response({"status": "success", "data": "Pedido Deleted"})

#     def get(self, request, id=None):
#         """
#         If the id is not None, then get the Pedido object with the id and return it. 
#         If the id is None, then get all the Pedido objects and return them. 
#         If the request has query parameters, then filter the Pedido objects and return them.
        
#         :param request: The request object
#         :param id: The id of the object you want to retrieve
#         :return: The get method is returning a response with the status and data.
#         """
#         if id:
#             Pedido = Pedido.objects.get(id=id)
#             serializer = PedidoSerializer(Pedido)
#             return Response(
#                 {"status": "success", "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         elif id == None:
#             Pedido = Pedido.objects.all()
#             serializer = PedidoSerializer(Pedido, many=True)
#             return Response(
#                 {"status": "success", "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
#         elif request.query_params:
#             Pedido = Pedido.objects.filter(**request.query_params.dict())
#             serializer = PedidoSerializer(Pedido, many=True)
#             return Response(
#                 {"status": "success", "data": serializer.data},
#                 status=status.HTTP_200_OK,
#             )
