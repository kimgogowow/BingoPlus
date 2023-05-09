import re

from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from bingo_plus import forms
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from bingo_plus.models import Profile,GameEntry

import random
import json


def login_action(request):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_prof = Profile.objects.get(user = request.user)
            if user_prof.allow_to_create_new_game: 
                return render(request, 'templates/home.html',context)
            else:
                curr_game = user_prof.most_up_to_date_game
                curr_mode = curr_game.mode
                #to_ret = 'templates/game.html/?'
                #to_ret += 'mode=' + curr_mode
                context['mode'] = curr_mode
                return render(request, 'templates/game.html',context)


        else:
            context['form'] = forms.LoginForm()
            context['login_url'] = settings.LOGIN_URL
            return render(request, 'templates/login.html',context)

        #context['form'] = forms.LoginForm()
        
        #return render(request, 'templates/login.html', context)

    form = forms.LoginForm(request.POST)
    context['form'] = form
  

    if not form.is_valid():
        return render(request, 'templates/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    user_prof = Profile.objects.get(user = request.user)
    if user_prof.allow_to_create_new_game: 
        return render(request, 'templates/home.html',context)
    else:
        curr_game = user_prof.most_up_to_date_game
        curr_mode = curr_game.mode
        #to_ret = 'templates/game.html/?'
        #to_ret += 'mode=' + curr_mode
        context['mode'] = curr_mode
        return render(request, 'templates/game.html',context)

    # return redirect(reverse('game'))
    #return render(request, 'templates/home.html')


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}
    if request.method == 'GET':
        context['form'] = forms.RegisterForm()
        return render(request, 'templates/register.html', context)
    form = forms.RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'templates/register.html', context)

    if User.objects.filter(username=form.cleaned_data['username']).exists():
        context['error'] = "Username already exists!"
        return render(request, 'templates/register.html', context)

    if User.objects.filter(email=form.cleaned_data['email']).exists():
        context['error'] = "Email already exists!"
        return render(request, 'templates/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    # create a new profie for user
    # other attributes will be set by default
    new_profile = Profile(user=new_user)
    new_profile.save()

    login(request, new_user)
    # return redirect(reverse('home'))
    return render(request, 'templates/home.html')


@login_required
def get_profile(request):
    profile = Profile.objects.get(user=request.user)
    context = {'u': profile}
    return render(request, 'profile.html', context)

@login_required
def make_profile(request):
     # Check if the user already has a profile
     try:
         Profile.objects.get(user=request.user)
         return redirect('home')  # Redirect to home if profile already exists
     except Profile.DoesNotExist:
         pass

     profile = Profile(user=request.user)
     profile.save()

     return redirect('home')  # Redirect to home after profile creation


@login_required
def edit_profile_pic(request):
    if request.method == 'POST' and request.FILES['upload']:
        upload_pic = request.FILES['upload']
        # fss = FileSystemStorage()
        # file = fss.save(upload_pic.name, upload)
        # file_url = fss.url(file)

        profile = Profile.objects.get(user=request.user)
        profile.picture = upload_pic
        profile.pic_by_default = 0
        profile.save()
        context = {'u': profile}
    return render(request, 'profile.html', context)


@login_required
def edit_profile_text(request):

    edited_user = User.objects.get(id=request.user.id)
    new_firstname = request.POST['edit_firstname']
    new_lastname = request.POST['edit_lastname']

    pattern = '[~!#$%^&*()+{}\\[\\]:;,<>/?-]'

    edited_user.first_name = new_firstname
    edited_user.last_name = new_lastname

    context = {}

    if re.search(pattern, new_firstname) or re.search(pattern, new_lastname):
        profile = Profile.objects.get(user=request.user)
        context['u'] = profile
        context['error'] = "Names can not contain special characters!"
        return render(request, 'templates/profile.html', context)


    edited_user.save()

    profile = Profile.objects.get(user=request.user)
    context = {'u': profile}
    return render(request, 'profile.html', context)


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)
