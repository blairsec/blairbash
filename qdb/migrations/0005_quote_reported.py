# Generated by Django 2.1 on 2018-08-06 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qdb', '0004_quote_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='reported',
            field=models.BooleanField(default=False),
        ),
    ]
