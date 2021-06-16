import subprocess

print("STARTING SERVER")
cmd = "python manage.py runserver"

shell = subprocess.Popen(cmd, shell=True)