# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-21 19:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Apps', '0003_apps_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='version',
            old_name='descriptionEncoded',
            new_name='description',
        ),
    ]
