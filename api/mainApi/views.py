from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from rest_framework.response import Response
from rest_framework import status
# from .models import Pedido
# from .serializers import PedidoSerializer


@requires_csrf_token
def home(request):
    return render(request, "index.html")
def comanda(request):
    return render(request, "comanda.html")
def estoque(request):
    return render(request, "estoque.html")
def finaceiro(request):
    return render(request, "relFinaceiro.html")
def pedidos(request):
    return render(request, "pedidos.html")

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
