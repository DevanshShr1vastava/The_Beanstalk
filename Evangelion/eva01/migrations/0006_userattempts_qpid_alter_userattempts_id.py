# Generated by Django 5.1 on 2024-08-26 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva01', '0005_questionpapers'),
    ]

    operations = [
        migrations.AddField(
            model_name='userattempts',
            name='qpID',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userattempts',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]