# Generated by Django 2.1 on 2018-08-17 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qdb', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='vote',
            index=models.Index(fields=['value', 'quote'], name='qdb_vote_value_c76b61_idx'),
        ),
    ]
