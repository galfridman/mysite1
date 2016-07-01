from datetime import datetime, date, timedelta
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from notify.signals import notify
from BaseApp import models, forms
from django.contrib import messages


def login_business(request, business_id):
    business = get_object_or_404(models.Business, id=business_id)
    if request.user.appuser not in business.managers.all():
        return redirect('default')
    request.session['business'] = business
    return redirect('my business newsfeed')


def logout_business(request):
    del request.session['business']
    return redirect('default')


def news_feed(request):
    posts = request.session['business'].business_base_posts.all().order_by('-is_important', 'changed_at')[:5]
    form = forms.PostForm((request.POST or None))
    if form.is_valid():
        instance = form.save(commit=False)
        instance.business = request.session['business']
        instance.save()
        followers = models.User.objects.filter(appuser__in=instance.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=instance.business,
                        verb='published new post.',
                        target=instance, nf_type='create')

        return redirect('default')
    if request.GET.get('like'):
        post = models.BasePost.objects.get(pk=request.GET.get('like'))
        post.followers.add(request.user.appuser)
    if request.GET.get('dislike'):
        post = models.BasePost.objects.get(pk=request.GET.get('dislike'))
        post.followers.remove(request.user.appuser)
    context = {
        'form': form,
        'posts': posts,
    }
    return render(request, 'BaseApp/NewsFeed/news_feed.html', context)


# Coupon
def coupon_list(request):
    item_coupon_list = models.ItemCoupon.objects.filter(business=request.session['business'])
    money_coupon_list = models.MoneyCoupon.objects.filter(business=request.session['business'])
    unused_item_coupons_count = item_coupon_list.filter(is_used=False).count
    unused_money_coupons_count = money_coupon_list.filter(is_used=False).count
    context = {
        'item_coupon_list': item_coupon_list,
        'money_coupon_list': money_coupon_list,
        'unused_item_coupons_count': unused_item_coupons_count,
        'unused_money_coupons_count': unused_money_coupons_count,
    }
    return render(request, 'BaseApp/Coupon/list.html', context)


# Conversation
def my_conversation_list(request):
    # appconversations = models.AppConversation.all().filter(business=request.session['business'])
    context = {
        # "appconversations": appconversations,
    }
    return render(request, 'conversation/conversation_list.html', context)


# Notification
def notification_list(request):
    context = {

    }
    return render(request, 'BaseApp/Notification/list.html', context)


# Request
def handle_request_accepted(request):
    request_object = models.Request(pk=request.POST.get('accepted'))
    if request_object.type == 'friend':
        """
        type=friend, reciever=user, sender=user
        """
        request_object.reciever.friends.add(request_object.sender)
    elif request_object.type == 'follow':
        """
        type=follow, reciever=user, sender=user
        """
        request_object.sender.followers.add(request_object.reciever)
    elif request_object.type == 'manage':
        """
        type=manage, reciever=user, sender=business
        """
        request_object.sender.managers.add(request_object.reciever)
    else:
        """
        type=friend-benefit, reciever=user, sender=user
        """
        request_object.reciever.friends.add(request_object.sender)
        for benefit in request_object.sender.user_friend_benefits:
            benefit.friends_added += 1
            if benefit.friends_added == benefit.friend_benefit.required_friends:
                benefit.friends_added = 0
            benefit.save()
            # give coupon


def handle_request_rejected(request):
    request_object = models.Request(pk=request.POST.get('rejected'))
    request_object.status = 'rejected'


def request_list(request):
    if request.POST.get('accept'):
        handle_request_accepted(request)
    elif request.POST.get('reject'):
        handle_request_rejected(request)
    recieved_requests = models.Request.objects.filter(reciever_object_id=request.session['business'].id,
                                                      reciever_content_type=models.ContentType.objects.get_for_model(
                                                          models.Business))
    sent_requests = models.Request.objects.filter(sender_object_id=request.session['business'].id,
                                                  sender_content_type=models.ContentType.objects.get_for_model(
                                                      models.Business))
    sent_pending_count = sent_requests.filter(status='pending').count
    recieved_pending_count = recieved_requests.filter(status='pending').count
    context = {
        'sent_pending_count': sent_pending_count,
        'recieved_pending_count': recieved_pending_count,
        'recieved_requests': recieved_requests,
        'sent_requests': sent_requests,
    }
    return render(request, 'BaseApp/Request/list.html', context)


# Dispute
def dispute_list(request):
    objects_list = models.Dispute.objects.filter(business=request.session['business'])
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/Dispute/list.html', context)


