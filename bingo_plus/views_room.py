from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from bingo_plus import forms


from bingo_plus.models import Profile, Room

@login_required
def create_room(request):
    context = {}
    return render(request, 'room_size.html', context)

@login_required
def enter_room(request):
    context = {}
    return render(request, 'room_token.html', context)

@login_required
def set_roomsize(request):
    if 'size_input' not in request.POST:
        print('error_size')

    new_room = Room()
    room_size = request.POST['size_input']
    print(room_size)
    context = {}
    return render(request, 'room_mode.html', context)

@login_required
def waiting_room_action(request):
    # user http json and js to generate a list of users
    # when the number meets the set of a room
    # do something
    context = {}
    return render(request, 'room_waiting.html', context)

def waiting_room_js_action(request):
    print('waiting_room_js_action')

@login_required
def check_token(request):
    if 'token_input' not in request.POST:
        print('error_token')
        
    token_input = request.POST['token_input']
    print(token_input)
    # do some checks
    context = {}
    return render(request, 'room_waiting.html', context)
