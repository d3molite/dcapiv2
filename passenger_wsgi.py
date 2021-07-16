import sys, os

app_name = 'app'
env_name = 'django-app-venv'

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/' + app_name)

INTERP = cwd + '/' + env_name + '/bin/python'
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, cwd + '/' + env_name + '/bin')
sys.path.insert(0, cwd + '/' + env_name + '/lib/python3.8.5/site-packages/django')
sys.path.insert(0, cwd + '/' + env_name + '/lib/python3.8.5/site-packages')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", app_name + ".settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()