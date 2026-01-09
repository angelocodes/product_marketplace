from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Business, Product


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'business', 'role', 'is_active')
    list_filter = ('role', 'business', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Business Info', {'fields': ('business', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Business Info', {'fields': ('business', 'role')}),
    )


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status', 'business', 'created_by', 'created_at', 'image_preview')
    list_filter = ('status', 'business', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return "No image"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'admin':
            return qs
        return qs.filter(business=request.user.business)
