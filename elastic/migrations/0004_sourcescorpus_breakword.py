# Generated by Django 3.2.9 on 2021-12-18 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elastic', '0003_alter_sourcescorpus_pagequery'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcescorpus',
            name='breakWord',
            field=models.TextField(default=''),
        ),
    ]
