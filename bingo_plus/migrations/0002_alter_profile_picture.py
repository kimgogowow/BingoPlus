# Generated by Django 4.1.7 on 2023-04-20 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo_plus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.FileField(blank=True, default='/static/image/profile1.png', upload_to=''),
        ),
    ]