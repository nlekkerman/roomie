# roomie

Householding App

# Roomie App

**Roomie App** is a comprehensive solution for property management that caters to landlords, house captains, and tenants. Designed to streamline communication, payment tracking, and role-based responsibilities, this app ensures efficient management of shared living spaces. By combining a Django-powered backend with a React-based frontend, Roomie App delivers a robust and user-friendly experience.

The app simplifies the complexities of managing rent, utility bills, and user roles in multi-tenant properties. With role-based access control, each user has a tailored experience, whether it's tracking rent payments, managing tenant profiles, or overseeing property details.

Roomie App is built to handle real-world challenges in property management, such as calculating shared expenses, maintaining user accountability, and ensuring transparency in payments.

---

## Features

### General Features

- **Role-Based Access Control**:
  - Users are assigned roles such as **Landlord**, **House Captain**, or **Tenant**, each with distinct permissions and views.
- **Payment Tracking**:
  - Tracks rent payments, utility bills (electricity, garbage), and deposits for tenants.
  - Provides a clear overview of pending and completed payments.
- **Roomie Score**:
  - A scoring system (1–5) to evaluate tenant performance or compliance.
- **Mobile-Responsive Design**:
  - Fully responsive user interface for seamless use on desktop and mobile devices.

---

### Backend Features (Django)

- **Custom User Profiles**:
  - Extends the default Django `User` model with a `UserProfile` for additional fields like role, payment history, and roomie score.
- **Admin Dashboard**:
  - Django Admin integration for managing user profiles, payments, and roles.
- **Data Validation**:
  - Ensures accurate data input, such as valid payment amounts and roomie score constraints.
- **APIs for Frontend Integration**:
  - RESTful APIs for user authentication, profile management, and payment tracking.

---

### Frontend Features (React)

- **Dynamic Dashboard**:
  - Role-specific dashboards for landlords, house captains, and tenants.
  - Displays relevant data such as payment summaries, user profiles, and notifications.
- **Interactive Forms**:
  - User-friendly forms for updating profiles, making payments, and managing roles.
- **State Management**:
  - Uses React Context or Redux to manage global application state.
- **Real-Time Updates**:
  - Fetches data from the backend and dynamically updates the UI.
- **Error Handling**:
  - Displays user-friendly error messages for API failures or invalid input.

---

### Extended Functionalities

- **Multi-Tenant Support**:
  - Handles multiple tenants within a single property, assigning individual payment responsibilities.
- **Bill Splitting**:
  - Automatically calculates and splits shared expenses among tenants.
- **Payment History**:
  - Provides a detailed history of all payments made, categorized by type (rent, electricity, garbage).
- **Search and Filter**:
  - Allows users to search and filter profiles or payments for quick access to information.
- **Notifications**:
  - Sends reminders for pending payments or updates on completed transactions.
