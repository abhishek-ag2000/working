# Generated by Django 2.0.6 on 2019-06-11 10:39

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('Date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Article_Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('Date', models.DateTimeField(auto_now_add=True)),
                ('Question_title', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Articles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Article_title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('Description', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='HelpCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(default='Getting Started', max_length=40)),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to='help_image')),
                ('desc', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='articles',
            name='Article_Category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='helpandsupport.HelpCategories'),
        ),
        migrations.AddField(
            model_name='article_questions',
            name='Article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Article', to='helpandsupport.Articles'),
        ),
        migrations.AddField(
            model_name='article_questions',
            name='User',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='article_answers',
            name='Answers',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='helpandsupport.Article_Questions'),
        ),
        migrations.AddField(
            model_name='article_answers',
            name='Question_of_article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Article_Question', to='helpandsupport.Articles'),
        ),
        migrations.AddField(
            model_name='article_answers',
            name='User',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
