from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from BaseApp import models, forms
from django.db import IntegrityError
from datetime import datetime, timedelta, date
from conversation import models as con_m
import pytz
from notify.signals import notify
from django.contrib import messages


# Coupon
def assign_coupons_to_order(request, order):
    selected_money_coupons = request.POST.getlist('money_coupon_checks')
    for coupon_id in selected_money_coupons:
        coupon = models.MoneyCoupon.objects.get(pk=coupon_id)
        order.money_coupons.add(coupon)
    selected_item_coupons = selected_money_coupons = request.POST.getlist('item_coupon_checks')
    for coupon_id in selected_item_coupons:
        coupon = models.ItemCoupon.objects.get(pk=coupon_id)
        order.item_coupons.add(coupon)
    order.save()


def create_item_coupon(business, user, item):
    item_coupon = models.ItemCoupon()
    item_coupon.item = item
    item_coupon.user = user
    item_coupon.business = business
    item_coupon.save()


def create_money_coupon(business, user, money_reward):
    money_coupon = models.MoneyCoupon()
    money_coupon.money_reward = money_reward
    money_coupon.user = user
    money_coupon.business = business
    money_coupon.save()


def coupon_list(request):
    item_coupon_list = models.ItemCoupon.objects.filter(user=request.user.appuser)
    money_coupon_list = models.MoneyCoupon.objects.filter(user=request.user.appuser)
    unused_item_coupons_count = item_coupon_list.filter(is_used=False).count
    unused_money_coupons_count = money_coupon_list.filter(is_used=False).count
    context = {
        'item_coupon_list': item_coupon_list,
        'money_coupon_list': money_coupon_list,
        'unused_item_coupons_count': unused_item_coupons_count,
        'unused_money_coupons_count': unused_money_coupons_count,
    }
    return render(request, 'BaseApp/Coupon/list.html', context)


# Benefit
def get_order_benefits(order):
    for itemorder in order.item_orders.all():
        try:
            for benefit in order.user.user_discount_benefits.all():
                if benefit.discountbenefit.benefit.is_available() and itemorder.item.itemdiscount in benefit.discount_benefit.item_discounts.all():
                    discount = (itemorder.item.price - itemorder.item.itemdiscount.new_price) * itemorder.quantity
                    order.total -= discount
                    benefit.times_completed += 1
                    benefit.save()
            for benefit in order.user.user_ticket_benefits.all():
                if benefit.ticket_benefit.benefit.is_available():
                    if benefit.ticket_benefit.reward_type == 'item_reward':
                        if benefit.item_reward == itemorder.item:
                            benefit.purchases_made += itemorder.quantity
                            benefit.save()
                            while benefit.purchases_made >= benefit.ticket_benefit.required_punches:
                                benefit.times_completed += 1
                                benefit.purchases_made -= benefit.ticket_benefit.required_punches
                                create_item_coupon(order.business, order.user, itemorder.item)
                                benefit.save()
        except:
            pass
    for benefit in order.user.user_discount_benefits.all():
        if benefit.discount_benefit.benefit.is_available():
            if benefit.discount_benefit.discount_type == 'purchase_amount_discount':
                if order.total >= benefit.discount_benefit.purchase_amount_discount:
                    order.total -= benefit.discount_benefit.purchase_amount_discount
                    benefit.times_completed += 1
                    benefit.save()
                    order.save()
    for benefit in order.user.user_ticket_benefits.all():
        if benefit.ticket_benefit.benefit.is_available():
            if benefit.ticket_benefit.reward_type == 'money_reward':
                if order.total >= benefit.ticket_benefit.money_reward:
                    benefit.purchases_made += 1
                    benefit.save()
                    if benefit.purchases_made >= benefit.ticket_benefit.required_punches:
                        benefit.purchases_made = 0
                        benefit.times_completed += 1
                        create_money_coupon(order.business, order.user, benefit.ticket_benefit.money_reward)
                        benefit.save()


def use_order_benefits(order):
    for item_coupon in order.item_coupons.all():
        if item_coupon.is_used == False:
            order_item = models.ItemOrder()
            order_item.item = item_coupon.item
            order_item.quantity = 1
            order_item.order = order
            item_coupon.is_used=True
            item_coupon.save()
            order_item.save()

    for money_coupon in order.money_coupons.all():
        if money_coupon.is_used == False:
            order.total -= money_coupon.money_reward
            order.save()
            money_coupon.is_used = True
            money_coupon.save()








