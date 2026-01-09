import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Business, Product

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def business(db):
    return Business.objects.create(name="Test Business", description="A test business")


@pytest.fixture
def admin_user(db, business):
    return User.objects.create_user(
        username="admin",
        password="admin123",
        business=business,
        role="admin"
    )


@pytest.fixture
def editor_user(db, business):
    return User.objects.create_user(
        username="editor",
        password="editor123",
        business=business,
        role="editor"
    )


@pytest.mark.django_db
def test_business_creation(business):
    assert business.name == "Test Business"
    assert str(business) == "Test Business"


@pytest.mark.django_db
def test_user_creation(editor_user, business):
    assert editor_user.username == "editor"
    assert editor_user.business == business
    assert editor_user.role == "editor"


@pytest.mark.django_db
def test_product_creation(editor_user, business):
    product = Product.objects.create(
        name="Test Product",
        description="A test product",
        price=99.99,
        created_by=editor_user,
        business=business
    )
    assert product.name == "Test Product"
    assert product.status == "draft"
    assert str(product) == "Test Product"


@pytest.mark.django_db
def test_token_obtain(api_client, admin_user):
    response = api_client.post('/api/token/', {
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_product_list_authenticated(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get('/api/products/')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_product_create(api_client, editor_user):
    api_client.force_authenticate(user=editor_user)
    data = {
        'name': 'New Product',
        'description': 'New description',
        'price': 25.00,
        'status': 'draft'
    }
    response = api_client.post('/api/products/', data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_public_product_list(api_client, editor_user, business):
    # Create approved product
    approved_product = Product.objects.create(
        name="Approved Product",
        price=30.00,
        status='approved',
        created_by=editor_user,
        business=business
    )
    response = api_client.get('/api/public/products/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == "Approved Product"
