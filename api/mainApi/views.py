from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
# from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.dispatch import receiver
from django.shortcuts import render
import pyrebase
from firebase_admin import credentials
from pathlib import Path
import json


#Initialize the Admin SDK
#colocando a credencial gerada
fileCred = "bite-a-pp-firebase-adminsdk-zhzha-63c005a8e7.json"
cred = Path(Path.home(),"Documents","Bite",fileCred)
cred = json.load(str(cred))

firebase=pyrebase.initialize_app(json.load(cred))
authe = firebase.auth()
database=firebase.database()
 
def signIn(request):
    return render(request,"Login.html")
def home(request):
    return render(request,"Home.html")
 
def postsignIn(request):
    email=request.POST.get('email')
    pasw=request.POST.get('pass')
    try:
        # if there is no error then signin the user with given email and password
        user=authe.sign_in_with_email_and_password(email,pasw)
    except:
        message="Invalid Credentials!!Please ChecK your Data"
        return render(request,"Login.html",{"message":message})
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request,"Home.html",{"email":email})
 
def logout(request):
    try:
        del request.session['uid']
    except:
        pass
    return render(request,"Login.html")
 
def signUp(request):
    return render(request,"Registration.html")
 
def postsignUp(request):
     email = request.POST.get('email')
     passs = request.POST.get('pass')
     name = request.POST.get('name')
     try:
        # creating a user with the given email and password
        user=authe.create_user_with_email_and_password(email,passs)
        uid = user['localId']
        idtoken = request.session['uid']
        print(uid)
     except:
        return render(request, "Registration.html")
     return render(request,"Login.html")

# def home(request):
#     return render(request, "index.html")
# def comanda(request):
#     return render(request, "comanda.html") 
# def pedidos(request):
#     return render(request, "pedidos.html")
# def estoque(request):
#     return render(request, "estoque.html")
# def finaceiro(request):
#     return render(request, "relFinaceiro.html")






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
