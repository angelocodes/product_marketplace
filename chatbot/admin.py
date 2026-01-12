from django.contrib import admin
from .models import ChatMessage


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'user_message', 'ai_response')
    readonly_fields = ('user', 'user_message', 'ai_response', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only superusers can see all messages, others see none
        if request.user.is_superuser:
            return qs
        return qs.none()


admin.site.register(ChatMessage, ChatMessageAdmin)
