import bleach
from bs4 import BeautifulSoup
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from django.views import View

from .models import UserProfile, Post, Comment, Conversation, Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

def sanitize_html(value):
    allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br']
    allowed_attributes = {'p': ['style'], 'br': []}  # Add any allowed attributes here

    cleaned_value = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned_value


def ProfileView(request, username):
    user = User.objects.get(username=username)
    profile = UserProfile.objects.get(user=user)
    posts = Post.objects.filter(user=user)
    return render(request, 'profile/profile.html', {'profile': profile, 'posts': posts})


def FeedView(request):
    show_all = request.GET.get('show_all') == '1'
    friends = []
    conversations = []

    if request.user.is_authenticated:
        user = request.user
        friends = user.userprofile.friends.all()

        if show_all:
            posts = Post.objects.all().order_by('-created_at')
        else:
            friend_posts = Post.objects.filter(user__in=friends)
            user_posts = Post.objects.filter(user=user)
            posts = (friend_posts | user_posts).order_by('-created_at')

        # Fetch the list of friends for the logged-in user
        friends = request.user.userprofile.friends.all()

        # Fetch conversations for the logged-in user
        conversations = Conversation.objects.filter(participants=request.user)

        # Fetch messages for each conversation
        for conversation in conversations:
            conversation.messages = Message.objects.filter(conversation=conversation)
    else:
        posts = Post.objects.all().order_by('-created_at')

    # Fetch comments for each post
    for post in posts:
        post.comments = Comment.objects.filter(post=post)



    return render(request, 'feed/feed.html',
                  {'posts': posts, 'show_all': show_all, 'friends': friends, 'conversations': conversations})

def PostDetailView(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = Comment.objects.filter(post=post)
    return render(request, 'post/post_detail.html', {'post': post, 'comments': comments})


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)


