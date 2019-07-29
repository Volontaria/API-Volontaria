# Quickstart

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

## Create a virtual environment

[Virtualenv](https://virtualenv.pypa.io/) provide isolated Python environments, which are more practical than installing packages systemwide. They also allow installing packages without administrator privileges.

1. Create a new virtual environment 
```
virtualenv env
```

2. Active the virtual environment

```
. env/bin/activate
```

You need to ensure the virtual environment is active each time you want to launch the project.

## Install all requirements

All requirements used by this projects are documented inside the `requirements.txt` file at the root of the repository.
You can install all requirements needed by just one commandline.

**WARNING** : Make sure your virtual environment is active or you will install all these packages systemwide. 
```
pip install -r requirements.txt
```
 
## Configure the database

Django have a system of database migration, you need to apply all migrations of the project on your database to 
have the right data schema.

```
python source/apiVolontaria/manage.py migrate
```

> By default this repository work with a Sqlite3 database which is a technology using a simple file in place of a server. You can change this config in `source/apiVolontaria/apiVolontaria/local_settings.py`. 
 
## Test the installation

At the beginning of this step you have a functional local setup. You can control it with the embedded web-server.

```
python source/apiVolontaria/manage.py runserver
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
python source/apiVolontaria/manage.py createsuperuser
```

## Custom settings

If you need to have custom settings on your local environment, you can override global settings in `source/apiVolontaria/apiVolontaria/local_settings.py`.