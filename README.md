# GRAND BLUE - MOBILE APP
# ICT 2207Y(3) – Web and Mobile Application Development

Project Title: GRAND BLUE - Flet Mobile Application

# Team Members:
1. Gangaram Kushan - 2414333
2. Ramjug Karishma - 2414539
3. Ghoorah Bhuvanesh - 2313458
4. Mohess Shreeyash - 2414197
5. Bhujun Yuvraj - 2414631
6. Bundhoo Bhavesh - 2414708

# Important Note
All group members agree that the marks for this project must be shared and allocated equally among all six members.

# 1. Project Overview
GRAND BLUE Mobile App is a Flet-based cross-platform mobile application that provides customers with seamless access to water-based activities in Mauritius. Built with Python and Flet, the application offers a modern, responsive interface for browsing, booking, and managing activities on both iOS and Android devices. It also includes a geolocation feature that allows users to view their real-time location and discover nearby activities.

The project was developed using:

1. Flet (UI framework for cross-platform mobile apps)
2. Python (backend logic)
3. Django REST API (backend integration)
4. HTTP client libraries (api_client for API communication)
5. Responsive design with custom components

# 2. Features 
**For Customers**

- User Authentication (Login/Register)
- Browse activity catalogue with filtering by activity type
- View detailed activity information with reviews and ratings
- Search for nearby activities based on location
- Book activities with date and group size selection
- Secure payment processing
- Manage bookings (view, cancel)
- Leave and view reviews
- Manage user profile (edit information, change password)
- Receive notifications about bookings and updates
- Dark mode support
- Persistent session management with JWT tokens
- Enable their live location to get nearby activities

**For Visitors**

- Browse available activities without authentication
- Register for an account
- Login to access booking features
- Enable their live location to get nearby activities

# 3. System Technical Summary
**Models & Components:**
- Activity Models (Activity, ActivityImage, ActivityHighlight)
- Booking System (create, view, cancel bookings)
- Payment Integration
- Review & Rating System
- User Authentication & Profile Management
- Notification System

**Architecture:**
- Views: Modular screen/view components (login, catalogue, booking, payment, etc.)
- API Client: Centralized HTTP client for RESTful API communication
- Utils: Configuration, API endpoints, constants, and activity API functions
- Components: Reusable UI components (bottom navigation, custom widgets)

**Security Features:**
- JWT token-based authentication
- Secure password hashing (backend)
- HTTPS for API communication
- Token refresh mechanism
- Persistent session storage

**UX Enhancements:**
1. Responsive design for multiple screen sizes
2. Intuitive navigation with bottom navigation bar
3. Real-time activity filtering and search
4. Smooth transitions and animations
5. Loading indicators for async operations
6. Error handling with user-friendly messages

# 4. How to run the project

**Requirements:**
1. Python 3.8 or higher
2. Flet framework
3. requests library
4. python-dotenv (for environment variables)
5. Internet connection for API calls

# 5. API Integration

The mobile app communicates with the Django REST API backend. Key endpoints include:

- Authentication: /auth/, /auth/token/refresh/
- Activities: /activities/, /activities/<activity_id>/, /activities-catalogue/
- Bookings: /bookings/, /bookings/<pk>/, /bookings/create/
- Payments: /payments/
- Reviews: /review/
- Profile: /userprofile/
- Notifications: /notifications/<user_id>/
- Nearby Activities: /nearmeactivity/

JWT tokens are used for authenticated requests and stored locally for session persistence.

# 6. Conclusion

GRAND BLUE Mobile App is a fully functional cross-platform mobile application that seamlessly integrates with the Django backend. It provides customers with a convenient way to discover, book, and manage water-based activities on the go. The app ensures usability, security, and performance while delivering a modern mobile experience.
