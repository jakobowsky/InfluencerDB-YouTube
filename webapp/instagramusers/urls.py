from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryView,
    InstagramAccountView,
    InstagramPostView,
    InstagramAccountReportView,
    HashtagView,
    HashtagMultiAddView,
    AddNewAccountView,
    UpdateAccountsView,
)

router = DefaultRouter(trailing_slash=False)
router.register('categories', CategoryView)
router.register('instagram_accounts', InstagramAccountView)
router.register('instagram_posts', InstagramPostView)
router.register('instagram_accounts_reports', InstagramAccountReportView)
router.register('hashtags', HashtagView)

urlpatterns = [
    path('', include(router.urls)),
    path('add_multi_hashtags/', HashtagMultiAddView.as_view()),
    path('add_new_account/', AddNewAccountView.as_view()),
    path('update_accounts/', UpdateAccountsView.as_view()),
]
