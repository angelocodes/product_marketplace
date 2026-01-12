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


@pytest.mark.django_db
def test_chatbot_functionality(api_client, editor_user, business):
    from chatbot.models import ChatMessage

    # Create approved product for context
    Product.objects.create(
        name="Test Product",
        description="A great test product",
        price=25.00,
        status='approved',
        created_by=editor_user,
        business=business
    )

    # Authenticate user
    api_client.force_authenticate(user=editor_user)

    # Test chat endpoint
    response = api_client.post('/api/chat/', {'message': 'What products are available?'})

    assert response.status_code == status.HTTP_201_CREATED
    assert 'user_message' in response.data
    assert 'ai_response' in response.data
    assert 'timestamp' in response.data
    assert response.data['user_message'] == 'What products are available?'

    # Check if message was saved
    messages = ChatMessage.objects.filter(user=editor_user)
    assert messages.count() == 1

    message = messages.first()
    assert message.user == editor_user
    assert message.user_message == 'What products are available?'
    assert len(message.ai_response) > 0

    # Test chat history
    history_response = api_client.get('/api/chat/history/')
    assert history_response.status_code == status.HTTP_200_OK
    assert len(history_response.data) == 1
    assert history_response.data[0]['user_message'] == 'What products are available?'


@pytest.mark.django_db
def test_chatbot_unauthenticated(api_client):
    # Test that unauthenticated users cannot access chat
    response = api_client.post('/api/chat/', {'message': 'Hello'})
    assert response.status_code == status.HTTP_403_FORBIDDEN

    history_response = api_client.get('/api/chat/history/')
    assert history_response.status_code == status.HTTP_403_FORBIDDEN
