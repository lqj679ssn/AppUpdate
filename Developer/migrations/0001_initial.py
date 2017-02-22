# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-22 10:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Developer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default=None, max_length=16, verbose_name='用户名')),
                ('password', models.CharField(default=None, max_length=40, verbose_name='加密密码')),
                ('salt', models.CharField(default=None, max_length=8, verbose_name='盐密')),
                ('isFrozen', models.BooleanField(default=False, verbose_name='是否被冻结')),
                ('lastLogin', models.DateTimeField(default=None, null=True, verbose_name='上次登录时间')),
                ('lastIpv4', models.GenericIPAddressField(default=None, null=True, verbose_name='上次登录IP')),
                ('thisLogin', models.DateTimeField(default=None, null=True, verbose_name='本次登录时间')),
                ('thisIpv4', models.GenericIPAddressField(default=None, null=True, verbose_name='本次登录IP')),
            ],
        ),
    ]
