# Generated by Django 5.1.2 on 2024-10-22 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_match_match_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apiuser',
            name='participated_tournaments',
        ),
        migrations.RemoveField(
            model_name='apiuser',
            name='tournaments',
        ),
        migrations.RemoveField(
            model_name='apiuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='Tournament',
        ),
        migrations.DeleteModel(
            name='ApiUser',
        ),
    ]