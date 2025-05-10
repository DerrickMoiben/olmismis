# Factory Management Process Optimization

Welcome to the Factory Management Process Optimization project! This project aims to optimize the process of managing farmers, fields, and coffee berry weights. It is built using Django and deployed on Render.com.

## Project Overview

This project provides a web application that allows administrators to:

- Register new farmers
- Record the weight of coffee berries for each farmer
- View a dashboard with total coffee weights
- Manage farmer records
- Handle seasonal updates and harvest management
- Process payments based on coffee weights

The project leverages Django's robust framework to handle user authentication, form submissions, and database operations using **SQLite**.

## Features

- **User Authentication**: Signup, login, and logout functionality for administrators.
- **Farmer Management**: Register new farmers, view all farmers, and delete farmer records.
- **Coffee Berry Weight Management**: Record and view the weight of coffee berries for each farmer.
- **Dashboard for Cashiers**: 
  - **Register Farmers**: Interface for cashiers to enter new farmer details.
  - **Record Weights**: Functionality to log the weight of coffee berries for registered farmers.
- **Season Management**: Track when seasons start and manage harvests.
- **Payment Processing**: Calculate payments per kilo of coffee berries and process transactions.
- **Messaging**: Send notifications using the African Talking API for weight adjustments and harvest updates.

## Technologies Used

- **Backend**: Django
- **Database**: SQLite (Django's built-in database)
- **Frontend**: HTML, CSS (with Django templates)
- **Deployment**: Render.com

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Django 3.x or later

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/olmismis.git
    cd olmismis
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Apply migrations**:
    ```sh
    python manage.py migrate
    ```

4. **Run the development server**:
    ```sh
    python manage.py runserver
    ```

Visit `http://127.0.0.1:8000` to view the application.

## Project Structure

- **views.py**: Contains all the view functions handling HTTP requests and rendering templates.
- **forms.py**: Contains form definitions for user signup, login, and data entry.
- **models.py**: Defines the database models for `Farmer`, `Field`, and `CoffeeBerries`.
- **templates/**: HTML templates for rendering the web pages.
- **dashboard/**: Contains functionalities for cashier operations, including registering farmers and recording weights.
- **apis/**: Handles integration with the African Talking API for messaging.

## Usage

### User Authentication

- **Signup**: Create a new admin account.
- **Login**: Access the dashboard and management features.
- **Logout**: End the current session.

### Farmer Management

- **Register Farmer**: Enter details of a new farmer through the cashier dashboard.
- **View Farmers**: See a list of all registered farmers and their total coffee weights.
- **Delete Farmer**: Remove a farmer from the database.

### Coffee Berry Weight Management

- **Enter Weight**: Cashiers can record the weight of coffee berries for a specific farmer.
- **Dashboard**: View a summary of all farmers and their total coffee berry weights, including seasonal updates and harvest management.
- **Payment Processing**: Calculate payments based on the weight of coffee berries and process transactions.

### Messaging

- **Notifications**: Send messages to farmers regarding weight adjustments and harvest updates using the African Talking API.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the repository**.
2. **Create a new branch**:
    ```sh
    git checkout -b feature-name
    ```
3. **Make your changes**.
4. **Commit your changes**:
    ```sh
    git commit -m 'Add some feature'
    ```
5. **Push to the branch**:
    ```sh
    git push origin feature-name
    ```
6. **Open a pull request**.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please open an issue on the repository or contact the project maintainer at [derrickmoio92@gmail.com](mailto:derrickmoio92@gmail.com).

---

Thank you for using the Factory Management Process Optimization project!
