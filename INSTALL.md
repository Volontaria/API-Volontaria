# How to setup the project locally

## Create a virtual environment

Take a look at [virtualenv](https://virtualenv.pypa.io/). This tool provide isolated Python environments, which are more practical than installing packages systemwide. They also allow installing packages without administrator privileges.

```
virtualenv env
. env/bin/activate
```

## Install all requirements

All requirements used by this projects are documented inside the `requirements.txt` file at the root of this repository. You can install all requirements needed by one commandline.

```commandline
pip install -r requirements.txt
```
 
## Apply migrations on your database

Django have a system of database migration, you need to migrate your

```commandline
python source/apiVolontaria/manage.py migrate
```

> By default this repository work with a Sqlite3 database which is a technology using a simple file in place of a server. You can change this config in the `source/apiVolontaria/apiVolontaria/settings.py` file. 
 
## Test the local setup

At the beginning of this step you have a fonctionnal local setup. You can control it with the embedded webserver.

```commandline
python source/apiVolontaria/manage.py runserver
```
 