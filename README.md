# Ikramov UZ - Django Portfolio Project

A Django-based portfolio website built with Bootstrap template "MyPage".

## Project Structure

```
ikramov_uz/
├── main/                   # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── index/                 # Main app for portfolio pages
│   ├── views.py          # View functions
│   ├── urls.py           # App URL patterns
│   └── models.py         # Database models
├── templates/             # Django templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── portfolio-details.html
│   ├── service-details.html
│   └── starter-page.html
├── static/               # Static files
│   └── MyPage/          # Bootstrap template assets
└── staticfiles/         # Collected static files
```

## Features

- **Responsive Design**: Built with Bootstrap 5
- **Modern UI/UX**: Clean and professional design
- **Django Integration**: Proper Django template structure
- **Static File Management**: Configured for development and production
- **Multiple Pages**: Home, Portfolio Details, Service Details, Starter Page

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Home: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Available Pages

- **Home** (`/`): Main portfolio page with hero section, about, and contact
- **Portfolio Details** (`/portfolio-details/`): Individual project showcase
- **Service Details** (`/service-details/`): Service information and pricing
- **Starter Page** (`/starter-page/`): Getting started information

## Technologies Used

- Django 5.2.5
- Bootstrap 5.3.8
- HTML5/CSS3
- JavaScript
- SQLite (development)

## Configuration

The project is configured with:
- Static files serving for development
- Template inheritance with base template
- URL routing for all pages
- Proper Django settings for production deployment

## Customization

To customize the portfolio:
1. Update content in templates/
2. Modify static files in static/MyPage/assets/
3. Add new pages by creating views and templates
4. Update the navigation in base.html

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving (nginx/Apache)
4. Configure environment variables
5. Use `python manage.py collectstatic` for static files