def dispute_details(request, dispute_id):
    object = request.session['business'].business_disputes.get(pk=dispute_id)
    if request.GET.get('accept'):
        object.status = 'accepted'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='accepted your order.', target=object, nf_type='accept')
    elif request.GET.get('reject'):
        object.status = 'rejected'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='rejected your order.', target=object, nf_type='reject')
    context = {
        "object": object,
    }
    return render(request, 'BaseApp/Dispute/details.html', context)


def business_details(request, business_id):
    object = get_object_or_404(models.Business, pk=business_id)
    if request.GET.get('follow'):
        follow_business(request, request.GET.get('follow'))
    if request.GET.get('unfollow'):
        unfollow_business(request, request.GET.get('unfollow'))
    if request.POST.get('manager'):
        new_manager = models.AppUser.objects.get(pk=request.POST.get('manager'))
        request_object = models.Request(reciever_content_object=new_manager,
                                        sender_content_object=request.session['business'], type='manage')
        try:
            request_object.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Request already exists.')
    context = {
        'object': object,
        'business_id': int(business_id),
    }
    return render(request, 'BaseApp/Business/details.html', context)


def follow_business(request, business_id):
    business = models.Business.objects.get(pk=business_id)
    if request.user.appuser not in business.followers.all():
        business.followers.add(request.user.appuser)
        managers = models.User.objects.filter(appuser__in=business.managers.all())
        notify.send(request.user, recipient_list=list(managers.all()), actor=request.user.appuser,
                    verb='started following your business.', target=business, nf_type='followed_by_one_user')


def friends_list(request):
    objects_list = request.user.appuser.friends.all()
    if request.POST.get('manager'):
        new_manager = models.AppUser.objects.get(pk=request.POST.get('manager'))
        request_object = models.Request(reciever_content_object=new_manager,
                                        sender_content_object=request.session['business'], type='manage')
        request_object.save()
        return redirect('my business request list')
    elif request.POST.get('benefit'):
        benefit_friend = models.AppUser.objects.get(pk=request.POST.get('benefit'))
        request_object = models.Request(reciever_content_object=benefit_friend,
                                        sender_content_object=request.user.appuser, type='follow-benefit')
        request_object.save()
        return redirect('my user request list')
    context = {
        'friends_list': objects_list,
    }
    return render(request, 'BaseApp/Business/friends_list.html', context)


def unfollow_business(request, business_id):
    business = models.Business.objects.get(pk=business_id)
    if request.user.appuser in business.followers.all():
        business.followers.remove(request.user.appuser)
        managers = models.User.objects.filter(appuser__in=business.managers.all())
        notify.send(request.user, recipient_list=list(managers.all()), actor=request.user.appuser,
                    verb='stopped following your business.', target=business, nf_type='followed_by_one_user')


