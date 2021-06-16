import subprocess, time

print("Waiting for bots and connected applications to shut down.")
time.sleep(5)

shell = subprocess.Popen("python run.py", shell=True)