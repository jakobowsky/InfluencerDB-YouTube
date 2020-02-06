from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class InstagramAccount(models.Model):
    username = models.CharField(max_length=80)
    bio = models.TextField(max_length=350)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='accounts')
    daily_growth = models.IntegerField(default=0)
    average_comments_per_post = models.IntegerField(default=0)
    average_likes_per_post = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    last_reported = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.username


class InstagramPost(models.Model):
    instagram_account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, related_name='posts')
    url_to_post = models.URLField(max_length=2000, unique=True)
    added_to_ig = models.DateTimeField()
    last_report = models.DateTimeField(auto_now_add=True)
    current_likes = models.IntegerField(default=0)
    current_comments = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.instagram_account.username} - {self.id}'


class InstagramAccountReport(models.Model):
    instagram_account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, related_name='reports')
    date_reported = models.DateTimeField(auto_now_add=True)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.instagram_account.username} - {self.date_reported}'


class Hashtag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='hashtags')
