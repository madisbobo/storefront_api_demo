from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from store.models import Collection, Product, ProductImage
from model_bakery import baker

# # A way to remove the api_client.post('/store/collections/') repetition
# @pytest.fixture
# def create_collection(api_client):
#     def do_create_collection(collection):
#         return api_client.post('/store/collections/', {'title': 'a'})
#     return do_create_collection

@pytest.mark.django_db
class TestCreateCollection:
    # @pytest.mark.skip - if you want to skip the test
    def test_if_user_anonymous_returns_401(self, api_client):
        # Arrange

        # Act
        response = api_client.post('/store/collections/', {'title': 'a'})
        # response = create_collection({'title':'a'})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client, authenticate):
        # Arrange
        authenticate(is_staff=False)

        # Act
        response = api_client.post('/store/collections/', {'title': 'a'})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client, authenticate):
        authenticate(is_staff=True)
        response = api_client.post('/store/collections/', {'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, api_client, authenticate):
        authenticate(is_staff=True)
        response = api_client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:

    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.pk}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.pk,
            'title': collection.title,
            'product_count': 0
        }


    def test_if_no_collection_returns_404(self, api_client):
        non_existing_collection_id = 99999

        response = api_client.get(f'/store/collections/{non_existing_collection_id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


