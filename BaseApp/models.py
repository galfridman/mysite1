from datetime import datetime, time, timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
import os
from conversation.models import Conversation as Conversation
from django.db.models import Q
from django.utils.functional import cached_property
import pytz

GENDERS = [
    ('NONE', "None"),
    ('MALE', "Male"),
    ('FEMALE', "Female"),
]

CATEGORIES = [
    ('NONE', "None"),
    ('FOOD', "Food"),
    ('FASHION', "Fashion"),
    ('ELECTRONICS', "Electronics"),
    ('LEISURE', "Leisure"),
    ('FURNITURES', "Furnitures"),
    ('OTHER', "Other"),

]

AUDIENCE = [
    ('all', "Every one"),
    ('followers', "Followers only"),
]

AVAILABILITY = [
    ('AVAILABLE', "Available"),
    ('NOT AVAILABLE', "Not Available"),
]

DURATION_CHOICES = {
    (timedelta(minutes=60), '1:00'),
    (timedelta(minutes=90), '1:30'),
    (timedelta(minutes=120), '2:00'),
    (timedelta(minutes=150), '2:30'),
    (timedelta(minutes=180), '3:00'),
    (timedelta(minutes=210), '3:30'),
    (timedelta(minutes=240), '4:00'),
    (timedelta(minutes=270), '4:30'),
}

ORDER_TYPE = [
    ('TAKE-AWAY', "Take Away"),
    ('DELIVERY', "Delivery"),
]

DISPUTE_TOPICS = [
    ('Misleading description', "Misleading description"),
    ('Bad service', "Bad service"),
    ('Wrong details supplied', "Wrong details supplied"),
    ('Accidentally made the order', "Accidentally made the order"),
    ('Other', "Other"),
]

WEEKDAYS = [
    (1, "Sunday"),
    (2, "Monday"),
    (3, "Tuesday"),
    (4, "Wednesday"),
    (5, "Thursday"),
    (6, "Friday"),
    (7, "Saturday"),
]

STATUS = [
    ('accepted', "Accepted"),
    ('pending', "Pending"),
    ('rejected', "Rejected"),
]

BENEFIT_TYPE = [
    ('friend', "Friend benefit"),
    ('ticket', "Ticket benefit"),
    ('discount', "Discount benefit"),
]

REWARD_TYPES = [
    ('item_reward', "Item"),
    ('service_reward', "Service"),
    ('money_reward', 'Money')
]

DISCOUNT_TYPES = [
    ('item_discounts', "Items"),
    ('service_discounts', "Services"),
    ('purchase_amount_discount', 'Purchase amount')
]

REQUEST_TYPES = [
    ('friend', 'friend'),
    ('follow', 'follow'),
    ('manage', 'manage'),
    ('follow-benefit', 'follow-benefit'),
]


class Request(models.Model):
    sender_content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='sent_requests',
                                            on_delete=models.CASCADE)
    sender_object_id = models.PositiveIntegerField(null=True, blank=True)
    sender_content_object = GenericForeignKey('sender_content_type', 'sender_object_id')

    reciever_content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='recieved_requests',
                                              on_delete=models.CASCADE)
    reciever_object_id = models.PositiveIntegerField(null=True, blank=True)
    reciever_content_object = GenericForeignKey('reciever_content_type', 'reciever_object_id')

    object_content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='included_requests',
                                            on_delete=models.CASCADE)
    object_object_id = models.PositiveIntegerField(null=True, blank=True)
    object_content_object = GenericForeignKey('object_content_type', 'object_object_id')

    status = models.CharField(choices=STATUS, default="pending", max_length=50)
    type = models.CharField(choices=REQUEST_TYPES, max_length=50, default="")
    created_at = models.DateTimeField(default=datetime.now())

    class Meta:
        ordering = ('created_at', 'type')
        unique_together = (
        'reciever_content_type', 'reciever_object_id', 'sender_content_type', 'sender_object_id', 'type')

    @cached_property
    def sender(self):
        return self.sender_content_object

    @cached_property
    def reciever(self):
        return self.reciever_content_object

    @cached_property
    def object(self):
        return self.object_content_object


def get_image_path(instance, filename):
    return os.path.join('img/', instance.__class__.__name__, str(instance.id), filename)


