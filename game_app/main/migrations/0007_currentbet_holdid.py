# Generated by Django 3.2.9 on 2021-12-02 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_currentbet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentbet',
            name='holdId',
            field=models.CharField(default=0, max_length=64),
        ),
    ]
