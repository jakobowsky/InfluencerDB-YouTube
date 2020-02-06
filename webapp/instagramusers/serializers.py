from rest_framework import serializers
from instagramusers.models import (
    Category,
    InstagramAccount,
    InstagramPost,
    InstagramAccountReport,
    Hashtag,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'name'
        )


class InstagramAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = (
            'id',
            'username',
            'bio',
            'category',
            'daily_growth',
            'average_comments_per_post',
            'average_likes_per_post',
            'followers',
            'following',
        )


class InstagramPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramPost
        fields = (
            'id',
            'instagram_account',
            'url_to_post',
            'added_to_ig',
            'last_report',
            'current_likes',
            'current_comments'
        )


class InstagramAccountReportSerializers(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccountReport
        fields = (
            'id',
            'instagram_account',
            'date_reported',
            'followers',
            'following'
        )


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = (
            'id',
            'name',
            'category',
        )
