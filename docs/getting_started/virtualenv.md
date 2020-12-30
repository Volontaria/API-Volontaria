# Getting started with manual installation

We're going to install and configure a basic instance of this API

## Clone the project

The project use [Git](https://git-scm.com/) and is accessible on [Github](https://github.com/).

First of all you need to clone the project on your computer.

To contribute on this repository, use a fork:
```
git clone https://github.com/your_github_username/API-Volontaria.git
```

To just use the API (to contribute on the frontend repository for example):
```
git clone https://github.com/Volontaria/API-Volontaria.git
```

You can now move in the newly created folder:

```
cd API-Volontaria
```

## Create a virtual environment

[Virtualenv](https://virtualenv.pypa.io/) provide isolated Python environments, which are more practical 
than installing packages systemwide. They also allow installing packages without administrator privileges.

1. Create a new virtual environment 
```
virtualenv env
```

2. Active the virtual environment

```
# For Linux
. env/bin/activate

# For Windows
env\Scripts\activate.bat
```

You need to ensure the virtual environment is active each time you want to launch the project.

## Install all requirements

All requirements used by this projects are documented inside the `requirements.txt` file at the root of the repository.
You can install all requirements needed by just one commandline.

**WARNING** : Make sure your virtual environment is active or you will install all these packages systemwide. 
```
pip install -r requirements.txt
```

## Configurations

You will need to define your environment variable, one of the easiest way is to copy-paste the `.env.example` at the root of the directory to create a `.env` file that will contain all your environment variables.

If you want to modify some settings you can just overwrite your `.env` file with the ENV variable that you want. Differents Django settings are based on ENV variables as you can see in `blitz_api/settings.py`

!!! danger
    Take care to not push your confidentials credentials when you push code to our repository or on your open-source forks. You can review your change by using git diff before committing your change. (ex: password, Secret API keys)

!!! danger
    Try to always use python-decouple to manage your settings and to not directly edit the `settings.py`.


## Configure the database

Django have a system of database migration, you need to apply all migrations of the project on your database to 
have the right data schema.

```
python manage.py migrate
```

!!! tip
    By default this repository work with a Sqlite3 database which is a technology using a simple file in place 
    of a database manager. You can change this config in your `.env` to use for example a custom instance of PostgreSQL. 
 
## Test the installation

At the beginning of this step you have a functional local setup. You can control it with the embedded web-server.

```
python manage.py runserver
```

You can now [visit the homepage](http://localhost:8000/) to validate the installation.

```
http://localhost:8000/
```

## Create an administrator

You will need an administrator to:

 - Access the django admin panel `http://localhost:8000/admin`
 - Access the admin panel of the frontend

To create an administrator, just use this command line and respond to some questions.

```
python manage.py createsuperuser
```

## Custom settings

If you need to have custom settings on your local environment, you can override global 
settings using `api_volontaria/local_settings.py`.