def create_conversation(object, business, app_user):
    try:
        app_conversation = models.AppConversation.objects.get(business=business, appuser=app_user)
    except ObjectDoesNotExist:
        conversation = con_m.Conversation()
        conversation.save()
        for manager in business.managers.all():
            conversation.users.add(manager.user)
        conversation.users.add(app_user.user)
        conversation.save()
        app_conversation = models.AppConversation()
        app_conversation.appuser = app_user
        app_conversation.business = business
        app_conversation.conversation = conversation
        app_conversation.is_regular = False
        app_conversation.save()
    object.appconversation = app_conversation
    object.save()


def news_feed(request):
    posts = models.BasePost.objects.all()
    app_user = request.user
    businesses = models.Business.objects.filter(managers=request.user.appuser)
    if request.GET.get('like'):
        post = models.BasePost.objects.get(pk=request.GET.get('like'))
        post.followers.add(request.user.appuser)
    if request.GET.get('dislike'):
        post = models.BasePost.objects.get(pk=request.GET.get('dislike'))
        post.followers.remove(request.user.appuser)
    context = {
        'posts': posts,
        'app_user': app_user,
        'businesses': businesses,
    }
    return render(request, 'BaseApp/NewsFeed/news_feed.html', context)


# Conversation
def my_conversation_list(request):
    context = {
    }
    return render(request, 'conversation/conversation_list.html', context)


# Notification
def notification_list(request):
    context = {

    }
    return render(request, 'BaseApp/Notification/list.html', context)


# Request
def handle_request_accepted(request):
    request_object = models.Request.objects.get(pk=request.POST.get('accept'))
    if request_object.type == 'friend':
        """
        type=friend, reciever=user, sender=user
        """
        request_object.reciever.friends.add(request_object.sender)
    elif request_object.type == 'follow':
        """
        type=follow, reciever=user, sender=business
        """
        request_object.sender.followers.add(request_object.reciever)
    elif request_object.type == 'manage':
        """
        type=manage, reciever=user, sender=business
        """
        request_object.sender.managers.add(request_object.reciever)
    else:
        """
        type=friend-benefit, reciever=user, sender=user, object=friend_benefit
        """
        request_object.reciever.friends.add(request_object.sender)
        friend_benefit = request_object.object
        if request_object.reciever not in friend_benefit.friends_added.all():
            friend_benefit.counter += 1
            business = friend_benefit.friend_benefit.benefit.business
            business.followers.add(request_object.reciever)
            business.save()
            friend_benefit.friends_added.add(request_object.reciever)
            if friend_benefit.counter >= friend_benefit.friend_benefit.required_friends:
                friend_benefit.times_completed += 1
                friend_benefit.counter = 0
                if friend_benefit.friend_benefit.reward_type == 'item_reward':
                    create_item_coupon(friend_benefit.friend_benefit.benefit.business, friend_benefit.user,
                                       friend_benefit.item_reward)
                elif friend_benefit.friend_benefit.reward_type == 'money_reward':
                    create_item_coupon(friend_benefit.friend_benefit.benefit.business, friend_benefit.user,
                                       friend_benefit.money_reward)
            friend_benefit.save()
    request_object.status = 'accepted'
    request_object.save()


def handle_request_rejected(request):
    request_object = models.Request.objects.get(pk=request.POST.get('reject'))
    request_object.status = 'rejected'
    request_object.save()


def request_list(request):
    if request.POST.get('accept'):
        handle_request_accepted(request)
    elif request.POST.get('reject'):
        handle_request_rejected(request)
    recieved_requests = models.Request.objects.filter(reciever_object_id=request.user.appuser.id,
                                                      reciever_content_type=models.ContentType.objects.get_for_model(
                                                          models.AppUser))
    sent_requests = models.Request.objects.filter(sender_object_id=request.user.appuser.id,
                                                  sender_content_type=models.ContentType.objects.get_for_model(
                                                      models.AppUser))
    sent_pending_count = sent_requests.filter(status='pending').count
    recieved_pending_count = recieved_requests.filter(status='pending').count
    # recieved_requests = models.Request.objects.filter(reciever_content_object=request.user.appuser)
    # sent_requests = models.Request.objects.filter(sender_content_object=request.user.appuser)
    context = {
        'sent_pending_count': sent_pending_count,
        'recieved_pending_count': recieved_pending_count,
        'recieved_requests': recieved_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'BaseApp/Request/list.html', context)


