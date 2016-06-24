from django.conf.urls import include, url
from . import views
from UserApp import views as v

urlpatterns = [
    url(r'^conversation/', include('conversation.urls')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', views.default, name='default'),
    url(r'^notifications/', include('notify.urls', 'notifications')),
    url(r'^refresh/', views.refresh, name='refresh'),
    url(r'^search/', views.search, name='search'),
    url(r'^maps/', views.maps, name='maps'),
]
