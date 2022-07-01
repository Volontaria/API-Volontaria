# Getting started with Docker

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

## Initialize the project

One command only will allow you to initialize the database, run the migration on it, configure you API, 
launch your documentation website and allow you to begin use the project:

```bash
docker-compose up
```

!!! warning
    This step can take some time on first launch but you should see periodic message to inform you that the work 
    is in progress. Breathe in, breathe out, have a coffee and come back in 2-3 minutes

## Create super admin

Since you don't have user the first time you launch the API you will need to execute this command in a separate 
terminal.

```bash
docker-compose run api python source/apiVolontaria/manage.py createsuperuser
```

!!! tip
    If you try to understand this command you can see that we ask docker-compose to `run` a command on the `api` image
    that represent our API in the `docker-compose.yml`. The command 
    is `python source/apiVolontaria/manage.py createsuperuser`, the default Django command to create a new 
    superuser. With this technique you can execute other Django commands 
    like `migrate`, `makemigrations`, `makemessages` or even custom command you create to automatise your tasks.

## Configurations

If you want to modify some settings of your Docker image you can just overwrite your `.env` file with the 
ENV variable that you want. Differents Django settings are based on ENV variables as you can see 
in `source/apiVolontaria/apiVolontaria/settings.py`

!!! danger
    Take care to not push your confidentials credentials when you push code to our repository or on your open-source 
    forks. You can review your change by using `git diff` before committing your change.
    
!!! danger
    Try to always use `python-decouple` to manage your settings and to not directly edit the `settings.py`. 

## Using the services

You can now visit these links to validate the installation:

- The root of the API (will need authentication as a first step): [http://localhost:8000/](http://localhost:8000/)
- The admin site: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- The documentation you're reading: [http://localhost:8001/](http://localhost:8001/)

Do not hesitate to check the API section of this documentation to know how to authenticate yourself with the API 
and begin asking queries. 