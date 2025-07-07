## Django Application Setup Steps

This guide will walk you through setting up the Django train ticket booking application.

### 1. Project Setup

**1.1 Create Django Project and App:**

```
django-admin startproject train_ticket_booking
cd train_ticket_booking
python manage.py startapp bookings
```

**1.2 Install Dependencies:**

```
pip install djangorestframework django-filter psycopg2-binary
```

**1.3 Configure `settings.py`:**

Open `train_ticket_booking/settings.py` and make the following changes:

- **Add `bookings` and `rest_framework` to `INSTALLED_APPS`:**
    
    
    ```
    INSTALLED_APPS = [
        # ... other apps
        'rest_framework',
        'rest_framework.authtoken',
        'bookings',
    ]
    ```
    
- **Configure PostgreSQL Database:**
    
    
    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'train_booking_db',  # Choose a name for your database
            'USER': 'your_db_user',       # Your PostgreSQL username
            'PASSWORD': 'your_db_password', # Your PostgreSQL password
            'HOST': 'localhost',         # Or your PostgreSQL server host
            'PORT': '5432',              # Default PostgreSQL port
        }
    }
    ```
    
    **Important:** Replace `your_db_user` and `your_db_password` with your actual PostgreSQL credentials.
    
- **Set `AUTH_USER_MODEL`:**
    
    
    ```
    AUTH_USER_MODEL = 'bookings.CustomUser'
    ```
    
- **Configure `REST_FRAMEWORK`:**
    
    
    ```
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication', # For browsable API
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ]
    }
    ```
    
- **Add `AdminApiKeyMiddleware` (Optional, based on the prompt's suggestion):**
    
    
    ```
    MIDDLEWARE = [
        # ... other middleware
        'bookings.middleware.AdminApiKeyMiddleware',
    ]
    ```
    
- **Set `ADMIN_API_KEY`:**
    
    
    ```
    ADMIN_API_KEY = 'your_super_secret_admin_api_key' # **CHANGE THIS IN PRODUCTION**
    ```
    
    This key can be used for extra security layers for admin routes, though `IsAdminUser` permission handles primary role-based access.
    
- **Set `TIME_ZONE`:**
    
    
    ```
    TIME_ZONE = 'Asia/Kolkata' # Or your desired timezone
    ```

### 2. Setup Postgres

1. Pull PostgreSQL Image

```
docker pull postgres:16

```

2. Start PostgreSQL Container

```
docker run --name railway-db \
  -e POSTGRES_DB=train_booking_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=user \
  -p 5432:5432 \
  -d postgres:16

```


### 3. Migrations and Superuser

**3.1 Make and Apply Migrations:**

Bash

```
python manage.py makemigrations bookings
python manage.py migrate
```

**3.2 Create a Superuser (Admin):**

Bash

```
python manage.py createsuperuser
```

Follow the prompts to create an admin user. Set their role to 'admin' when prompted (if you use the Django admin, you can later edit the user and set their `role` field to `admin`).


### 4. Run the Development Server

Bash

```
python manage.py runserver
```

Your Django application should now be running on `http://127.0.0.1:8000/`.

### 5. Testing Endpoints (Example with `curl`)

#### 5.1 Register User (User Role)

Bash

```
curl -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword", "role": "user"}' http://127.0.0.1:8000/register/
```

You will get a token in the response.

#### 5.2 Login User

Bash

```
curl -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}' http://127.0.0.1:8000/login/
```

This will also return a token. Store this token for authenticated requests.

#### 5.3 Add Station (Admin Only)

First, create an admin user using `createsuperuser` and log in to get their token.

Bash

```
# Assuming you have an admin token
ADMIN_TOKEN="your_admin_token_here"
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token $ADMIN_TOKEN" -d '{"name": "Bengaluru"}' http://127.0.0.1:8000/stations/
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token $ADMIN_TOKEN" -d '{"name": "Chennai"}' http://127.0.0.1:8000/stations/
```

#### 5.4 Add Train (Admin Only)

Bash

```
ADMIN_TOKEN="your_admin_token_here"
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token $ADMIN_TOKEN" -d '{"no": "TRN001", "name": "Express", "source": "Bengaluru", "destination": "Chennai"}' http://127.0.0.1:8000/trains/
```

#### 5.5 Add Trip (Admin Only)

Bash

```
ADMIN_TOKEN="your_admin_token_here"
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token $ADMIN_TOKEN" -d '{"train": "TRN001", "starting_time_date": "2025-07-10T10:00:00Z", "ending_time_date": "2025-07-10T18:00:00Z", "total_seats": 100, "free_seats": 100}' http://127.0.0.1:8000/trips/
```

#### 5.6 Get Availability (Authenticated User/Admin)

Bash

```
USER_TOKEN="your_user_token_here" # Or ADMIN_TOKEN
curl -X GET -H "Authorization: Token $USER_TOKEN" "http://127.0.0.1:8000/availability/?train__source__name=Bengaluru&train__destination__name=Chennai&starting_time_date=2025-07-10"
```

#### 5.7 Book Seat (Authenticated User)

You need the `trip_id` from the availability response.

Bash

```
USER_TOKEN="your_user_token_here"
TRIP_ID="your_trip_id_here" # e.g., 1
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token $USER_TOKEN" -d '{"trip_id": "'"$TRIP_ID"'", "seat_count": 2}' http://127.0.0.1:8000/book-seat/
```

#### 5.8 Get My Bookings (Authenticated User)

Bash

```
USER_TOKEN="your_user_token_here"
curl -X GET -H "Authorization: Token $USER_TOKEN" http://127.0.0.1:8000/my-bookings/
```

#### 5.9 Get My Bookings for a Specific Trip (Authenticated User)

Bash

```
USER_TOKEN="your_user_token_here"
TRIP_ID="your_trip_id_here" # e.g., 1
curl -X GET -H "Authorization: Token $USER_TOKEN" "http://127.0.0.1:8000/my-bookings/$TRIP_ID/"
```

### 6. Accessing Django Admin

You can access the Django admin interface at `http://127.0.0.1:8000/admin/`. Use the superuser credentials you created earlier. From here, you can manage users (and set their roles), stations, trains, trips, and bookings directly.