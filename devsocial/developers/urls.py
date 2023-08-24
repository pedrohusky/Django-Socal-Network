from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('profile/<str:username>/', views.ProfileView, name='profile'),
    path('feed/', views.FeedView, name='feed'),
    path('post/<int:post_id>/', views.PostDetailView, name='post_detail'),
    path('post_creation', views.create_post, name='post_creation'),  # Add this line
    path('register/', views.create_account_view, name='register'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('profile/<str:username>/add_friend/', views.add_friend, name='add_friend'),
    path('profile/<str:username>/remove_friend/', views.remove_friend, name='remove_friend'),
    path('profile/<str:username>/block_user/', views.add_blocked_user, name='block_user'),
    path('profile/<str:username>/remove_block/', views.remove_from_blocked_users, name='remove_block'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('add_reaction/<int:object_id>/<str:is_comment>/<str:reaction_type>/', views.add_reaction, name='add_reaction'),
    path('get_updated_posts/', views.get_updated_posts, name='get_updated_posts'),
    path('custom_logout/', views.custom_logout, name='custom_logout'),
path('messages/', views.MessageListView.as_view(), name='messages'),
    path('conversation_detail/<int:conversation_id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('send_message/<int:conversation_id>/', views.SendNewMessageView.as_view(), name='send_message'),
path('start_conversation/<int:user_id>/', views.StartConversationView.as_view(), name='start_conversation'),
path('fetch_messages/<int:conversation_id>/', views.FetchMessages.as_view(), name='fetch_messages'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
