from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from store.models import Product, Collection
from model_bakery import baker
from decimal import Decimal


@pytest.mark.django_db
class TestCreateProduct:
    
    def test_if_user_anonymous_returns_401(self, api_client):
        # Arrange

        # Act 
        response = api_client.post('/store/products/', {'title': 'a'})
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, authenticate):
        # Arrange
        authenticate(is_staff=False)
        # Act
        response = api_client.post('/store/products/', {'title': 'a'})
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_data_is_invalid_returns_400(self, api_client, authenticate):
        # Arrange
        authenticate(is_staff=True)
        # Act
        response = api_client.post('/store/products/', {'title': 'a'})
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_201(self, api_client, authenticate):
        # Arrange
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        product = {
            'title': 'a',
            'slug': 'a',
            'unit_price': 1,
            'inventory': 1,
            'collection': collection.pk
        }
        # Act
        response = api_client.post('/store/products/', product)
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {
            'id': 1,
            'description': None,
            'title': 'a',
            'slug': 'a',
            'unit_price': 1,
            'inventory': 1,
            'collection': collection.pk,
            'images': [],
            'price_with_tax': product['unit_price'] * Decimal(1.1)
        }




@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        product = baker.make(Product)
        
        response = api_client.get(f'/store/products/{product.pk}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': product.pk,
            'title': product.title,
            'collection': product.collection.pk,
            'description': product.description,
            'inventory': product.inventory,
            'slug': product.slug,
            'unit_price': product.unit_price,
            'images': [],
            'price_with_tax': product.unit_price * Decimal(1.1)
        }

    def test_if_product_not_existing_returns_404(self, api_client):
        non_existing_product_id = 99999999999
        
        response = api_client.get(f'/store/products/{non_existing_product_id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
