# Generated by Django 2.1.3 on 2018-11-23 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('s3', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sentiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=128)),
                ('date', models.DateField()),
                ('positive', models.IntegerField()),
                ('neutral', models.IntegerField()),
                ('negative', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4)),
                ('date', models.CharField(max_length=10)),
                ('opening', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('ending', models.FloatField()),
                ('volume', models.IntegerField()),
                ('adjust', models.FloatField()),
            ],
        ),
    ]