class Address(models.Model):
    raw = models.TextField(default="")
    street_name = models.TextField()
    street_number = models.TextField()
    city = models.TextField()
    state = models.TextField()
    zip_code = models.TextField()
    country = models.TextField()

    def __unicode__(self):
        return u"%s" % self.raw

    def __str__(self):
        return "%s" % self.raw

    def attrs(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value


class AppUser(models.Model):
    birthdate = models.DateField(null=True, blank=True, default='01/01/2000')
    address = models.ForeignKey(Address, null=True, blank=True)
    image = models.ImageField(upload_to=get_image_path, default=os.path.join('img', 'default.png'))
    gender = models.CharField(choices=GENDERS, default='NONE', max_length=50)
    user = models.OneToOneField(User)
    friends = models.ManyToManyField("self")

    def statistics(self, business):
        items_bought = ItemOrder.objects.filter(item__catalog__business=business, order__user=self)
        items_count, friend_benefits_count, ticket_benefits_count, discount_benefits_count = 0, 0,  0, 0
        for item_order in items_bought:
            items_count += item_order.quantity
        friend_benefits = UserFriendBenefit.objects.filter(friend_benefit__benefit__business=business, user=self)
        for benefit in friend_benefits:
            friend_benefits_count += benefit.times_completed
        ticket_benefits = UserTicketBenefit.objects.filter(ticket_benefit__benefit__business=business, user=self)
        for benefit in ticket_benefits:
            ticket_benefits_count += benefit.times_completed
        discount_benefits = UserDiscountBenefit.objects.filter(discount_benefit__benefit__business=business,user=self)
        for benefit in discount_benefits:
            discount_benefits_count += benefit.times_completed
        orders_made = Order.objects.filter(user=self, business=business)
        orders_total = 0
        for order in orders_made:
            orders_total += order.total
        orders_average = orders_total / orders_made.count()
        my_dict = {
            'orders_count': orders_made.count,
            'orders_total': orders_total,
            'order_average': orders_average,
            'items_count': items_count,
            'friend_benefits_count': friend_benefits_count,
            'ticket_benefits_count': ticket_benefits_count,
            'discount_benefits_count': discount_benefits_count,
        }
        return my_dict

    def age(self):
        return datetime.now().year - self.birthdate.year

    def get_absolute_url(self):
        return "/user/%i/details" % self.id

    def __unicode__(self):
        return u"%s %s" % (self.user.first_name, self.user.last_name)

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class Business(models.Model):
    followers = models.ManyToManyField(AppUser, related_name='favorite_businesses')
    name = models.TextField()
    description = models.TextField()
    category = models.CharField(choices=CATEGORIES, max_length=50)
    email = models.EmailField(null=True, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True)
    image = models.ImageField(upload_to=get_image_path, default=os.path.join('img', 'default.png'))
    managers = models.ManyToManyField(AppUser, related_name='managed_businesses')

    def followers_statistics(self):
        my_list = []
        for user in self.followers.all():
            my_list.append({user: user.statistics(self)})
        return my_list

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return "/business/%i/details" % self.id

    def get_benefits_popularity(self):
        friend_benefit = UserFriendBenefit.objects.filter(friend_benefit__benefit__business=self).count
        ticket_benefit = UserTicketBenefit.objects.filter(ticket_benefit__benefit__business=self).count
        discount_benefit = UserDiscountBenefit.objects.filter(discount_benefit__benefit__business=self).count
        my_dict = {
            'friend_benefit': friend_benefit,
            'ticket_benefit': ticket_benefit,
            'discount_benefit': discount_benefit,
        }
        return my_dict

    def get_business_income(self):
        previous_year_dict = {}
        this_year_dict = {}
        for i in range(1, 13):
            for j in range(0, 2):
                orders = Order.objects.filter(business=self, created_at__month=i,
                                              created_at__year=datetime.now().year - j)
                total = 0
                for order in orders:
                    total += order.total
                if j == 0:
                    this_year_dict.update({i: total})
                else:
                    previous_year_dict.update({i: total})
        my_dict = {
            'this_year': this_year_dict,
            'previous_year': previous_year_dict,
        }
        return my_dict



class Phone(models.Model):
    business = models.ForeignKey(Business, related_name='phones')
    description = models.TextField(max_length='20')
    number = models.CharField(max_length=10, unique=True, validators=[RegexValidator(regex='^\d{10}$',
                                                                                     message='Length has to be 10',
                                                                                     code='Invalid number')])


class AppConversation(models.Model):
    appuser = models.ForeignKey(AppUser)
    business = models.ForeignKey(Business)
    conversation = models.OneToOneField(
        Conversation,
        verbose_name='Conversation',
        related_name='appconversation',
        null=True,
        blank=True
    )
    is_regular = models.BooleanField(default=True)


class Catalog(models.Model):
    name = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    changed_at = models.DateTimeField(default=datetime.now)
    image = models.ImageField(upload_to=get_image_path, default=os.path.join('img', 'default.png'))
    business = models.ForeignKey(Business, related_name='business_catalogs')

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return "/business/%i/catalog/%i/details" % (self.business.id, self.id)


class Item(models.Model):
    name = models.TextField()
    image = models.ImageField(upload_to=get_image_path, default=os.path.join('img', 'default.png'))
    description = models.TextField()
    price = models.FloatField(null=True, blank=True)
    catalog = models.ForeignKey(Catalog, related_name='catalog_items')
    created_at = models.DateTimeField(default=datetime.now)
    changed_at = models.DateTimeField(default=datetime.now)
    is_available = models.CharField(choices=AVAILABILITY, max_length=50)

    def purchased_times(self):
        total = 0
        for item_order in self.order_items.all():
            total += item_order.quantity
        return total

    def statistics(self):
        orders = Order.objects.filter(business=self.catalog.business)
        age1, age2, age3, age4 = 0, 0, 0, 0
        g_male, g_female, g_none = 0, 0, 0
        t_take_away, t_delivery = 0, 0
        total = self.purchased_times()
        if total == 0:
            total = 1
        for order in orders:
            for item_order in order.item_orders.all():
                if self == item_order.item:
                    if order.user.birthdate.year:
                        age = datetime.now().year - order.user.birthdate.year
                    else:
                        age = 18
                    if age <= 18:
                        age1 += item_order.quantity
                    elif 18 < age <= 35:
                        age2 += item_order.quantity
                    elif 35 < age3 <= 50:
                        age3 += item_order.quantity
                    else:
                        age4 += item_order.quantity

                    if order.user.gender == 'MALE':
                        g_male += item_order.quantity
                    elif order.user.gender:
                        g_female += item_order.quantity
                    else:
                        g_none =+ item_order.quantity

        return {
            'age': {
                'age_18': age1 / total,
                'age_18_35': age2 / total,
                'age_35_50': age3 / total,
                'age_50': age4 / total
            },

            'gender': {
                'male': g_male / total,
                'female': g_female / total,
                'none': g_none / total,
            }


        }



    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return "/business/%i/catalog/%i/item/%i/details" % (self.catalog.business.id, self.catalog.id, self.id)


class Service(models.Model):
    name = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to=get_image_path, default=os.path.join('img', 'default.png'))
    price = models.FloatField(null=True, blank=True)
    catalog = models.ForeignKey(Catalog, related_name='catalog_services')
    created_at = models.DateTimeField(default=datetime.now)
    changed_at = models.DateTimeField(default=datetime.now)
    duration = models.DurationField(choices=DURATION_CHOICES, default=timedelta(minutes=60))
    purchased_times = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s" % self.name

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return "/business/%i/catalog/%i/service/%i/details" % (self.catalog.business.id, self.catalog.id, self.id)


