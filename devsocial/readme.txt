This is a Django test project created to test my skills to develop a "social network".

What was used to do this:
 - Django
 - Python and JS
 - HTML and CSS

What my 'social network' does:
 - It has a login screen, and a register screen.
 - It has a feed, showing all posts from all users (This was meant to connect all different users).
 - The same feed, also has a option to just show friends posts (and yours too), to close the circle of people in the posts.
 - It supports adding and blocking users. When blocking a user, if you were friends, it will be removed. Vice versa.
 - Chat support! After add a friend, they'll show on the right side of the feed. The chat auto-updates with new messages using 'pooling'.
 - In the posts, it supports sending all types of files. Images are shown, links are generated to be downloaded by any user.

My objectives with that:
- Create a social network where everyone can post anything, without filters. Somehow acting like a new megaupload but fused with facebook.

What I've learned:
 - I've learned a few tricks to make a Django server. It is awesome.
 - I've learned a little more of HTML and CSS and how they behave.
 - I've created API endpoints for the server to communicate with the users.
 - I've setted up the logics to handle files and everything.

How to run:
 - python manage.py migrate (if you change something in the Models.py file, you must run: python manage.py makemigrations )
 - python manage.py runserver
