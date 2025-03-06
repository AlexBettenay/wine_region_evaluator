from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import YourModel

class YourModelTests(APITestCase):
    def setUp(self):
        self.model_instance = YourModel.objects.create(field1='value1', field2='value2')

    def test_model_creation(self):
        url = reverse('yourmodel-list')  # Adjust the URL name as needed
        data = {'field1': 'value1', 'field2': 'value2'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(YourModel.objects.count(), 2)

    def test_model_retrieval(self):
        url = reverse('yourmodel-detail', args=[self.model_instance.id])  # Adjust the URL name as needed
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['field1'], self.model_instance.field1)

    def test_model_update(self):
        url = reverse('yourmodel-detail', args=[self.model_instance.id])  # Adjust the URL name as needed
        data = {'field1': 'new_value', 'field2': 'value2'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.model_instance.refresh_from_db()
        self.assertEqual(self.model_instance.field1, 'new_value')

    def test_model_deletion(self):
        url = reverse('yourmodel-detail', args=[self.model_instance.id])  # Adjust the URL name as needed
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(YourModel.objects.count(), 0)