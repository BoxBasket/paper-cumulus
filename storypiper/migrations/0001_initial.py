# Generated by Django 3.0.6 on 2020-05-27 03:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='Untitled Series', max_length=50)),
                ('slug', models.SlugField(blank=True, default='')),
                ('is_demo', models.BooleanField(blank=True, default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flipbook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id64', models.CharField(blank=True, default='', max_length=8)),
                ('title', models.CharField(blank=True, default='', max_length=50)),
                ('description', models.TextField(blank=True, default='', max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('series', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='storypiper.Series')),
            ],
        ),
    ]
