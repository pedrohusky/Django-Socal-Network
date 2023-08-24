import bleach
from django import template

from ..models import UserProfile

register = template.Library()

@register.filter(name='split_string')
def split_string(value):
    file_name = value.split('/')[-1]
    if "." in file_name:
        return file_name
    else:
        return value

@register.filter(name='log')
def log(value):
    print(value)

@register.filter(name='is_friend')
def is_friend(user, profile_user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile.friends.filter(username=profile_user.username).exists()
    except UserProfile.DoesNotExist:
        return False


@register.filter(name='is_blocked')
def is_blocked(user, profile_user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        return user_profile.blocked_users.filter(username=profile_user.username).exists()
    except UserProfile.DoesNotExist:
        return False

@register.filter(name='find_user')
def find_user(username):
    try:
        user_profile = UserProfile.objects.get(user__username=username)
        return user_profile
    except UserProfile.DoesNotExist:
        return None


@register.filter(name='sanitize_html')
def sanitize_html(value):
    allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br']
    allowed_attributes = {'p': ['style'], 'br': []}  # Add any allowed attributes here

    cleaned_value = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned_value

