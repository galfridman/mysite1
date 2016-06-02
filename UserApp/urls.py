from django.conf.urls import include, url
from . import views

urlpatterns = [
    # url(r'^show_user/(?P<user_id>\d+)/$', views.user_details, name='user_profile'),
    url(r'^comments/', include('django_comments.urls')),


    # News Feed
    url(r'^newsfeed/', views.news_feed, name='my user newsfeed'),


    # Profile
    url(r'^(?P<user_id>\d+)/details/$', views.user_details, name='user details'),


    # Conversations
    url(r'^conversation/list$', views.my_conversation_list, name='my user conversation list'),


    # Notifications
    url(r'^notification/list$', views.notification_list, name='my user notification list'),

    # Requests
    url(r'^request/list$', views.request_list, name='my user request list'),


    # Disputes
    url(r'^disputes/list$', views.dispute_list, name='my user dispute list'),
    url(r'^disputes/(?P<dispute_id>\d+)/details/', views.dispute_details, name='my user dispute details'),
    url(r'^disputes/(?P<dispute_id>\d+)/delete/', views.dispute_delete, name='my user dispute delete'),
    url(r'^disputes/create/', views.dispute_create, name='my user dispute create'),


    # Order
    url(r'^order/list$', views.order_list, name='my user order list'),
    url(r'^order/(?P<order_id>\d+)/details/', views.order_details, name='my user order details'),
    url(r'^order/create/$', views.order_create, name='my user order create'),


    # Appointment
    url(r'^appointment/create/$', views.create_appointment_select_service_and_date, name='my user appointment create'),
    url(r'^appointment/list/$', views.appointment_list, name='my user appointment list'),
    url(r'^order/(?P<appointment_id>\d+)/details/', views.appointment_details, name='my user appointment details'),


    # DiscountBenefit
    url(r'^basebenefit/discountbenefit/list/$', views.discount_benefit_list, name='my user discount benefit list'),
    url(r'^basebenefit/discountbenefit/(?P<benefit_id>\d+)/details/$', views.discount_benefit_details, name='my user discount benefit details'),


    # FriendBenefit
    url(r'^basebenefit/friendbenefit/list/$', views.friend_benefit_list, name='my user friend benefit list'),
    url(r'^basebenefit/friendbenefit/(?P<benefit_id>\d+)/details/$', views.friend_benefit_details, name='my user friend benefit details'),


    # TicketBenefit
    url(r'^basebenefit/ticketbenefit/list/$', views.ticket_benefit_list, name='my user ticket benefit list'),
    url(r'^basebenefit/ticketbenefit/(?P<benefit_id>\d+)/details/$', views.ticket_benefit_details, name='my user ticket benefit details'),


    # Coupons
    url(r'^coupons/', views.coupon_list, name='my user coupon list'),

]

