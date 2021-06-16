import subprocess

print("STARTING SERVER")
cmd = "python manage.py runserver --noreload"

shell = subprocess.Popen(cmd, shell=True)