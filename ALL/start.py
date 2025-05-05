import subprocess
import time


login_server = subprocess.Popen(["python", "flasklogin.py"], cwd="C:/Users/User/OneDrive/Desktop/python/MMU-TutorFinder/ALL")
print("flasklogin.py started successfully")


time.sleep(1)


chat_server = subprocess.Popen(["python", "chat.py"], cwd="C:/Users/User/OneDrive/Desktop/python/MMU-TutorFinder/ALL")
print("chat.py started successfully")

time.sleep(1)

chat_server = subprocess.Popen(["python", "testingweb.py"], cwd="C:/Users/User/OneDrive/Desktop/python/MMU-TutorFinder/ALL")
print("testingweb.py started successfully")



try:
    login_server.wait()
    chat_server.wait()
except KeyboardInterrupt:
    print("\nShutting down servers...")
    login_server.terminate()
    chat_server.terminate()
    print("Servers closed")
