from django.urls import path
from .views import PostList, PostDetail, Posts, PostSearch, PostAdd, UpdatePost, PostDelete, upgrade_me, subscribe_to_category, unsubscribe_from_category, CategoryDetail, like_post, dislike_post

app_name = 'news'

urlpatterns = [
    path('', PostList.as_view(), name='home'),
    path('<int:pk>/', PostDetail.as_view(), name='news_id'),
    path('search/', PostSearch.as_view(), name='search'),
    path('add/', PostAdd.as_view(), name='add'),
    path('<int:pk>/edit/', UpdatePost.as_view(), name='edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='delete'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('category/<int:pk>/subscribe/', subscribe_to_category, name='subscribe'),
    path('category/<int:pk>/unsubscribe/', unsubscribe_from_category, name='unsubscribe'),
    path('category/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('<int:pk>/like/', like_post, name='like_post'),
    path('<int:pk>/dislike/', dislike_post, name='dislike_post'),
]

