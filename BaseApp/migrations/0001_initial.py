# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-02 16:01
from __future__ import unicode_literals

import BaseApp.models
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('conversation', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw', models.TextField(default='')),
                ('street_name', models.TextField()),
                ('street_number', models.TextField()),
                ('city', models.TextField()),
                ('state', models.TextField()),
                ('zip_code', models.TextField()),
                ('country', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AppConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_regular', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.FloatField(default=0)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('appconversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.AppConversation')),
            ],
        ),
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birthdate', models.DateField(blank=True, default='01/01/2000', null=True)),
                ('image', models.ImageField(default='img\\default.png', upload_to=BaseApp.models.get_image_path)),
                ('gender', models.CharField(choices=[('NONE', 'None'), ('MALE', 'Male'), ('FEMALE', 'Female')], default='NONE', max_length=50)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Address')),
                ('friends', models.ManyToManyField(related_name='_appuser_friends_+', to='BaseApp.AppUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BaseBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('text', models.TextField()),
                ('type', models.CharField(choices=[('friend', 'Friend benefit'), ('ticket', 'Ticket benefit'), ('discount', 'Discount benefit')], default='', max_length=50)),
                ('starting_date', models.DateTimeField(blank=True, null=True)),
                ('ending_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BasePost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_important', models.BooleanField(default=False)),
                ('audience', models.CharField(choices=[('all', 'Every one'), ('followers', 'Followers only')], max_length=50)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('changed_at', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('NONE', 'None'), ('FOOD', 'Food'), ('FASHION', 'Fashion'), ('ELECTRONICS', 'Electronics'), ('LEISURE', 'Leisure'), ('FURNITURES', 'Furnitures'), ('OTHER', 'Other')], max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('image', models.ImageField(default='img\\default.png', upload_to=BaseApp.models.get_image_path)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Address')),
                ('followers', models.ManyToManyField(related_name='favorite_businesses', to='BaseApp.AppUser')),
                ('managers', models.ManyToManyField(related_name='managed_businesses', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('changed_at', models.DateTimeField(default=datetime.datetime.now)),
                ('image', models.ImageField(default='img\\default.png', upload_to=BaseApp.models.get_image_path)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_catalogs', to='BaseApp.Business')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(choices=[('item_discounts', 'Items'), ('service_discounts', 'Services'), ('purchase_amount_discount', 'Purchase amount')], default='', max_length=50)),
                ('purchase_amount_discount', models.FloatField(default=0)),
                ('discount_percentage', models.IntegerField(default=0)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_base_benefits', to='BaseApp.BaseBenefit')),
            ],
        ),
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(choices=[('Misleading description', 'Misleading description'), ('Bad service', 'Bad service'), ('Wrong details supplied', 'Wrong details supplied'), ('Accidentally made the order', 'Accidentally made the order'), ('Other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('appconversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.AppConversation')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Appointment')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_disputes', to='BaseApp.Business')),
            ],
        ),
        migrations.CreateModel(
            name='FriendBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required_friends', models.IntegerField(default=1)),
                ('reward_type', models.CharField(choices=[('item_reward', 'Item'), ('service_reward', 'Service'), ('money_reward', 'Money')], default='', max_length=50)),
                ('money_reward', models.FloatField(default=0)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_base_benefits', to='BaseApp.BaseBenefit')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('image', models.ImageField(default='img\\default.png', upload_to=BaseApp.models.get_image_path)),
                ('description', models.TextField()),
                ('price', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('changed_at', models.DateTimeField(default=datetime.datetime.now)),
                ('is_available', models.CharField(choices=[('AVAILABLE', 'Available'), ('NOT AVAILABLE', 'Not Available')], max_length=50)),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_items', to='BaseApp.Catalog')),
            ],
        ),
        migrations.CreateModel(
            name='ItemCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_used', models.BooleanField(default=False)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_item_coupons', to='BaseApp.Business')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item_coupons', to='BaseApp.Item')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_item_coupons', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='ItemDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_price', models.FloatField(default=0)),
                ('item', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ItemOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='BaseApp.Item')),
            ],
        ),
        migrations.CreateModel(
            name='MoneyCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money_reward', models.IntegerField(default=0)),
                ('is_used', models.BooleanField(default=False)),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_money_coupons', to='BaseApp.Business')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_money_coupons', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(1, 'Sunday'), (2, 'Monday'), (3, 'Tuesday'), (4, 'Wednesday'), (5, 'Thursday'), (6, 'Friday'), (7, 'Saturday')])),
                ('from_hour', models.TimeField(default=datetime.time(5, 0))),
                ('to_hour', models.TimeField(default=datetime.time(23, 59))),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='BaseApp.Business')),
            ],
            options={
                'ordering': ('weekday', 'from_hour'),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('TAKE-AWAY', 'Take Away'), ('DELIVERY', 'Delivery')], max_length=50)),
                ('picking_time', models.TimeField(blank=True, null=True)),
                ('total', models.FloatField(blank=True, null=True)),
                ('phone', models.TextField()),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Address')),
                ('appconversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.AppConversation')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_orders', to='BaseApp.Business')),
                ('item_coupons', models.ManyToManyField(to='BaseApp.ItemCoupon')),
                ('money_coupons', models.ManyToManyField(to='BaseApp.MoneyCoupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_orders', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length='20')),
                ('number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(code='Invalid number', message='Length has to be 10', regex='^\\d{10}$')])),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='BaseApp.Business')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('reciever_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('object_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='pending', max_length=50)),
                ('type', models.CharField(choices=[('friend', 'friend'), ('follow', 'follow'), ('manage', 'manage'), ('follow-benefit', 'follow-benefit')], default='', max_length=50)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2016, 6, 2, 19, 1, 2, 206324))),
                ('object_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='included_requests', to='contenttypes.ContentType')),
                ('reciever_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recieved_requests', to='contenttypes.ContentType')),
                ('sender_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_requests', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('created_at', 'type'),
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('image', models.ImageField(default='img\\default.png', upload_to=BaseApp.models.get_image_path)),
                ('price', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('changed_at', models.DateTimeField(default=datetime.datetime.now)),
                ('duration', models.DurationField(choices=[(datetime.timedelta(0, 10800), '3:00'), (datetime.timedelta(0, 3600), '1:00'), (datetime.timedelta(0, 16200), '4:30'), (datetime.timedelta(0, 7200), '2:00'), (datetime.timedelta(0, 5400), '1:30'), (datetime.timedelta(0, 12600), '3:30'), (datetime.timedelta(0, 9000), '2:30'), (datetime.timedelta(0, 14400), '4:00')], default=datetime.timedelta(0, 3600))),
                ('purchased_times', models.IntegerField(default=0)),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_services', to='BaseApp.Catalog')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_price', models.FloatField(default=0)),
                ('service', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Service')),
            ],
        ),
        migrations.CreateModel(
            name='TicketBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('required_punches', models.IntegerField(default=0)),
                ('reward_type', models.CharField(choices=[('item_reward', 'Item'), ('service_reward', 'Service'), ('money_reward', 'Money')], default='', max_length=50)),
                ('money_reward', models.FloatField(default=0)),
                ('benefit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_base_benefits', to='BaseApp.BaseBenefit')),
                ('item_reward', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Item')),
                ('service_reward', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Service')),
            ],
        ),
        migrations.CreateModel(
            name='UserDiscountBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_completed', models.IntegerField(default=0)),
                ('discount_benefit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discount_benefits_made', to='BaseApp.DiscountBenefit')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_discount_benefits', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserFriendBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_completed', models.IntegerField(default=0)),
                ('counter', models.IntegerField(default=0)),
                ('friend_benefit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend_benefits_made', to='BaseApp.FriendBenefit')),
                ('friends_added', models.ManyToManyField(to='BaseApp.AppUser')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_friend_benefits', to='BaseApp.AppUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserTicketBenefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchases_made', models.IntegerField(blank=True, default=0, null=True)),
                ('times_completed', models.IntegerField(default=0)),
                ('ticket_benefit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ticket_benefits_made', to='BaseApp.TicketBenefit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_ticket_benefits', to='BaseApp.AppUser')),
            ],
        ),
        migrations.AddField(
            model_name='itemorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_orders', to='BaseApp.Order'),
        ),
        migrations.AddField(
            model_name='friendbenefit',
            name='item_reward',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Item'),
        ),
        migrations.AddField(
            model_name='friendbenefit',
            name='service_reward',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Service'),
        ),
        migrations.AddField(
            model_name='dispute',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Order'),
        ),
        migrations.AddField(
            model_name='dispute',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_disputes', to='BaseApp.AppUser'),
        ),
        migrations.AddField(
            model_name='discountbenefit',
            name='item_discounts',
            field=models.ManyToManyField(related_name='discount', to='BaseApp.ItemDiscount'),
        ),
        migrations.AddField(
            model_name='discountbenefit',
            name='service_discounts',
            field=models.ManyToManyField(related_name='discount', to='BaseApp.ServiceDiscount'),
        ),
        migrations.AddField(
            model_name='basepost',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_base_posts', to='BaseApp.Business'),
        ),
        migrations.AddField(
            model_name='basepost',
            name='followers',
            field=models.ManyToManyField(related_name='favorite_posts', to='BaseApp.AppUser'),
        ),
        migrations.AddField(
            model_name='basebenefit',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_base_benefits', to='BaseApp.Business'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_appointments', to='BaseApp.Business'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_appointments', to='BaseApp.Service'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_appointments', to='BaseApp.AppUser'),
        ),
        migrations.AddField(
            model_name='appconversation',
            name='appuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BaseApp.AppUser'),
        ),
        migrations.AddField(
            model_name='appconversation',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BaseApp.Business'),
        ),
        migrations.AddField(
            model_name='appconversation',
            name='conversation',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appconversation', to='conversation.Conversation', verbose_name='Conversation'),
        ),
        migrations.AlterUniqueTogether(
            name='userticketbenefit',
            unique_together=set([('ticket_benefit', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='userfriendbenefit',
            unique_together=set([('friend_benefit', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='userdiscountbenefit',
            unique_together=set([('discount_benefit', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='request',
            unique_together=set([('reciever_content_type', 'reciever_object_id', 'reciever_content_type', 'reciever_object_id', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='openinghours',
            unique_together=set([('weekday', 'from_hour', 'to_hour')]),
        ),
    ]