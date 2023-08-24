from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


def user_post_attachment_path(instance, filename):
    # Generate a unique filename based on the user's username, timestamp, and filename
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    username = instance.user.username
    extension = filename.split('.')[-1]
    new_filename = f"user_{username}/post_attachments/{timestamp}.{extension}"
    return new_filename

def user_profile_picture_path(instance, filename):
    # Generate a unique filename based on the user's username, timestamp, and filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    username = instance.user.username
    extension = filename.split('.')[-1]
    new_filename = f"user_{username}/profile_pics/{timestamp}.{extension}"
    return new_filename

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, blank=True, null=True)
    friends = models.ManyToManyField(User, related_name='user_friends', blank=True)
    blocked_users = models.ManyToManyField(User, related_name='user_blocked_users', blank=True)



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=user_post_attachment_path, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='post_dislikes', blank=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True)


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    is_one_on_one = models.BooleanField(default=True)  # Indicates if the conversation is one-on-one

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)



