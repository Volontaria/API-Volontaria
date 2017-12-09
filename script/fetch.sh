INITIAL_PATH=`pwd`

ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
SCRIPT_PATH=`dirname $ABSOLUTE_PATH`
REPOSITORY_PATH=`dirname $SCRIPT_PATH`

cd $REPOSITORY_PATH

# Init virtualenv
deactivate
rm -rf env
virtualenv env
. env/bin/activate

# Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Refresh dabatabe
python source/apiVolontaria/manage.py migrate

# Move user to initial folder
cd $INITIAL_PATH