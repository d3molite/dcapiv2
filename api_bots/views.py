from django.shortcuts import render
from django.http import HttpResponse
import subprocess, sys, time, os

# Create your views here.


def restart(request):
    restartSystem()
    return HttpResponse("Restarting System")


def restartSystem():
    path = os.path.join(os.path.dirname("restart.py"))
    subprocess.Popen(path, shell=True)
    time.sleep(5)
    raise SystemExit
