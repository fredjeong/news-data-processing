# Generated by Django 5.2 on 2025-04-25 04:42

import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsArticle',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('writer', models.CharField(max_length=255)),
                ('write_date', models.DateTimeField()),
                ('category', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('url', models.CharField(max_length=200)),
                ('keywords', models.CharField(max_length=200)),
                ('embedding', pgvector.django.vector.VectorField(dimensions=1024)),
                ('summary', models.TextField()),
            ],
            options={
                'db_table': 'news_articles',
                'managed': False,
            },
        ),
    ]
