# Sports Club Volunteering App

A Django application to coordinate volunteering for sports club matches. Members can sign up, select a home team, view matches, and volunteer for available slots.

---

## Features

- User signup with optional **home team** selection
- Edit profile and change password
- View upcoming matches and volunteer for open slots
- Matches display up to 3 volunteers horizontally
- Users cannot volunteer for matches of their own home team
- Admin interface for managing matches, home teams, and volunteer slots
- Automatic creation of volunteer slots per match

---

## Requirements

- Python 3.12+
- Django 5.2+
- SQLite (default; can be swapped for another DB)
- (Optional) WSL if using Windows for local development

---

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd volunteer-app
    ```

2. **Create a virtual environment and activate it**
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/Mac
    .venv\Scripts\activate      # Windows
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a superuser for the admin**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server and access the app**
    ```bash
    python manage.py runserver
    ```

    Main app: http://127.0.0.1:8000/  
    Admin: http://127.0.0.1:8000/admin/

---

## Notes

- Volunteer slots: Each match automatically creates 3 slots for volunteers.
- Home team restriction: Users cannot volunteer for matches of their own home team.
- Profile: Users can edit their profile and select/change home team.
- Styling: Simple responsive UI with horizontal volunteer slots and clearly styled buttons.

---

## Future Improvements

- Add notifications for upcoming matches
- Add filtering/search for matches by date or location
- Add an exchange page, for players to trade slots