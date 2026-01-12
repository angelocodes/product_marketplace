import os
from pathlib import Path
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from google import genai
from django.conf import settings
from dotenv import load_dotenv
from api.models import Product
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatRequestSerializer

# Load environment variables
env_path = Path(settings.BASE_DIR) / 'chatbot' / '.env'
load_dotenv(env_path)


def get_product_context():
    """Get approved products data for AI context"""
    products = Product.objects.filter(status='approved').select_related('business')
    context = "Available products:\n"
    for product in products:
        context += f"- {product.name}: {product.description} (${product.price}) by {product.business.name}\n"
    return context


def generate_ai_response(user_message, product_context):
    """Generate AI response using Gemini API"""
    try:
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "Error: Gemini API key not configured."

        
        client = genai.Client(api_key=api_key)

        # The prompt for context to give to LLM
        prompt = f"""You are a helpful product marketplace assistant. Use the following product information to answer questions:

{product_context}

User question: {user_message}

Please provide a helpful, accurate response based on the available products. If the user asks about products not in the list, mention that only approved products are shown."""

        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error generating AI response: {str(e)}"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    """Handle chat messages and generate AI responses"""
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_message = serializer.validated_data['message']

    product_context = get_product_context()

    ai_response = generate_ai_response(user_message, product_context)

    # Save the chat message
    chat_message = ChatMessage.objects.create(
        user=request.user,
        user_message=user_message,
        ai_response=ai_response
    )

    # Return response
    response_serializer = ChatMessageSerializer(chat_message)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history_view(request):
    """Get user's chat history"""
    messages = ChatMessage.objects.filter(user=request.user)
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)
