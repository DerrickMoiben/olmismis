<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Factory Management Process Optimization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        pre {
            background: #eee;
            padding: 10px;
            border-radius: 5px;
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Factory Management Process Optimization</h1>
        <p>Welcome to the Factory Management Process Optimization project! This project aims to optimize the process of managing farmers, fields, and coffee berry weights. It is built using Django and deployed on Render.com.</p>

        <h2>Project Overview</h2>
        <p>This project provides a web application that allows administrators to:</p>
        <ul>
            <li>Register new farmers</li>
            <li>Record the weight of coffee berries for each farmer</li>
            <li>View a dashboard with total coffee weights</li>
            <li>Manage farmer records</li>
        </ul>
        <p>The project leverages Django's robust framework to handle user authentication, form submissions, and database operations.</p>

        <h2>Live Demo</h2>
        <p>You can access the live version of the project at <a href="https://olmismis.onrender.com" target="_blank">https://olmismis.onrender.com</a>.</p>

        <h2>Features</h2>
        <ul>
            <li><strong>User Authentication</strong>: Signup, login, and logout functionality for administrators.</li>
            <li><strong>Farmer Management</strong>: Register new farmers, view all farmers, and delete farmer records.</li>
            <li><strong>Coffee Berry Weight Management</strong>: Record and view the weight of coffee berries for each farmer.</li>
            <li><strong>Dashboard</strong>: View a summary of all farmers and their total coffee berry weights.</li>
        </ul>

        <h2>Technologies Used</h2>
        <ul>
            <li><strong>Backend</strong>: Django</li>
            <li><strong>Database</strong>: Django's built-in SQLite</li>
            <li><strong>Frontend</strong>: HTML, CSS (with Django templates)</li>
            <li><strong>Deployment</strong>: Render.com</li>
        </ul>

        <h2>Getting Started</h2>

        <h3>Prerequisites</h3>
        <p>Ensure you have the following installed:</p>
        <ul>
            <li>Python 3.x</li>
            <li>Django 3.x or later</li>
        </ul>

        <h3>Installation</h3>
        <ol>
            <li><strong>Clone the repository</strong>:
                <pre><code>git clone https://github.com/yourusername/olmismis.git
cd olmismis</code></pre>
            </li>
            <li><strong>Install dependencies</strong>:
                <pre><code>pip install -r requirements.txt</code></pre>
            </li>
            <li><strong>Apply migrations</strong>:
                <pre><code>python manage.py migrate</code></pre>
            </li>
            <li><strong>Run the development server</strong>:
                <pre><code>python manage.py runserver</code></pre>
            </li>
        </ol>
        <p>Visit <a href="http://127.0.0.1:8000" target="_blank">http://127.0.0.1:8000</a> to view the application.</p>

        <h2>Project Structure</h2>
        <ul>
            <li><strong>views.py</strong>: Contains all the view functions handling HTTP requests and rendering templates.</li>
            <li><strong>forms.py</strong>: Contains form definitions for user signup, login, and data entry.</li>
            <li><strong>models.py</strong>: Defines the database models for <code>Farmer</code>, <code>Field</code>, and <code>CoffeeBerries</code>.</li>
            <li><strong>templates/</strong>: HTML templates for rendering the web pages.</li>
        </ul>

        <h2>Deployment</h2>
        <p>The project is deployed on Render.com. Follow these steps to deploy your own version:</p>
        <ol>
            <li><strong>Create a new web service on Render.com</strong>.</li>
            <li><strong>Connect your repository</strong>.</li>
            <li><strong>Specify the build and start commands</strong>:
                <pre><code># Build command
pip install -r requirements.txt
# Start command
gunicorn project_settings.wsgi:application</code></pre>
            </li>
            <li><strong>Set up environment variables</strong> as needed.</li>
        </ol>

        <h2>Usage</h2>

        <h3>User Authentication</h3>
        <ul>
            <li><strong>Signup</strong>: Create a new admin account.</li>
            <li><strong>Login</strong>: Access the dashboard and management features.</li>
            <li><strong>Logout</strong>: End the current session.</li>
        </ul>

        <h3>Farmer Management</h3>
        <ul>
            <li><strong>Register Farmer</strong>: Enter details of a new farmer.</li>
            <li><strong>View Farmers</strong>: See a list of all registered farmers and their total coffee weights.</li>
            <li><strong>Delete Farmer</strong>: Remove a farmer from the database.</li>
        </ul>

        <h3>Coffee Berry Weight Management</h3>
        <ul>
            <li><strong>Enter Weight</strong>: Record the weight of coffee berries for a specific farmer.</li>
            <li><strong>Dashboard</strong>: View a summary of all farmers and their total coffee berry weights.</li>
        </ul>

        <h2>Contributing</h2>
        <p>Contributions are welcome! Please follow these steps to contribute:</p>
        <ol>
            <li><strong>Fork the repository</strong>.</li>
            <li><strong>Create a new branch</strong>:
                <pre><code>git checkout -b feature-name</code></pre>
            </li>
            <li><strong>Make your changes</strong>.</li>
            <li><strong>Commit your changes</strong>:
                <pre><code>git commit -m 'Add some feature'</code></pre>
            </li>
            <li><strong>Push to the branch</strong>:
                <pre><code>git push origin feature-name</code></pre>
            </li>
            <li><strong>Open a pull request</strong>.</li>
        </ol>

        <h2>License</h2>
        <p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>

        <h2>Contact</h2>
        <p>For any inquiries or issues, please open an issue on the repository or contact the project maintainer at <a href="mailto:derrickmoio92@gmail.com">derrickmoio92@gmail.com</a>.</p>

        <hr>

        <p>Thank you for using the Factory Management Process Optimization project!</p>
    </div>
</body>
</html>
