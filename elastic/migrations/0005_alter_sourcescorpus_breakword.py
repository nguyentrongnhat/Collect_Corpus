# Generated by Django 3.2.9 on 2021-12-18 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elastic', '0004_sourcescorpus_breakword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourcescorpus',
            name='breakWord',
            field=models.TextField(blank=True),
        ),
    ]
