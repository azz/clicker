# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20150518_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bubblesort',
            name='size',
        ),
    ]
