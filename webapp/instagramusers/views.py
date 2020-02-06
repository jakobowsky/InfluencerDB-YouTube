from .serializers import (
    CategorySerializer,
    InstagramAccountSerializer,
    InstagramPostSerializer,
    InstagramAccountReportSerializers,
    HashtagSerializer
)
from instagramusers.models import (
    Category,
    InstagramAccount,
    InstagramPost,
    InstagramAccountReport,
    Hashtag,
)
from instagramusers.models import Hashtag, Category
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, views, exceptions
from rest_framework.response import Response
from datetime import datetime, timedelta
import pytz
import json


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    filter_fields = (
        'name',
    )

    search_fields = (
        'name',
    )


class InstagramAccountView(viewsets.ModelViewSet):
    serializer_class = InstagramAccountSerializer
    queryset = InstagramAccount.objects.all()
    filter_fields = (
        'username',
        'category__name',
    )


class InstagramPostView(viewsets.ModelViewSet):
    serializer_class = InstagramPostSerializer
    queryset = InstagramPost.objects.all()


class InstagramAccountReportView(viewsets.ModelViewSet):
    serializer_class = InstagramAccountReportSerializers
    queryset = InstagramAccountReport.objects.all()


class HashtagView(viewsets.ModelViewSet):
    serializer_class = HashtagSerializer
    queryset = Hashtag.objects.all().order_by('?')

    filter_fields = (
        'name',
        'category__name',
        'category__id',
    )


class UpdateAccountsView(views.APIView):
    """
    [GET] and [POST]
    """

    def validate(self, data):
        if data.get('account') is None:
            raise exceptions.ValidationError(
                "account is null"
            )
        if data.get('profile_page_metrics') is None:
            raise exceptions.ValidationError(
                "profile_page_metrics is null"
            )
        if data.get('profile_page_recent_posts') is None:
            raise exceptions.ValidationError(
                "profile_page_recent_posts is null"
            )

    def get_accounts(self):
        # let's use utc for this.
        utc = pytz.utc

        limit = 50
        # accounts = InstagramAccount.objects.filter(last_reported__lt=(datetime.now(utc) - timedelta(hours=12)))
        accounts = InstagramAccount.objects.filter(
            last_reported__lt=(datetime.now(utc) - timedelta(hours=3))).order_by('?')[:limit]  # testing
        return [account.username for account in accounts]

    def get(self, request):
        # returns all account names which need to be updated
        accounts = self.get_accounts()
        return Response({"accounts": accounts})

    def update_account_and_report(self, account_name, profile_page_metrics):
        account_obj = InstagramAccount.objects.get(username=account_name.lower())
        report_obj = self.create_report(profile_page_metrics, account_obj)
        account_obj.bio = profile_page_metrics.get('biography'),
        account_obj.followers = report_obj.followers
        account_obj.following = report_obj.following
        account_obj.last_reported = report_obj.date_reported
        account_obj.save()
        return account_obj

    def update_single_post(self, account_obj, instagram_post_data):

        utc = pytz.utc
        date_added = datetime.fromtimestamp(instagram_post_data.get('taken_at_timestamp'))
        new_post, created = InstagramPost.objects.update_or_create(
            instagram_account=account_obj,
            url_to_post=f"https://www.instagram.com/p/{instagram_post_data.get('shortcode')}/",
            defaults={
                'current_likes': instagram_post_data['edge_liked_by']['count'],
                'current_comments': instagram_post_data['edge_media_to_comment']['count'],
                'last_report': datetime.now(utc),
                'added_to_ig': date_added,
            }
        )
        if created:
            print(f"{account_obj} Post created.")
        else:
            print(f"{account_obj} Post updated.")

    def update_posts(self, profile_page_recent_posts, acount_obj):
        for post in profile_page_recent_posts:
            self.update_single_post(acount_obj, post)

    def create_report(self, profile_page_metrics, account_obj):
        report = InstagramAccountReport()
        report.instagram_account = account_obj
        report.followers = profile_page_metrics.get('edge_followed_by')
        report.following = profile_page_metrics.get('edge_follow')
        report.save()
        return report

    def update_indicators(self, account_obj):
        account_obj.daily_growth = self.calculate_daily_growth(account_obj)

    def calculate_daily_growth(self, account_obj):
        # last 10 days max
        reports = account_obj.reports.all().order_by('-date_reported')[:10]
        denom = float(len(reports))
        daily_growth = 0
        if denom > 2:
            diff = reports[0].followers - reports[int(denom) - 1].followers
            diff = float(diff)
            bottom = (reports[0].date_reported - reports[int(denom) - 1].date_reported).total_seconds()
            daily_growth = timedelta(days=1).total_seconds() * diff / bottom
        account_obj.daily_growth = daily_growth
        account_obj.save()
        return account_obj

    def calculate_acc_indicators(self, account_obj):
        posts = account_obj.posts.all().order_by('-added_to_ig')[:10]
        denom = float(len(posts))
        comments = 0
        likes = 0
        for post in posts:
            comments += post.current_comments
            likes += post.current_likes
        av_comments = float(comments) / float(denom)
        av_likes = float(likes) / float(denom)
        engagement_rate = (float(likes + comments)) / (float(account_obj.followers * denom))
        account_obj.engagement_rate = engagement_rate
        account_obj.average_comments_per_post = av_comments
        account_obj.average_likes_per_post = av_likes
        account_obj.save()
        return account_obj

    def update_all_indicators(self, account_obj):
        account_obj = self.calculate_daily_growth(account_obj)
        account_obj = self.calculate_acc_indicators(account_obj)

    def post(self, request):
        data = request.data
        self.validate(data)
        account_name = data.get('account')
        profile_page_metrics = data.get('profile_page_metrics')
        profile_page_recent_posts = data.get('profile_page_recent_posts')
        account_obj = self.update_account_and_report(account_name, profile_page_metrics)
        self.update_posts(profile_page_recent_posts, account_obj)
        self.update_all_indicators(account_obj)
        return Response({"Info: ": "Done"})


