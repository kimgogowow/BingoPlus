# Generated by Django 4.1.5 on 2023-04-21 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_plus', '0005_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.FileField(blank=True, default='/static/image/profile5.png', upload_to=''),
        ),
    ]
