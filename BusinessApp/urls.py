from django.conf.urls import include, url
from . import views

urlpatterns = [
    # Current Business
    url(r'^login/(?P<business_id>\d+)/$', views.login_business, name='login_business'),
    url(r'^logout/', views.logout_business, name='logout_business'),


    # News Feed
    url(r'^newsfeed/', views.news_feed, name='my business newsfeed'),


    # Conversations
    url(r'^conversation/list$', views.my_conversation_list, name='my business conversation list'),

    # Notifications
    url(r'^notification/list$', views.notification_list, name='my business notification list'),

    # Requests
    url(r'^request/list$', views.request_list, name='my business request list'),

    # Business
    url(r'^(?P<business_id>\d+)/details/$', views.business_details, name='business details'),
    url(r'^(?P<business_id>\d+)/delete/$', views.business_delete, name='business delete'),
    url(r'^create/$', views.business_create, name='business create'),
    url(r'^(?P<business_id>\d+)/update/$', views.business_update, name='business update'),
    url(r'^friends/$', views.friends_list, name='friends list'),



    # Catalog
    url(r'^(?P<business_id>\d+)/catalog/list/', views.catalog_list, name='catalog list'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/details$', views.catalog_details, name='catalog details'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/delete/$', views.catalog_delete, name='catalog delete'),
    url(r'^(?P<business_id>\d+)/catalog/create/$', views.catalog_create, name='catalog create'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/update/$', views.catalog_update, name='catalog update'),


    # Item
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/item/list$', views.item_list, name='item list'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/item/(?P<item_id>\d+)/details/$', views.item_details, name='item details'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/item/(?P<item_id>\d+)/delete/$', views.item_delete, name='item delete'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/item/create/$', views.item_create, name='item create'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/item/(?P<item_id>\d+)/update/$', views.item_update, name='item update'),


    # Service
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/service/list$', views.service_list, name='service list'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/service/(?P<service_id>\d+)/details/$', views.service_details, name='service details'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/service/(?P<service_id>\d+)/delete/$', views.service_delete, name='service delete'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/service/create/$', views.service_create, name='service create'),
    url(r'^(?P<business_id>\d+)/catalog/(?P<catalog_id>\d+)/service/(?P<service_id>\d+)/update/$', views.service_update, name='service update'),


    # Disputes
    url(r'^disputes/list$', views.dispute_list, name='my business dispute list'),
    url(r'^disputes/(?P<dispute_id>\d+)/details/', views.dispute_details, name='my business dispute details'),

    # Order
    url(r'^order/list$', views.order_list, name='my business order list'),
    url(r'^order/(?P<order_id>\d+)/details/', views.order_details, name='my business order details'),

    # Appointment
    url(r'^appointment/list/$', views.appointment_list, name='my business appointment list'),
    url(r'^appointment/(?P<appointment_id>\d+)/details/', views.appointment_details, name='my business appointment details'),


    # BaseBenefit
    url(r'^basebenefit/create/$', views.base_benefit_create, name='base benefit create'),
    url(r'^(?P<business_id>\d+)/basebenefit/list/$', views.base_benefit_list, name='base benefit list'),


    # DiscountBenefit
    url(r'^basebenefit/discountbenefit/create/$', views.discount_benefit_create, name='my business discount benefit create'),
    url(r'^basebenefit/discountbenefit/list/$', views.discount_benefit_list, name='my business discount benefit list'),
    url(r'^basebenefit/discountbenefit/(?P<benefit_id>\d+)/details/$', views.discount_benefit_details, name='my business discount benefit details'),


    # FriendBenefit
    url(r'^basebenefit/friendbenefit/create/$', views.friend_benefit_create, name='my business friend benefit create'),
    url(r'^basebenefit/friendbenefit/list/$', views.friend_benefit_list, name='my business friend benefit list'),
    url(r'^basebenefit/friendbenefit/(?P<benefit_id>\d+)/details/$', views.friend_benefit_details, name='my business friend benefit details'),

    # TicketBenefit
    url(r'^basebenefit/ticketbenefit/create/$', views.ticket_benefit_create, name='my business ticket benefit create'),
    url(r'^basebenefit/ticketbenefit/list/$', views.ticket_benefit_list, name='my business ticket benefit list'),
    url(r'^basebenefit/ticketbenefit/(?P<benefit_id>\d+)/details/$', views.ticket_benefit_details, name='my business ticket benefit details'),

    # Coupons
    url(r'^coupons/', views.coupon_list, name='my business coupon list'),


    # statistics
        url(r'^statistics/', views.statistics_charts, name='my business statistics list'),

]
