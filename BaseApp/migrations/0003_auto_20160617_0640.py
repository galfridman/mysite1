# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-17 03:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BaseApp', '0002_auto_20160602_1926'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('raw', models.CharField(default='', max_length=100)),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2016, 6, 17, 6, 40, 20, 165615))),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='BaseApp.AppUser')),
            ],
        ),
        migrations.AlterField(
            model_name='request',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 17, 6, 40, 20, 140098)),
        ),
        migrations.AlterField(
            model_name='service',
            name='duration',
            field=models.DurationField(choices=[(datetime.timedelta(0, 12600), '3:30'), (datetime.timedelta(0, 16200), '4:30'), (datetime.timedelta(0, 14400), '4:00'), (datetime.timedelta(0, 5400), '1:30'), (datetime.timedelta(0, 7200), '2:00'), (datetime.timedelta(0, 3600), '1:00'), (datetime.timedelta(0, 9000), '2:30'), (datetime.timedelta(0, 10800), '3:00')], default=datetime.timedelta(0, 3600)),
        ),
    ]