def create_account_view(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_picture_form.is_valid():
            user = user_form.save()

            # Create a UserProfile instance for the user
            profile_picture = profile_picture_form.cleaned_data['profile_picture']
            UserProfile.objects.create(user=user, profile_picture=profile_picture)

            # Log the user in
            login(request, user)
            return redirect('feed')
    else:
        user_form = UserCreationForm()
        profile_picture_form = ProfilePictureForm()

    return render(request, 'registration/create_account.html',
                  {'user_form': user_form, 'profile_picture_form': profile_picture_form})

@login_required
def create_post(request):
    response_data = {'success': False}

    if request.method == 'POST':
        content = request.POST['content']
        file = request.FILES.get('file')  # Get uploaded file
        user = request.user

        if content.strip() or file:
            post = Post.objects.create(user=user, content=sanitize_html(content))

            if file:
                post.attachment = file
                response_data['file'] = post.attachment.url
                post.save()

            response_data['success'] = True
            response_data['id'] = post.id
            response_data['created'] = post.created_at
            response_data['content'] = content
            response_data['username'] = post.user.username
            response_data['image'] = post.user.userprofile.profile_picture.url

    return JsonResponse(response_data)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.user:
        post.delete()

    return redirect('feed')  # Redirect to the appropriate page after deletion


@login_required
def add_friend(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.blocked_users.contains(target_user):
            user_profile.blocked_users.remove(target_user)
        user_profile.friends.add(target_user)
        user_profile.save()

    return redirect('profile', username=username)


@login_required
def remove_friend(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.friends.remove(target_user)
        user_profile.save()

    return redirect('profile', username=username)

@login_required
def add_blocked_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        target_user_profile = UserProfile.objects.get(user=target_user)
        if target_user_profile.friends.contains(request.user):
            target_user_profile.friends.remove(request.user)
        if user_profile.friends.contains(target_user):
            user_profile.friends.remove(target_user)
        user_profile.blocked_users.add(target_user)
        print(f"User {target_user} was blocked")
        user_profile.save()

    return redirect('profile', username=username)


@login_required
def remove_from_blocked_users(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.blocked_users.remove(target_user)
        print(f"User {target_user} was unblocked")
        user_profile.save()

    return redirect('profile', username=username)

@login_required
def edit_post(request, post_id):
    # Retrieve the post using post_id
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        # If the logged-in user is not the post creator, return a forbidden response
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        new_content = request.POST['edited_content']
        file = request.FILES.get('file')  # Get uploaded file

        url = ''

        if file:
            post.attachment = file
            post.save()
            try:
                url = post.attachment.url
            except Exception:
                url = ''

        post.content = sanitize_html(new_content)
        post.save()

        return JsonResponse({'success': True, 'url': url})

    return render(request, 'edit_post.html', {'post': post})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        comment_content = request.POST.get('comment_content')

        if comment_content:
            comment = Comment.objects.create(user=request.user, post=post, content=sanitize_html(comment_content))

            # You can construct a dictionary with the new comment's details
            comment_data = {
                'success': True,
                'comment_id': comment.id,
                'likes': comment.likes.all().count(),
                'dislikes': comment.dislikes.all().count(),
                'comment_content': comment.content,
                'username': comment.user.username,
                'user_id': comment.user.id,
                'post_id': post.id,
                'user_image': comment.user.userprofile.profile_picture.url,
                'created_at': comment.created_at.strftime('%B %d, %Y %I:%M %p')  # Format the datetime
            }

            # Return a JSON response with the new comment's details
            return JsonResponse(comment_data)
        else:
            # Return an error response if comment content is empty
            return JsonResponse({'success': False, 'error': 'Comment content cannot be empty'})

    # Return an error response if the request is not POST
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def add_reaction(request, object_id, is_comment, reaction_type):
    if request.method == 'POST':
        user = request.user
        if is_comment == "true":
            obj = get_object_or_404(Comment, id=object_id)
        else:
            obj = get_object_or_404(Post, id=object_id)

        if reaction_type == 'like':
            reactions = obj.likes
            other_reactions = obj.dislikes
        elif reaction_type == 'dislike':
            reactions = obj.dislikes
            other_reactions = obj.likes
        else:
            return JsonResponse({'success': False, 'error': 'Invalid reaction type'})

        if user in reactions.all():
            reactions.remove(user)
        else:
            reactions.add(user)
            other_reactions.remove(user)  # Remove user from other reactions if they're reacting

        reactions_count = sum(1 for _ in reactions.all())
        other_reactions_count = sum(1 for _ in other_reactions.all())
        return JsonResponse({'success': True, 'reactions': reactions_count, 'other': other_reactions_count})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_updated_posts(request):
    # Retrieve the updated list of posts (similar to your existing logic)
    show_all = request.GET.get('show_all') == '1'

    if request.user.is_authenticated:
        user = request.user
        friends = user.userprofile.friends.all()

        if show_all:
            posts = Post.objects.all().order_by('-created_at')
        else:
            friend_posts = Post.objects.filter(user__in=friends)
            user_posts = Post.objects.filter(user=user)
            posts = (friend_posts | user_posts).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')

    # Fetch comments for each post
    for post in posts:
        post.comments = Comment.objects.filter(post=post)

        # Render the updated post list HTML as a string
    updated_html = render_to_string('post/post_card.html', {'posts': posts, 'user': request.user})

    # Return the updated HTML and extracted scripts as JSON
    return JsonResponse({'updated_html': updated_html})

def custom_logout(request):
    # Clear session data for the user
    request.session.flush()

    # Log out the user
    logout(request)

    # Customize the response after logout
    return redirect('login')  # Redirect to the homepage or any other page


class MessageListView(View):
    def get(self, request):
        conversations = Conversation.objects.filter(participants=request.user)
        return render(request, 'messages/conversation_list.html', {'conversations': conversations})

class ConversationDetailView(View):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        messages = Message.objects.filter(conversation=conversation)
        return render(request, 'messages/conversation_detail.html', {'conversation': conversation, 'messages': messages})


class SendNewMessageView(View):
    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
        messages = Message.objects.filter(conversation=conversation)

        # Construct the updated messages list HTML
        updated_messages_html = ''
        for message in messages:
            updated_messages_html += f'<li>{message.sender.username}: {message.content}</li>'
        updated_messages_html += ''

        # Construct the response
        response_data = {
            'success': True,
            'updated_messages_html': updated_messages_html,
        }
        return JsonResponse(response_data)


class FetchMessages(View):
    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        messages = Message.objects.filter(conversation=conversation)

        # Construct the updated messages list HTML
        updated_messages_html = ''
        for message in messages:
            updated_messages_html += f'<li>{message.sender.username}: {message.content}</li>'
        updated_messages_html += ''

        # Construct the response
        response_data = {
            'success': True,
            'updated_messages_html': updated_messages_html,
        }
        return JsonResponse(response_data)




class StartConversationView(View):
    def get(self, request, user_id):
        # Get the user to start the conversation with
        other_user = get_object_or_404(User, id=user_id)

        # Check if a conversation between users already exists
        conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()

        if not conversation:
            # Create a new conversation if one doesn't exist
            conversation = Conversation.objects.create(is_one_on_one=True)
            conversation.participants.add(request.user, other_user)
            conversation.save()

        # Get messages for the conversation
        messages = Message.objects.filter(conversation=conversation)

        # Render the conversation detail template with the conversation and messages
        context = {
            'conversation': conversation,
            'messages': messages,
        }
        return render(request, 'messages/conversation_detail.html', context)