def business_delete(request, business_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    object = request.session['business']
    object.delete()
    return redirect('logout_business')


def business_create(request):
    form = forms.BusinessForm(request.POST or None, request.FILES or None)
    address_form = forms.AddressForm(request.POST or None)
    if form.is_valid() and address_form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        instance.managers.add(request.user.appuser)
        instance.save()
        address = address_form.save(commit=False)
        address.raw = request.POST.get('address_raw')
        address.save()
        instance.address = address
        instance.save()
        return redirect('default')
    context = {
        'address_form': address_form,
        'form': form,
    }
    return render(request, 'BaseApp/Business/create.html', context)


def business_update(request, business_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    instance = get_object_or_404(models.Business, pk=business_id)
    form = forms.BusinessForm(request.POST or None, request.FILES or None, instance=instance)
    address_form = forms.AddressForm(request.POST or None)
    print("@@@@@@@@@@@@@@@@@@@", request.POST, "@@@@@@@@@@@@@@@@@@@@@@@@")
    if form.is_valid() and address_form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        address = address_form.save(commit=False)
        address.raw = request.POST.get('address_raw')
        address.save()
        instance.address = address
        instance.save()
        return redirect('default')
    context = {
        'business_id': int(business_id),
        'form': form,
        'address_form': address_form,
    }
    return render(request, 'BaseApp/Business/update.html', context)


# Catalog
def catalog_list(request, business_id):
    objects_list = models.Catalog.objects.filter(business__id=business_id)
    context = {
        'business_id': int(business_id),
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Catalog/list.html', context)


def catalog_details(request, business_id, catalog_id):
    object = get_object_or_404(models.Catalog, pk=catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'object': object,
    }
    return render(request, 'BaseApp/Catalog/details.html', context)


def catalog_delete(request, business_id, catalog_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    object = get_object_or_404(models.Catalog, pk=catalog_id)
    object.delete()
    return redirect('catalog list', business_id)


def catalog_create(request, business_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    business = get_object_or_404(models.Business, pk=business_id)
    form = forms.CatalogForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.business = business
        instance.save()
        followers = models.User.objects.filter(appuser__in=business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=business, verb='created a new catalog.',
                        target=instance, nf_type='create')
        return redirect('catalog list', business_id)
    context = {
        'business_id': int(business_id),
        'form': form,
    }
    return render(request, 'BaseApp/Catalog/create.html', context)


def catalog_update(request, business_id, catalog_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    instance = get_object_or_404(models.Catalog, pk=catalog_id)
    form = forms.CatalogForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.save()
        return redirect('default')
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'form': form
    }
    return render(request, 'BaseApp/Catalog/update.html', context)


# Item
def item_list(request, business_id, catalog_id):
    objects_list = models.Item.objects.filter(catalog__id=catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Item/list.html', context)


def item_details(request, business_id, catalog_id, item_id):
    object = get_object_or_404(models.Item, pk=item_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'item_id': int(item_id),
        'object': object,
    }
    return render(request, 'BaseApp/Item/details.html', context)


def item_delete(request, business_id, catalog_id, item_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    object = get_object_or_404(models.Item, pk=item_id)
    object.delete()
    return redirect('catalog list', business_id)


def item_create(request, business_id, catalog_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    catalog = get_object_or_404(models.Catalog, pk=catalog_id)
    form = forms.ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.catalog = catalog
        instance.save()
        followers = models.User.objects.filter(appuser__in=catalog.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=catalog.business,
                        verb='created a new item.',
                        target=instance, nf_type='create')
        return redirect('item list', business_id, catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'form': form,
    }
    return render(request, 'BaseApp/Item/create.html', context)


def item_update(request, business_id, catalog_id, item_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    instance = get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.save()
        return redirect('item list', business_id, catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'item_id': int(item_id),
        'form': form
    }
    return render(request, 'BaseApp/Item/update.html', context)


# Service
def service_list(request, business_id, catalog_id):
    objects_list = models.Service.objects.filter(catalog__id=catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Service/list.html', context)


def service_details(request, business_id, catalog_id, service_id):
    object = get_object_or_404(models.Service, pk=service_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'service_id': int(service_id),
        'object': object,
    }
    return render(request, 'BaseApp/Service/details.html', context)


def service_delete(request, business_id, catalog_id, service_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    object = get_object_or_404(models.Service, pk=service_id)
    object.delete()
    return redirect('catalog list', business_id)


def service_create(request, business_id, catalog_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    catalog = get_object_or_404(models.Catalog, pk=catalog_id)
    form = forms.ServiceForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.catalog = catalog
        instance.save()
        followers = models.User.objects.filter(appuser__in=catalog.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=catalog.business,
                        verb='created a new service.',
                        target=instance, nf_type='create')
        return redirect('service list', business_id, catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'form': form,
    }
    return render(request, 'BaseApp/Service/create.html', context)


def service_update(request, business_id, catalog_id, service_id):
    if str(request.session['business'].id) != business_id:
        return redirect('default')
    instance = get_object_or_404(models.Service, pk=service_id)
    form = forms.ServiceForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.changed_at = datetime.now()
        instance.save()
        return redirect('service list', business_id, catalog_id)
    context = {
        'business_id': int(business_id),
        'catalog_id': int(catalog_id),
        'service_id': int(service_id),
        'form': form
    }
    return render(request, 'BaseApp/Service/update.html', context)


# Order
def order_list(request):
    objects_list = models.Order.objects.filter(business=request.session['business'])
    context = {
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Order/list.html', context)


def order_details(request, order_id):
    object = get_object_or_404(models.Order, pk=order_id)
    if request.GET.get('accept'):
        object.status = 'accepted'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='accepted your order.', target=object, nf_type='accept')
    elif request.GET.get('reject'):
        object.status = 'rejected'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='rejected your order.', target=object, nf_type='reject')
    context = {
        'order_id': int(order_id),
        'object': object,
    }
    return render(request, 'BaseApp/Order/details.html', context)


# Appointment
def appointment_list(request):
    objects_list = models.Appointment.objects.filter(business=request.session['business'])
    context = {
        'objects_list': objects_list,
    }
    return render(request, 'BaseApp/Appointment/list.html', context)


def appointment_details(request, appointment_id):
    object = get_object_or_404(models.Appointment, pk=appointment_id)
    if request.GET.get('accept'):
        object.status = 'accepted'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='accepted your order.', target=object, nf_type='accept')
    elif request.GET.get('reject'):
        object.status = 'rejected'
        object.save()
        notify.send(request.user, recipient=object.user.user, actor=object.business,
                    verb='rejected your order.', target=object, nf_type='reject')
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/Appointment/details.html', context)


# BaseBenefits
def base_benefit_create(request):
    form = forms.BaseBenefitForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        request.session['BaseBenefit'] = instance
        if instance.type == "friend":
            return redirect('my business friend benefit create')
        elif instance.type == "ticket":
            return redirect('my business ticket benefit create')
        else:
            return redirect('my business discount benefit create')
    context = {
        'form': form,
    }
    return render(request, 'BaseApp/BaseBenefit/create.html', context)


def base_benefit_list(request, business_id):
    business = get_object_or_404(models.Business, pk=business_id)
    discount_benefit_list_1 = models.DiscountBenefit.objects.filter(benefit__business=business) \
        .filter(benefit__ending_date__gte=date.today())
    friend_benefit_list_1 = models.FriendBenefit.objects.filter(benefit__business=business) \
        .filter(benefit__ending_date__gte=date.today())
    ticket_benefit_list_1 = models.TicketBenefit.objects.filter(benefit__business=business) \
        .filter(benefit__ending_date__gte=date.today())
    if request.POST.get('discount_benefit'):
        discount_benefit = discount_benefit_list_1.get(pk=request.POST.get('discount_benefit'))
        new_benefit = models.UserDiscountBenefit()
        new_benefit.discount_benefit = discount_benefit
        new_benefit.user = request.user.appuser
        try:
            new_benefit.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Benefit already in your benefits.')

    elif request.POST.get('friend_benefit'):
        friend_benefit = friend_benefit_list_1.get(pk=request.POST.get('friend_benefit'))
        new_benefit = models.UserFriendBenefit()
        new_benefit.friend_benefit = friend_benefit
        new_benefit.user = request.user.appuser
        try:
            new_benefit.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Benefit already in your benefits.')

    elif request.POST.get('ticket_benefit'):
        ticket_benefit = ticket_benefit_list_1.get(pk=request.POST.get('ticket_benefit'))
        new_benefit = models.UserTicketBenefit()
        new_benefit.ticket_benefit = ticket_benefit
        new_benefit.user = request.user.appuser
        try:
            new_benefit.save()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'Benefit already in your benefits.')

    context = {
        'discount_benefit_list': discount_benefit_list_1,
        'friend_benefit_list': friend_benefit_list_1,
        'ticket_benefit_list': ticket_benefit_list_1,
        'business_id': int(business_id)
    }
    return render(request, 'BaseApp/BaseBenefit/list.html', context)


# FriendBenefit
def friend_benefit_create(request):
    form = forms.FriendBenefitForm(request.POST or None)
    items = models.Item.objects.filter(catalog__business__id=request.session['business'].id)
    services = models.Service.objects.filter(catalog__business__id=request.session['business'].id)
    if form.is_valid():
        instance = form.save(commit=False)
        base_benefit = request.session['BaseBenefit']
        base_benefit.business = request.session['business']
        base_benefit.save()
        instance.benefit = base_benefit
        instance.save()
        if instance.reward_type == 'item_reward':
            print()
            selected = request.POST.get('item_checks')
            for item in items:
                if str(item.id) == selected:
                    instance.item_reward = item
        elif instance.reward_type == 'service_reward':
            selected = request.POST.get('service_checks')
            for service in services:
                if str(service.id) == selected:
                    instance.service_reward = service
        else:
            money_reward = request.POST.get('money_reward')
            instance.money_reward = money_reward
        instance.save()
        followers = models.User.objects.filter(appuser__in=base_benefit.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=base_benefit.business,
                        verb='created a new friend benefit.', target=instance, nf_type='create')
        return redirect('default')
    context = {
        'form': form,
        'items': items,
        'services': services,
    }
    return render(request, 'BaseApp/BaseBenefit/FriendBenefit/create.html', context)


def friend_benefit_list(request):
    objects_list = models.UserFriendBenefit.objects.filter(
        friend_benefit__benefit__business=request.session['business'])
    context = {
        "objects_list": objects_list,
    }
    return render(request, 'BaseApp/BaseBenefit/FriendBenefit/list.html', context)


def friend_benefit_details(request, benefit_id):
    object = get_object_or_404(models.UserFriendBenefit, pk=benefit_id)
    context = {
        'object': object,
    }
    return render(request, 'BaseApp/BaseBenefit/FriendBenefit/details.html', context)


# TicketBenefit
def ticket_benefit_create(request):
    form = forms.TicketBenefitForm(request.POST or None)
    items = models.Item.objects.filter(catalog__business__id=request.session['business'].id)
    services = models.Service.objects.filter(catalog__business__id=request.session['business'].id)
    if form.is_valid():
        instance = form.save(commit=False)
        base_benefit = request.session['BaseBenefit']
        base_benefit.business = request.session['business']
        base_benefit.save()
        instance.benefit = base_benefit
        instance.required_punches -= 1
        instance.save()
        if instance.reward_type == 'item_reward':
            selected = request.POST.get('item_checks')
            for item in items:
                if str(item.id) == selected:
                    instance.item_reward = item
        elif instance.reward_type == 'service_reward':
            selected = request.POST.get('service_checks')
            for service in services:
                if str(service.id) == selected:
                    instance.service_reward = service
        else:
            money_reward = request.POST.get('money_reward')
            instance.money_reward = money_reward
        instance.save()
        followers = models.User.objects.filter(appuser__in=base_benefit.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=base_benefit.business,
                        verb='created a new ticket benefit.', target=instance, nf_type='create')
        return redirect('default')
    context = {
        'form': form,
        'items': items,
        'services': services,
    }
    return render(request, 'BaseApp/BaseBenefit/TicketBenefit/create.html', context)


def ticket_benefit_list(request):
    objects_list = models.UserTicketBenefit.objects.filter(
        ticket_benefit__benefit__business=request.session['business'])
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
def discount_benefit_create(request):
    form = forms.DiscountBenefitForm(request.POST or None)
    items = models.Item.objects.filter(catalog__business__id=request.session['business'].id).exclude(
        itemdiscount__new_price__gte=0)
    services = models.Service.objects.filter(catalog__business__id=request.session['business'].id).exclude(
        servicediscount__new_price__gte=0)
    if form.is_valid():
        instance = form.save(commit=False)
        base_benefit = request.session['BaseBenefit']
        base_benefit.business = request.session['business']
        base_benefit.save()
        instance.benefit = base_benefit
        instance.save()
        if instance.discount_type == 'item_discounts':
            print()
            selected = request.POST.getlist('item_checks')
            for item in items:
                if str(item.id) in selected:
                    item_discount = models.ItemDiscount()
                    item_discount.new_price = item.price * (1 - (instance.discount_percentage / 100))
                    item_discount.item = item
                    item_discount.save()
                    instance.item_discounts.add(item_discount)
        elif instance.discount_type == 'service_discounts':
            selected = request.POST.getlist('service_checks')
            for service in services:
                if str(service.id) in selected:
                    service_discount = models.ServiceDiscount()
                    service_discount.new_price = service.price * (1 - (instance.discount_percentage / 100))
                    service_discount.service = service
                    service_discount.save()
                    instance.service_discounts.add(service_discount)
        else:
            purchase_amount = request.POST.get('purchase_amount')
            instance.purchase_amount_discount = float(purchase_amount)
        instance.save()
        followers = models.User.objects.filter(appuser__in=base_benefit.business.followers.all())
        if followers:
            notify.send(request.user, recipient_list=list(followers), actor=base_benefit.business,
                        verb='created a new discount benefit.', target=instance, nf_type='create')
        return redirect('default')
    context = {
        'form': form,
        'items': items,
        'services': services,
    }
    return render(request, 'BaseApp/BaseBenefit/DiscountBenefit/create.html', context)


def discount_benefit_list(request):
    objects_list = models.UserDiscountBenefit.objects.filter(
        discount_benefit__benefit__business=request.session['business'])
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


def statistics_charts(request):
    business = request.session['business']
    popularity_dict = business.get_benefits_popularity()
    income_dict = business.get_business_income()
    items_list = models.Item.objects.filter(catalog__business=business)
    ticket_benefits = models.TicketBenefit.objects.filter(benefit__business=business)
    friend_benefits = models.FriendBenefit.objects.filter(benefit__business=business)
    discount_benefits = models.DiscountBenefit.objects.filter(benefit__business=business)
    print(income_dict)
    context = {
        'items_list': items_list,
        'popularity_dict': popularity_dict,
        'income_dict': income_dict,
        'ticket_benefits': ticket_benefits,
        'friend_benefits': friend_benefits,
        'discount_benefits': discount_benefits,

    }
    return render(request, 'BaseApp/charts/charts.html', context)


def followers_nearby(request):
    followers_dict = request.session['business'].followers_nearby()

    context = {
        'followers_dict': followers_dict,
    }
    return render(request, 'BaseApp/Location/followers_nearby.html', context)
