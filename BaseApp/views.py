from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q

from . import models as m
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from conversation.models import Conversation
import UserApp.views as UserAppViews


def default(request):
    try:
        if request.session['business']:
            return redirect('my business newsfeed')
    except:
        if request.user.is_authenticated():
            # request.session['messages'] = request.user.appuser.user_app_conversations
            request.session['favorites'] = request.user.appuser.favorite_businesses.all()
            request.session['businesses'] = request.user.appuser.managed_businesses.all()
            return redirect('my user newsfeed')
        else:
            return render(request, 'BaseApp/login.html')


def refresh(request):
    if request.session['business']:
        business = request.session['business']
        num_conversations_business = m.AppConversation.objects.filter(business=business)
        num_disputes_user = m.Dispute.objects.filter(user=request.user.appuser)
    context = {

    }
    return render(request, 'BaseApp/refresh/refresh.html', context)


def search(request):
    query = request.GET.get('q')
    businesses_list = m.Business.objects.all()
    if query:
        businesses_list = businesses_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(managers__user__first_name__icontains=query) |
            Q(managers__user__last_name__icontains=query)
        )
    users_list = m.AppUser.objects.all()
    if query:
        users_list = users_list.filter(
            Q(gender__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    context = {
        'businesses_list': businesses_list,
        'users_list': users_list,
    }
    return render(request, 'BaseApp/search.html', context)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def maps(request):
    if request.POST:
        user_location = m.UserLocation()
        print(request.POST.get('lat') + request.POST.get('long') + request.POST.get('raw'))
        user_location.latitude = float(request.POST.get('lat'))
        user_location.longitude = float(request.POST.get('long'))
        user_location.raw = request.POST.get('raw')
        if request.user.appuser.userlocation:
            request.user.appuser.userlocation.delete()
            user_location.user = request.user.appuser
        else:
            user_location.user = request.user.appuser
        user_location.save()
    context = {

    }
    return render(request, 'BaseApp/Location/maps.html', context)