# Order
def order_list(request):
    objects_list = models.Order.objects.filter(user=request.user.appuser)
    context = {
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Order/list.html', context)


def order_details(request, order_id):
    object = get_object_or_404(models.Order, pk=order_id)
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/Order/details.html', context)


def order_create(request):
    business_id = request.GET.get('order_business_id')
    business = models.Business.objects.get(pk=business_id)
    items_list = models.Item.objects.all().filter(catalog__business__id=business_id)
    form = forms.OrderForm(request.POST or None)
    address_form = forms.AddressForm(request.POST or None)
    if form.is_valid() & address_form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user.appuser
        business = get_object_or_404(models.Business, id=int(request.GET.get('order_business_id')))
        instance.business = business
        instance.save()
        total = 0
        for item in items_list:
            item_id = 'item_' + str(item.id)
            quantity = int(request.POST[item_id])
            if quantity > 0:
                total += (item.price * quantity)
                item_order = models.ItemOrder()
                item_order.item = item
                item_order.order = instance
                item_order.quantity = quantity
                item_order.save()
        instance.total = total
        address = address_form.save(commit=False)
        address.raw = request.POST.get('address_raw')
        address.save()
        instance.address = address
        create_conversation(instance, business, request.user.appuser)
        instance.save()

        get_order_benefits(instance)
        assign_coupons_to_order(request, instance)
        use_order_benefits(instance)

        managers = models.User.objects.filter(appuser__in=business.managers.all())
        notify.send(request.user, recipient_list=list(managers.all()), actor=request.user.appuser,
                    verb='created new order.', target=instance, nf_type='create')
        return redirect('my user order list')
    context = {
        'items_list': items_list,
        'form': form,
        'address_form': address_form,
        'business': business,
    }
    return render(request, 'BaseApp/Order/create.html', context)


# Dispute
def dispute_list(request):
    objects_list = request.user.appuser.user_disputes.all()
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/Dispute/list.html', context)


def dispute_details(request, dispute_id):
    object = request.user.appuser.user_disputes.get(pk=dispute_id)
    context = {
        "object": object,
    }
    return render(request, 'BaseApp/Dispute/details.html', context)


def dispute_delete(request, dispute_id):
    object = request.user.appuser.user_disputes.get(pk=dispute_id)
    object.conversation.delete()
    object.delete()
    return redirect('my user dispute list')


def dispute_create(request):
    form = forms.DisputeForm(request.POST or None)
    try:
        order = request.user.appuser.user_orders.get(pk=request.GET.get('order_id'))
        appointment = None
    except:
        order = None
        appointment = request.user.appuser.user_appointments.get(pk=request.GET.get('appointment_id'))
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user.appuser
        if order:
            instance.order = order
            instance.business = order.business
        else:
            instance.appointment = appointment
            instance.business = appointment.business
        create_conversation(instance, instance.business, instance.user)
        instance.save()
        managers = models.User.objects.filter(appuser__in=instance.business.managers.all())
        notify.send(request.user, recipient_list=list(managers.all()), actor=request.user.appuser,
                    verb='created new dispute.', target=instance, nf_type='create')
        return redirect('my user dispute list')

    context = {
        'form': form
    }
    return render(request, 'BaseApp/Dispute/create.html', context)


# User
def user_details(request, user_id):
    var = get_object_or_404(models.AppUser, pk=user_id)
    if request.POST.get('add friend'):
        user = models.AppUser.objects.get(pk=request.POST.get('add friend'))
        request_object = models.Request(sender_content_object=request.user.appuser, reciever_content_object=user,
                                        type="friend")
        try:
            request_object.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Friend request already exists.')
            return redirect(user.get_absolute_url())
    if request.POST.get('invite to follow'):
        user = models.AppUser.objects.get(pk=request.POST.get('invite to follow'))
        request_object = models.Request(sender_content_object=request.session['business'], reciever_content_object=user,
                                        type="follow")
        try:
            request_object.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Request already exists.')
    if request.POST.get('add manager'):
        user = models.AppUser.objects.get(pk=request.POST.get('add manager'))
        request_object = models.Request(reciever_content_object=user, sender_content_object=request.session['business'], type='manage')
        try:
            request_object.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Request already exists.')

    context = {
        'var': var,
    }
    return render(request, 'BaseApp/AppUser/details.html', context)


# Appointment
def create_appointment_select_service_and_date(request):
    if request.GET.get('business_id'):
        request.session['appointment_business_id'] = request.GET.get('business_id')

    if request.GET.get('service_id') and request.GET.get('date'):
        request.session['appointment_service_id'] = request.GET.get('service_id')
        request.session['appointment_date'] = request.GET.get('date')
        return create_appointment_select_time(request)

    if request.GET.get('date_time'):
        object = request.GET.get('date_time')
        date_time = datetime.strptime(object, "%d/%m/%Y %H:%M")
        business_id = request.session['appointment_business_id']
        business = models.Business.objects.all().get(pk=business_id)
        service_id = request.session['appointment_service_id']
        service = models.Service.objects.all().get(pk=service_id)
        appointment = models.Appointment()
        appointment.service = service
        appointment.business = business
        appointment.date = date_time
        appointment.user = request.user.appuser
        try:
            appointment.total = service.servicediscount.new_price
        except:
            appointment.total = service.price
        appointment.save()
        create_conversation(appointment, business, request.user.appuser)
        managers = models.User.objects.filter(appuser__in=appointment.business.managers.all())
        notify.send(request.user, recipient_list=list(managers.all()), actor=request.user.appuser,
                    verb='created new appointment.', target=appointment, nf_type='create')
        appointment.save()
        return redirect('my user appointment list')

    service_list = models.Service.objects.all().filter(catalog__business__id=request.session['appointment_business_id'])
    context = {
        'service_list': service_list,
    }
    return render(request, 'BaseApp/Appointment/create_1.html', context)


def create_appointment_select_time(request):
    date = datetime.strptime(request.session['appointment_date'], "%Y-%m-%d").date()
    business_id = request.session['appointment_business_id']
    service_id = request.session['appointment_service_id']
    service = models.Service.objects.all().get(pk=service_id)
    opening_hour = models.OpeningHours.objects.all().get(business__id=business_id, weekday=date.weekday())
    existing_appoointments = models.Appointment.objects.all().filter(date__date=date)
    open = opening_hour.from_hour
    close = opening_hour.to_hour
    delta = timedelta(minutes=30)
    utc = pytz.UTC
    date_open = utc.localize(datetime.combine(date, open))
    date_close = utc.localize(datetime.combine(date, close))
    hours = {}
    i = 0
    while date_open < date_close:
        if existing_appoointments:
            for appointment in existing_appoointments:
                if date_open < appointment.date + appointment.service.duration and \
                                        date_open + service.duration > appointment.date:
                    hours.update({'open' + str(i): (date_open, False, date_open + delta)})
                    break
                else:
                    hours.update({'open' + str(i): (date_open, True, date_open + delta)})
        else:
            hours.update({'open' + str(i): (date_open, True, date_open + delta)})
        i += 1
        date_open += delta
    sorted_hours = sorted(hours.items(), key=lambda x: x[1])
    context = {
        'opening_hour': open,
        'closing_hour': close,
        'hours': sorted_hours,
        'appointments': existing_appoointments,
    }
    return render(request, 'BaseApp/Appointment/create_2.html', context)


def appointment_list(request):
    objects_list = models.Appointment.objects.filter(user=request.user.appuser)
    context = {
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Appointment/list.html', context)


def appointment_details(request, appointment_id):
    object = get_object_or_404(models.Appointment, pk=appointment_id)
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/Appointment/details.html', context)


# Friend Benefit
def friend_benefit_list(request):
    objects_list = models.UserFriendBenefit.objects.filter(user=request.user.appuser)
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/BaseBenefit/FriendBenefit/list.html', context)


def friend_benefit_details(request, benefit_id):
    object = get_object_or_404(models.UserFriendBenefit, pk=benefit_id)
    if request.POST.get('benefit'):
        friend = models.AppUser.objects.get(pk=request.POST.get('benefit'))
        request_object = models.Request(sender_content_object=request.user.appuser, reciever_content_object=friend,
                                        object_content_object=object, type='follow-benefit')
        request_object.save()
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/BaseBenefit/FriendBenefit/details.html', context)


# TicketBenefit
def ticket_benefit_list(request):
    objects_list = models.UserTicketBenefit.objects.filter(user=request.user.appuser)
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/BaseBenefit/TicketBenefit/list.html', context)


def ticket_benefit_details(request, benefit_id):
    object = get_object_or_404(models.UserTicketBenefit, pk=benefit_id)
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/BaseBenefit/TicketBenefit/details.html', context)


# DiscountBenefit
def discount_benefit_list(request):
    objects_list = models.UserDiscountBenefit.objects.filter(user=request.user.appuser)
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/BaseBenefit/DiscountBenefit/list.html', context)


def discount_benefit_details(request, benefit_id):
    object = get_object_or_404(models.UserDiscountBenefit, pk=benefit_id)
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/BaseBenefit/DiscountBenefit/details.html', context)


