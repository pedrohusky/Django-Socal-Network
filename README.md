# Django Social Network Test Project

This is a test project designed to demonstrate my skills in web development using Django, Python, JavaScript, HTML, and CSS. The project simulates a basic social network with various features commonly found in such platforms.

## How to Run

1. Run pip install requirements.txt
2. Run database migrations: `python manage.py migrate`
3. Create migrations if models change: `python manage.py makemigrations`
4. Start the development server: `python manage.py runserver`

## Features

- **Authentication System**: The project includes a secure user authentication system with login and registration screens.

- **Feed**: The main page displays a feed that shows posts from all users, providing a platform for users to share content.

- **Feed Filtering**: Users can choose to view only posts from their friends, creating a more personalized feed experience.

- **Friendship Management**: Users can add and block other users. When a user blocks another, any existing friendship is severed.

- **Chat System**: After becoming friends, users can engage in real-time chat through the right-side chat panel. The chat updates automatically (pooling, every 2s) with new messages, enhancing the user experience.

- **File Sharing**: The platform supports various file types, including images. Images are displayed directly in the feed, and links are generated for file downloads.

## Objectives

The primary goal of this project was to build a functional social network that replicates key functionalities of established platforms while serving as a showcase for my web development skills.

## Technologies Used

- Django: A powerful Python web framework used for creating the backend logic and handling data.

- Python: The programming language utilized for server-side scripting and logic.

- JavaScript: Implemented to enhance user interactions and provide real-time updates.

- HTML and CSS: Used for structuring and styling the frontend interface.

## Learning Outcomes

- Gain Proficiency in Django: Through building the project, I learned how to set up a Django server, create API endpoints for communication, and manage databases.

- Improve Frontend Skills: I enhanced my understanding of HTML and CSS by creating a visually appealing user interface.

- Handle File Uploads: I developed logic to handle file uploads and display them appropriately in the feed.
