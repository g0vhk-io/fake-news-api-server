python manage.py migrate
python manage.py collectstatic --noinput 
uwsgi --ini uwsgi.ini
