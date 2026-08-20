from django.contrib import admin
from .models import ChatRoom


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'pin', 'created_at')
    search_fields = ('id', 'pin')