class AddNewAccountView(views.APIView):
    """
        POST request
        {

        }
    """

    def validate(self, data):
        if data.get('account') is None:
            raise exceptions.ValidationError(
                "account is null"
            )

        if data.get('category') is None:
            raise exceptions.ValidationError(
                "category is null"
            )
        if data.get('profile_page_metrics') is None:
            raise exceptions.ValidationError(
                "profile_page_metrics is null"
            )
        if data.get('profile_page_recent_posts') is None:
            raise exceptions.ValidationError(
                "profile_page_recent_posts is null"
            )

    def add_account(self, account_name, category, profile_page_metrics):
        category_obj = Category.objects.get(id=category.get('id'))
        account_obj, created = InstagramAccount.objects.update_or_create(
            username=account_name.lower(),
            defaults={
                'bio': profile_page_metrics.get('biography'),
                'category': category_obj,
                'followers': profile_page_metrics.get('edge_followed_by'),
                'following': profile_page_metrics.get('edge_follow'),
            }
        )
        return account_obj

    def create_posts(self, account_object, profile_page_recent_posts):
        for post in profile_page_recent_posts:
            date_added = datetime.fromtimestamp(post.get('taken_at_timestamp'))
            if not date_added:
                utc = pytz.utc
                date_added = datetime.now(utc)
            new_post, _ = InstagramPost.objects.update_or_create(
                instagram_account=account_object,
                url_to_post=f"https://www.instagram.com/p/{post.get('shortcode')}/",
                defaults={
                    'added_to_ig': date_added,
                    'current_likes': post['edge_liked_by']['count'],
                    'current_comments': post['edge_media_to_comment']['count'],
                    # last_report added auto.
                }
            )

    def create_report(self, account_object):
        InstagramAccountReport.objects.get_or_create(
            instagram_account=account_object,
            followers=account_object.followers,
            following=account_object.following,
            # date_reported now
        )

    def create_first_report_and_posts(self, account_object, profile_page_recent_posts):
        # 1 create InstagramAccountReport.
        # 2 create Post objects.
        self.create_report(account_object)
        self.create_posts(account_object, profile_page_recent_posts)
        return True

    def add_data_to_db(self, data):
        account_username = data.get('account')
        category = data.get('category')
        profile_page_metrics = data.get('profile_page_metrics')
        profile_page_recent_posts = data.get('profile_page_recent_posts')
        account_obj = self.add_account(account_username, category, profile_page_metrics)
        self.create_first_report_and_posts(account_obj, profile_page_recent_posts)

    def post(self, request):
        data = request.data
        self.validate(data)
        self.add_data_to_db(data)
        return Response({"Info: ": "Done"})


class HashtagMultiAddView(views.APIView):
    """
        POST request
        {
            "category_id": 1,
            "hashtags": ["coding", "programming"]
        }
    """
    parser_classes = (JSONParser,)

    def validate(self, data):
        if data.get('category_id') is None:
            raise exceptions.ValidationError(
                "category_id is null"
            )
        if type(data.get('hashtags')) is not list:
            raise exceptions.ValidationError(
                "hashtags is not list"
            )

    def add_new_hashtags(self, category_id, hashtags):
        for hashtag in hashtags:
            if Hashtag.objects.filter(name__iexact=hashtag).exists():
                continue
            hashtag_obj = Hashtag()
            hashtag_obj.category_id = int(category_id)
            hashtag_obj.name = hashtag.lower()
            hashtag_obj.save()

    def add_data_to_db(self, data):
        category_id = data.get('category_id')
        hashtags = data.get('hashtags')
        if Category.objects.filter(id=category_id).exists():
            self.add_new_hashtags(category_id, hashtags)

    def post(self, request):
        data = request.data
        self.validate(data)
        self.add_data_to_db(data)
        return Response({"Info: ": "Done"})
