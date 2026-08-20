from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.ws_dashboard, name='ws_dashboard'),
    path('add-room/', views.add_room, name='add_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),

    path('join/', views.room_auth_view, name='room_auth'),
    path('room/<str:room_uuid>/', views.room_view, name='room_view'),
]
