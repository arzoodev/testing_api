# Implementing JWT Authentication

## 1. Install Dependencies:
Run the following command to install the required package:
```
pip install djangorestframework-simplejwt
```

2. Update settings.py:
Add the necessary apps in the INSTALLED_APPS section:
```INSTALLED_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
]
```
Then configure the REST framework for JWT authentication:
```
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```
3. Configure URLs:
Update urls.py to add routes for obtaining and refreshing JWT tokens:

```from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```
4. How to Use JWT Tokens:
Obtain Token:
Make a POST request to /api/token/ with the following payload:

```
{
  "username": "Super_username",
  "password": "Superuser_password"
}
```
You will receive two tokens: the **access token** and the **refresh token**.

Include the Access Token:
Use the **access token** in your API requests by adding it to the **Authorization header**
```
Authorization: Bearer <access_token> 
```
The **refresh token** can generate a new **access token** when the current one expires.

5. Access Swagger UI:
You can access the Swagger UI at:

`http://127.0.0.1:8000/swagger/`
