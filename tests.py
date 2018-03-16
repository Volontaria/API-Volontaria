import os

print ("Running -- Coverage --")
os.system("coverage run --omit=*.virtualenvs*,*virtualenv* source/apiVolontaria/manage.py test source/apiVolontaria/")

print ("Running -- Pycodestyle --")
os.system("pycodestyle --count --show-source --exclude=migrations source/apiVolontaria")

print ("Running -- Coverage Report --")
os.system("coverage report -m --skip-covered --include=./source/*")

print ("Running -- Django Tests --")
os.system("python source/apiVolontaria/manage.py test source/apiVolontaria/")