class ItemCoupon(models.Model):
    item = models.ForeignKey(Item, related_name='item_coupons', null=True, blank=True)
    user = models.ForeignKey(AppUser, related_name='user_item_coupons', null=True, blank=True)
    business = models.ForeignKey(Business, related_name='business_item_coupons', null=True, blank=True)
    is_used = models.BooleanField(default=False)


class MoneyCoupon(models.Model):
    money_reward = models.IntegerField(default=0)
    business = models.ForeignKey(Business, related_name='business_money_coupons', null=True, blank=True)
    user = models.ForeignKey(AppUser, related_name='user_money_coupons', null=True, blank=True)
    is_used = models.BooleanField(default=False)


class Order(models.Model):
    user = models.ForeignKey(AppUser, related_name='user_orders')
    business = models.ForeignKey(Business, related_name='business_orders')
    type = models.CharField(choices=ORDER_TYPE, max_length=50)
    picking_time = models.TimeField(null=True, blank=True)
    address = models.ForeignKey(Address, null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    phone = models.TextField()
    status = models.CharField(choices=STATUS, max_length=20, default="pending")
    created_at = models.DateTimeField(default=datetime.now)
    appconversation = models.ForeignKey(AppConversation, null=True, blank=True)
    item_coupons = models.ManyToManyField(ItemCoupon)
    money_coupons = models.ManyToManyField(MoneyCoupon)

    def __unicode__(self):
        return u"Order %s" % self.id

    def __str__(self):
        return "Order %s" % self.id

    def get_absolute_url(self):
        return "/business/order/%i/details" % self.id




class ItemOrder(models.Model):
    order = models.ForeignKey(Order, related_name='item_orders')
    item = models.ForeignKey(Item, related_name='order_items')
    quantity = models.IntegerField(null=True, blank=True)


# business time
class OpeningHours(models.Model):
    business = models.ForeignKey(Business, related_name='opening_hours')
    weekday = models.IntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField(default=time(5, 00))
    to_hour = models.TimeField(default=time(23, 59))

    class Meta:
        ordering = ('weekday', 'from_hour')
        unique_together = ('weekday', 'from_hour', 'to_hour')

    def __unicode__(self):
        return u'%s: %s - %s' % (self.get_weekday_display(),
                                 self.from_hour, self.to_hour)

    def __str__(self):
        return '%s: %s - %s' % (self.get_weekday_display(), self.from_hour, self.to_hour)


# end business time


class Appointment(models.Model):
    service = models.ForeignKey(Service, related_name='service_appointments')
    total = models.FloatField(default=0)
    date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(AppUser, related_name='user_appointments')
    business = models.ForeignKey(Business, related_name='business_appointments', null=True, blank=True)
    appconversation = models.ForeignKey(AppConversation, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20, default='pending')

    def get_absolute_url(self):
        return "/business/appointment/%i/details" % self.id


class Dispute(models.Model):
    user = models.ForeignKey(AppUser, related_name='user_disputes', null=True, blank=True)
    business = models.ForeignKey(Business, related_name='business_disputes', null=True, blank=True)
    appointment = models.ForeignKey(Appointment, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)
    topic = models.CharField(choices=DISPUTE_TOPICS, max_length=50)
    description = models.TextField()
    appconversation = models.ForeignKey(AppConversation, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20, default='pending')
    created_at = models.DateTimeField(default=datetime.now)

    def get_absolute_url(self):
        return "/business/dispute/%i/details" % self.id


class BasePost(models.Model):
    followers = models.ManyToManyField(AppUser, related_name='favorite_posts')
    text = models.TextField()
    business = models.ForeignKey(Business, related_name='business_base_posts')
    is_important = models.BooleanField(default=False)
    audience = models.CharField(choices=AUDIENCE, max_length=50)
    created_at = models.DateTimeField(default=datetime.now)
    changed_at = models.DateTimeField(default=datetime.now)


class BaseBenefit(models.Model):
    title = models.TextField()
    text = models.TextField()
    type = models.CharField(choices=BENEFIT_TYPE, max_length=50, default="")
    business = models.ForeignKey(Business, related_name='business_base_benefits')
    starting_date = models.DateTimeField(null=True, blank=True)
    ending_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'%s: %s - %s' % (self.business,
                                 self.title, self.type)

    def __str__(self):
        return '%s: %s - %s' % (self.business,
                                self.title, self.type)

    def is_available(self):
        utc = pytz.UTC
        return self.starting_date <= utc.localize(datetime.now()) <= self.ending_date


class TicketBenefit(models.Model):
    benefit = models.ForeignKey(BaseBenefit, related_name='ticket_base_benefits')
    required_punches = models.IntegerField(default=0)
    reward_type = models.CharField(choices=REWARD_TYPES, max_length=50, default="")
    item_reward = models.OneToOneField(Item, null=True, blank=True)
    service_reward = models.OneToOneField(Service, null=True, blank=True)
    money_reward = models.FloatField(default=0)

    def times_completed(self):
        registered_benefits = self.ticket_benefits_made.all()
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        return times_completed

    def get_score(self):
        registered_benefits = self.ticket_benefits_made.all()
        registered_count = registered_benefits.count()
        if registered_count == 0:
            return 0
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        if times_completed == 0:
            return 0
        delta = self.benefit.ending_date - self.benefit.starting_date
        if delta.days == 0:
            delta = 1
        worthiness = float(self.required_punches) * 10
        score = ((times_completed + registered_count) / registered_count) * (1 / delta.days) * worthiness
        return score


    def get_absolute_url(self):
        return "/user/basebenefit/ticketbenefit/%i/details" % self.id


class FriendBenefit(models.Model):
    benefit = models.ForeignKey(BaseBenefit, related_name='friend_base_benefits')
    required_friends = models.IntegerField(default=1)  # required friends
    reward_type = models.CharField(choices=REWARD_TYPES, max_length=50, default="")
    item_reward = models.OneToOneField(Item, null=True, blank=True)
    service_reward = models.OneToOneField(Service, null=True, blank=True)
    money_reward = models.FloatField(default=0)

    def times_completed(self):
        registered_benefits = self.friend_benefits_made.all()
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        return times_completed

    def get_score(self):
        registered_benefits = self.friend_benefits_made.all()
        registered_count = registered_benefits.count()
        if registered_count == 0:
            return 0
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        if times_completed == 0:
            return 0
        delta = self.benefit.ending_date - self.benefit.starting_date
        if delta.days == 0:
            delta = 1
        worthiness = float(self.required_friends) * 10
        score = ((times_completed + registered_count) / registered_count) * (1 / delta.days) * worthiness
        return score

    def get_absolute_url(self):
        return "/user/basebenefit/friendbenefit/%i/details" % self.id


class ItemDiscount(models.Model):
    item = models.OneToOneField(Item, null=True, blank=True)
    new_price = models.FloatField(default=0)


class ServiceDiscount(models.Model):
    service = models.OneToOneField(Service)
    new_price = models.FloatField(default=0)


class DiscountBenefit(models.Model):
    benefit = models.ForeignKey(BaseBenefit, related_name='discount_base_benefits')
    discount_type = models.CharField(choices=DISCOUNT_TYPES, max_length=50, default="")
    item_discounts = models.ManyToManyField(ItemDiscount, related_name='discount')
    service_discounts = models.ManyToManyField(ServiceDiscount, related_name='discount')
    purchase_amount_discount = models.FloatField(default=0)
    discount_percentage = models.IntegerField(default=0)

    def times_completed(self):
        registered_benefits = self.discount_benefits_made.all()
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        return times_completed

    def get_score(self):
        registered_benefits = self.discount_benefits_made.all()
        registered_count = registered_benefits.count()
        if registered_count == 0:
            return 0
        times_completed = 0
        for benefit in registered_benefits:
            times_completed += benefit.times_completed
        if times_completed == 0:
            return 0
        delta = self.benefit.ending_date - self.benefit.starting_date
        if delta.days == 0:
            delta = 1
        worthiness = 100 - float(self.discount_percentage)
        score = ((times_completed + registered_count) / registered_count) * (1 / delta.days) * worthiness
        return score

    def get_discount(self):
        return self.purchase_amount_discoun * self.discount_percentage / 100

    def get_absolute_url(self):
        return "/user/basebenefit/discountbenefit/%i/details" % self.id


class UserFriendBenefit(models.Model):
    user = models.ForeignKey(AppUser, related_name='user_friend_benefits')
    friends_added = models.ManyToManyField(AppUser)
    friend_benefit = models.ForeignKey(FriendBenefit, related_name='friend_benefits_made', null=True, blank=True)
    times_completed = models.IntegerField(default=0)
    counter = models.IntegerField(default=0)

    class Meta:
        unique_together = ('friend_benefit', 'user')

    def get_percents(self):
        return (self.counter / self.friend_benefit.required_friends) * 100


class UserTicketBenefit(models.Model):
    user = models.ForeignKey(AppUser, related_name='user_ticket_benefits')
    purchases_made = models.IntegerField(default=0, null=True, blank=True)
    ticket_benefit = models.ForeignKey(TicketBenefit, related_name='ticket_benefits_made', null=True, blank=True)
    times_completed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('ticket_benefit', 'user')

    def get_percents(self):
        return (self.purchases_made / self.ticket_benefit.required_punches) * 100


class UserDiscountBenefit(models.Model):
    user = models.ForeignKey(AppUser, related_name='user_discount_benefits', null=True, blank=True)
    discount_benefit = models.ForeignKey(DiscountBenefit, related_name='discount_benefits_made', null=True, blank=True)
    times_completed = models.IntegerField(default=0)


    class Meta:
        unique_together = ('discount_benefit', 'user')
