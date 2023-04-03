from django.shortcuts import render
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.contrib.auth.decorators import login_required
import pyrebase
import allauth.exceptions
import firebase_admin
from firebase_admin import credentials



# Configure Firebase
config={
    "apiKey": "AIzaSyA4CnkanVSlOq9YOdTkPUZV4NEQkVYh87g",
    "authDomain": "bite-a-pp.firebaseapp.com",
    "databaseURL": "https://bite-a-pp-default-rtdb.firebaseio.com",
    'projectId': "bite-a-pp",
    'storageBucket': "bite-a-pp.appspot.com",
    'messagingSenderId': "480172695212",
    'appId': "1:480172695212:web:efde2d926d5135ab540909",
    # "measurementId": "G-HJ361CB6B1",
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Set up Google OAuth2 adapter
class GoogleAdapter(GoogleOAuth2Adapter):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/accounts/google/login/callback/'
    client_class = OAuth2Client


@login_required
def home(request):
    return render(request,"Home.html")

def login(request):
    return render(request, "Login.html")

def signup(request):
    return render(request, "Registration.html")

def logout(request):
    auth.logout(request)
    return render(request, "Login.html")

def auth_error(request):
    return render(request, "auth_error.html")

def google_login(request):
    return google_oauth2_login(request)

def google_callback(request):
    try:
        # Authenticate with Firebase using the Google access token
        access_token = request.GET.get('access_token')
        user = auth.sign_in_with_oauth(access_token)
        # If the user is authenticated, log them in
        if user:
            auth_data = auth.get_account_info(user['idToken'])
            uid = auth_data['users'][0]['localId']
            request.session['uid'] = uid
            return render(request, "Home.html")
    except allauth.exceptions.AuthenticationError:
        return render(request, "auth_error.html")

def reset(request):
    return render(request, "Reset.html")
 
def postReset(request):
    email = request.POST.get('email')
    try:
        auth.send_password_reset_email(email)
        message = "An email to reset password is successfully sent"
        return render(request, "Reset.html", {"msg": message})
    except:
        message = "Something went wrong. Please check if the email you provided is registered or not."
        return render(request, "Reset.html", {"msg": message})

# def home(request):
#     return render(request, "index.html")
def comanda(request):
    return render(request, "comanda.html") 
def pedidos(request):
    return render(request, "pedidos.html")
def estoque(request):
    return render(request, "estoque.html")
def finaceiro(request):
    return render(request, "relFinaceiro.html")

# cred
# cred = credentials.Certificate({
#  "type": "service_account",
#  "project_id": os.getenv('FIREBASE_PROJECT_ID'),
#  "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
#  "private_key": os.environ.get('FIREBASE_PRIVATE_KEY'),
#  "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
#  "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
#  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#  "token_uri": "https://accounts.google.com/o/oauth2/token",
#  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#  "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
# })
default_app = firebase_admin.initialize_app(config)

def Firebase_validation(id_token):
   """
   This function receives id token sent by Firebase and
   validate the id token then check if the user exist on
   Firebase or not if exist it returns True else False
   """
   try:
       decoded_token = auth.verify_id_token(id_token)
       uid = decoded_token['uid']
       provider = decoded_token['firebase']['sign_in_provider']
       image = None
       name = None
       if "name" in decoded_token:
           name = decoded_token['name']
       if "picture" in decoded_token:
           image = decoded_token['picture']
       try:
           user = auth.get_user(uid)
           email = user.email
           if user:
               return {
                   "status": True,
                   "uid": uid,
                   "email": email,
                   "name": name,
                   "provider": provider,
                   "image": image
               }
           else:
               return False
       except UserNotFoundError:
           print("user not exist")
   except ExpiredIdTokenError:
       print("invalid token")



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
