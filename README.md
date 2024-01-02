# Expense Tracker

Expense Tracker is a comprehensive expense reporting system designed to simplify the process of recording and tracking purchases. 

## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Languages and Frameworks Used](#languages-and-frameworks-used)
- [Installation](#installation)
- [Backend Documentation](#backend-documentation)
- [License](#license)

## Features

- **Receipt Upload**: Users can easily upload receipts, and the system will automatically extract via OCR and record the necessary information.
- **Manual Reporting**: For those who prefer a hands-on approach, the system also supports manual entry of purchase details.
- **Detailed Reporting**: Expense Tracker generates detailed, interactive reports based on the recorded data. This allows users to easily visualize and understand their spending habits.
- **Secure Login**: System also features mordern secure login that no one else can access user's own sensitive data
- **Google Login**: For added convenience, users can also log in using their Google accounts.

## Usage

To use Expense Tracker, simply log in, and choose to either upload a receipt or manually enter your purchase details. The system will take care of the rest, automatically updating your reports to reflect the new data.

## Languages and Frameworks Used

- **Python**: The backend of the application is built with Python.
- **Flask**: Flask is used as the web framework.
- **Flask-login**: Flask-login is used to handle user login session.
- **Jinja2**: Jinja2 is used for templating and generating HTML dynamically.
- **JavaScript**: JavaScript is used for client-side scripting.
- **CSS**: CSS is used for styling the web pages.
- **SQLAlchemy**: SQLAlchemy is used as the ORM for database operations.
- **SQLite**: SQLite is used as the database.
- **OAuth2**: OAuth2 is used for Google Login.
- **Pillow**: Pillow is used to handle the images upload by users
- **Tesseract OCR**: Tesseract OCR is used for extracting text from uploaded receipt images.
- **Werkzeug**: werkzeug.security is used to generate secure password hashing to store in server database.

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/huajie-zhong/expense-tracker.git
   cd expense-tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
Create a .env file in the project root with the following variables:
    ```bash
    SECRET_KEY=your_secret_key
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    TESSERACT_PATH=your_tesseract_installation_location
    ```

4. Run the Flask application:
   ```bash
   python app.py
   ```
   The application will be accessible at http://localhost:8000.

## Backend Documentation
## Render Pages

### 1. Main Page
- **URL**: `/`
- **Method**: `GET`
- **Description**: Renders the main page of the application.

### 2. Currency Page
- **URL**: `/currency/`
- **Methods**: `GET`, `POST`
- **Description**: Renders the currency page. If the method is `POST`, it redirects to the `/currency` route.

### 3. Header Page
- **URL**: `/header/`
- **Methods**: `GET`, `POST`
- **Description**: Renders the header page. If the method is `POST`, it redirects to the `/header` route.

### 4. Report Page
- **URL**: `/report/`
- **Methods**: `GET`, `POST`
- **Description**: Renders the report page. If the method is `POST`, it redirects to the `/report` route.

### 5. Login Page
- **URL**: `/login/`
- **Methods**: `GET`, `POST`
- **Description**: Renders the login page. If the method is `POST`, it redirects to the `/login` route.

## API Routes

### 1. User Login
- **URL**: `/api/login/`
- **Method**: `POST`
- **Description**: 
  - Retrieves username and password from the request body.
  - Verifies user existence in the database and checks the correctness of the password.
  - Generates access and refresh tokens.
  - Sets access and refresh tokens as cookies in the response.

### 2. Refresh Token
- **URL**: `/api/refresh-token/`
- **Method**: `POST`
- **Description**: 
  - Refreshes the access token using a provided refresh token.
  - Sets the new access token as a cookie in the response.

### 3. User Logout
- **URL**: `/api/logout/`
- **Method**: `POST`
- **Description**: 
  - Logs out the user.
  - Clears access and refresh tokens by setting their expiration to the immediate time.

### 4. User Registration
- **URL**: `/api/register/`
- **Method**: `POST`
- **Description**: 
  - Registers a new user.
  - Hashes the password and stores the user in the database.

### 5. Submit Expense
- **URL**: `/api/submit_expense/`
- **Method**: `POST`
- **Description**: 
  - Takes receipt or amount as input and returns the amount and type of expense.
  - Records the expense in the database.

## OAuth2 Login

### 6. Get Expenses
- **URL**: `/api/get_expenses/`
- **Method**: `GET`
- **Description**: 
  - Returns all expenses for the authenticated user.

### 7. OAuth2 Authorization
- **URL**: `/api/authorize/<provider>`
- **Method**: `GET`
- **Description**: 
  - Authorizes the user with the specified OAuth2 provider.

### 8. OAuth2 Callback
- **URL**: `/api/callback/<provider>`
- **Method**: `GET`
- **Description**: 
  - Handles the OAuth2 callback, exchanging the code for an access token.

### Error Handling
- **404 Page Not Found**
  - **URL**: `*` (catch-all)
  - **Method**: `GET`
  - **Description**: Renders a custom 404 page.

- **Unauthorized Handler**
  - **URL**: `*` (catch-all)
  - **Method**: `GET`
  - **Description**: Handles unauthorized access with a 401 response.

## Lisence
This project is licensed under the GNU General Public License v3.0.


## Future Enhancements

We are constantly working to improve Expense Tracker. Future updates will include more detailed reports, support for multiple currencies, and improved receipt scanning accuracy.
