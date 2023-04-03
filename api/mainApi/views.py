from django.shortcuts import render
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.contrib.auth.decorators import login_required
import pyrebase
from allauth.exceptions import AuthenticationError # type: ignore


# Configure Firebase
config={
    apiKey: "AIzaSyA4CnkanVSlOq9YOdTkPUZV4NEQkVYh87g",
    authDomain: "bite-a-pp.firebaseapp.com",
    databaseURL: "https://bite-a-pp-default-rtdb.firebaseio.com",
    projectId: "bite-a-pp",
    storageBucket: "bite-a-pp.appspot.com",
    messagingSenderId: "480172695212",
    appId: "1:480172695212:web:efde2d926d5135ab540909",
    # measurementId: "G-HJ361CB6B1",
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Set up Google OAuth2 adapter
google_adapter = GoogleOAuth2Adapter(client_id=settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID,client_secret=settings.SOCIAL_AUTH_GOOGLE_CLIENT_SECRET)
google_oauth2_login = google_adapter.login
google_oauth2_callback = google_adapter.callback


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
    except AuthenticationError:
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
