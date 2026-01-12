from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user_message', 'ai_response', 'timestamp']
        read_only_fields = ['id', 'ai_response', 'timestamp']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
