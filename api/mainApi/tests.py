from django.test import TestCase
from .models import Veiculo

    # id = models.BigAutoField(primary_key=True)
    # veiculo = models.CharField(max_length = 180)
    # marca = models.CharField(max_length = 180)
    # cor = models.CharField(max_length = 180)
    # ano = models.PositiveIntegerField()
    # descricao = models.TextField()
    # vendido = models.BooleanField(default = False)
    # created = models.DateTimeField(auto_created= True, blank = True, auto_now_add=True)
    # update = models.DateTimeField(auto_now = True, blank = True)

# class VeiculoModelTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         # Set up non-modified objects used by all test methods
#         Veiculo.objects.create(veiculo="uno", marca="fiat", cor="rosa", vendido="False", created="", update="")

#     def test_veiculo_label(self):
#         author = Veiculo.objects.get(id=1)
#         field_label = author._meta.get_field('veiculo').verbose_name
#         self.assertEqual(field_label, 'first name')

#     def test_marca_label(self):
#         author = Veiculo.objects.get(id=1)
#         field_label = author._meta.get_field('marca').verbose_name
#         self.assertEqual(field_label, 'marca')

#     def test_first_veiculo_max_length(self):
#         author = Veiculo.objects.get(id=1)
#         max_length = author._meta.get_field('veiculo').max_length
#         self.assertEqual(max_length, 180)

#     def test_get_absolute_url(self):
#         author = Veiculo.objects.get(id=1)
#         # This will also fail if the urlconf is not defined.
#         self.assertEqual(author.get_absolute_url(), 'veiculo/1')