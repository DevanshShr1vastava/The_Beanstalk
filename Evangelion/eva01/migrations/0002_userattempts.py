# Generated by Django 5.1 on 2024-08-26 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='userAttempts',
            fields=[
                ('uAID', models.IntegerField(primary_key=True, serialize=False)),
                ('qID', models.IntegerField()),
                ('answer', models.IntegerField()),
                ('marked_for_review', models.IntegerField()),
                ('time_taken', models.IntegerField()),
            ],
        ),
    ]