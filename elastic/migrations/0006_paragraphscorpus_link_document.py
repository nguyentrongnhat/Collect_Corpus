# Generated by Django 3.2.9 on 2021-12-18 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elastic', '0005_alter_sourcescorpus_breakword'),
    ]

    operations = [
        migrations.AddField(
            model_name='paragraphscorpus',
            name='link_document',
            field=models.URLField(blank=True),
        ),
    ]