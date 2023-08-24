from django.contrib import admin
from .models import UserProfile, Post, Comment, Message, Conversation

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(Conversation)
