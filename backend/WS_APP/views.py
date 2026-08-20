from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatRoom
import random
import string
import uuid


def ws_dashboard(request):
    rooms = ChatRoom.objects.none()

    if request.user.is_authenticated:
        rooms = ChatRoom.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'WS_APP/dashboard.html', {'rooms': rooms})


@login_required
def add_room(request):

    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to create a room.')
        return redirect('ws_dashboard')

    if request.method == 'POST':

        pin = request.POST.get('pin')

        # Check if pin is valid
        if not pin or len(pin) != 4 or not pin.isdigit():
            messages.error(request, 'Invalid PIN. Please enter a 4-digit number.')
            return redirect('ws_dashboard')

        # Generate fresh UUID for the new room
        uuid_str = str(uuid.uuid4())
            
        ChatRoom.objects.create(
            uuid=uuid_str, 
            pin=pin, 
            created_by=request.user
        )

        messages.success(request, f'Room "{uuid_str}" created successfully.')
        return redirect('ws_dashboard')
    
    return redirect('ws_dashboard')


@login_required
def delete_room(request, room_id):
    if request.method == 'POST':
        try:
            room = ChatRoom.objects.get(id=room_id)
            room.delete()
            messages.success(request, f'Room "{room.uuid}" deleted successfully.')
        except ChatRoom.DoesNotExist:
            messages.error(request, f'Room "{room.uuid}" does not exist.')
    return redirect('ws_dashboard')


@login_required
def room_auth_view(request):
    """
    Authenticate a user into a room using UUID + PIN.

    UUID may be supplied through the URL when joining from the dashboard.
    Otherwise the user enters the UUID manually.
    """

    room_uuid = request.GET.get('uuid', '').strip()

    if request.method == 'POST':
        room_uuid = request.POST.get('uuid', '').strip()
        pin = request.POST.get('pin', '').strip()

        if not room_uuid or not pin:
            messages.error(request, 'Room UUID and PIN are required.')
            return render(
                request,
                'WS_APP/room_auth.html',
                {'room_uuid': room_uuid}
            )

        try:
            room = ChatRoom.objects.get(uuid=room_uuid)
        except ChatRoom.DoesNotExist:
            messages.error(request, 'Room does not exist.')
            return render(
                request,
                'WS_APP/room_auth.html',
                {'room_uuid': room_uuid}
            )

        if pin != room.pin:
            messages.error(request, 'Incorrect PIN.')
            return render(
                request,
                'WS_APP/room_auth.html',
                {'room_uuid': room_uuid}
            )

        # Authentication successful
        authorized_rooms = request.session.get('authorized_rooms', [])

        if str(room.id) not in authorized_rooms:
            authorized_rooms.append(str(room.id))
            request.session['authorized_rooms'] = authorized_rooms

        return redirect('room_view', room_uuid=room.uuid)

    return render(
        request,
        'WS_APP/room_auth.html',
        {'room_uuid': room_uuid}
    )


@login_required
def room_view(request, room_uuid):
    try:
        room = ChatRoom.objects.get(uuid=room_uuid)
    except ChatRoom.DoesNotExist:
        messages.error(request, 'Room does not exist.')
        return redirect('ws_dashboard')

    authorized_rooms = request.session.get('authorized_rooms', [])

    if str(room.id) not in authorized_rooms:
        return redirect('room_auth')

    return render(
        request,
        'WS_APP/room.html',
        {'room': room}
    )