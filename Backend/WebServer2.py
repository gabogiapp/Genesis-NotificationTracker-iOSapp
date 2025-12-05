from flask import Flask, request
#from flask_cors import CORS
from DummyRequests import DummyRequests
from Requests import Requests
from Scrapes import Scrapes
from Firebase import Firebase
from Crypto import Crypto
import time
import os
from threading import Thread, Lock
import logging

# Configure the logging module
logging.basicConfig(
  level=logging.INFO,  # Set the desired logging level
  filename='app.log',  # Specify the log file name
  filemode='a',  # Set the file mode to append
  format='%(asctime)s - %(levelname)s - %(message)s'  # Specify the log format
)

app = Flask("")
#CORS(app)

listOfOldAssignmentGradeLens = []
usernames = []
passwords = []
studentIDs = []
tokens = []
checks = Firebase.getChecks()
update_thread = None  # Thread for running the update_grades function
lock = Lock()  # Lock for synchronization


def process_token(index, token):
  # Process a token at a specific index
  # Each thread operates independently

  try:
    # Obtain necessary information for the token at the index
    if index >= len(tokens) or not token or not checks[index]:
      return
    username = usernames[index]
    password = passwords[index]
    student_id = studentIDs[index]

    if Crypto.decrypt_fcm_token(username, os.environ["KEY"]) == "developertest@test.com" and Crypto.decrypt_fcm_token(password, os.environ["KEY"]) == "test123" and student_id == "1":
      logging.info("TEST NOTIF")
      Firebase.sendNotif(Crypto.decrypt_fcm_token(token, os.environ['KEY']), "Test Notification", "This is to test if notifications work")
      return
      
    # Perform necessary operations using the token
    DummyRequests.login()
    gradebookPage = DummyRequests.getGradebookPage()
    classPages = DummyRequests.getClassPages()

    # Requests.login(Crypto.decrypt_fcm_token(username, os.environ["KEY"]), Crypto.decrypt_fcm_token(password, os.environ["KEY"]))
    # gradebookPage = Requests.getGradebookPage(student_id)
    # classPages = Requests.getClassPages(Scrapes.scrapeClassCodes(gradebookPage), student_id)

    
    logging.info("Requests Complete")

    assignmentGrades = []
    assignmentNames = []
    assignmentTypes = []

    
    for j in range(len(classPages)):
      assignmentGrades.append(Scrapes.scrapeAssignmentGrades(classPages[j]))
      if len(assignmentGrades[j]) > listOfOldAssignmentGradeLens[index][j]:
        assignmentNames = Scrapes.scrapeAssignmentNames(classPages[j])
        assignmentTypes = Scrapes.scrapeAssignmentTypes(classPages[j])
        averageGrades = Scrapes.scrapeAverageGrades(gradebookPage)
        classNames = Scrapes.scrapeClassNames(gradebookPage)
        averageGrades, classNames = Scrapes.cleanUp(averageGrades, classNames)

        body = (assignmentGrades[j][0] + " on " + assignmentNames[0] + " in " +
                classNames[j] + "\n" + "New Average Grade: " +
                averageGrades[j])
        logging.info(body)
        try:
          Firebase.sendNotif(Crypto.decrypt_fcm_token(token, os.environ['KEY']), "New Grade", body)
        except Exception as e:
          logging.exception("Error in sending Notification: %s", str(e))
        listOfOldAssignmentGradeLens[index][j] = len(assignmentGrades[j])
    logging.info("Checking for Updates Complete")

  except Exception as e:
    # Log the error
    logging.exception("Error in process_token(): %s", str(e))


def update_grades():
  global listOfOldAssignmentGradeLens, usernames, passwords, studentIDs, tokens, checks

  while True:
    try:
      logging.info("Starting Check")
      logging.info(checks)
      # Process tokens in parallel
      for i in range(len(tokens)):
        thread = Thread(target=process_token, args=(i, tokens[i]))
        thread.start()

      # Wait for all threads to complete
      time.sleep(5)
    except Exception as e:
      # Log the error
      logging.exception("Error in update_grades(): %s", str(e))


@app.route("/")
def home():
  logging.info("Home method called")
  return "Web server is running!"


@app.route("/ping")
def ping():
  logging.info("Ping method called")
  return "Pinging the server to keep it alive."

@app.route("/stop")
def stop():
  return

@app.route("/button")
def button():
  global checks, update_thread
  logging.info("Button method called")
  checks = Firebase.getChecks()
  # Start the update_grades function in a separate thread if it's not already running
  if update_thread is None or not update_thread.is_alive():
    update_thread = Thread(target=update_grades)
    update_thread.start()
  logging.info("Received Data 2")
  return "User information updated 2."


@app.route("/new_user")
def new_user():
  global listOfOldAssignmentGradeLens, usernames, passwords, studentIDs, tokens, checks, update_thread

  try:
    # Update the user information or perform any necessary initialization
    listOfOldAssignmentGradeLens = Firebase.getOldAssignmentGradeLengths()
    usernames = Firebase.getEmails()
    passwords = Firebase.getPasswords()
    studentIDs = Firebase.getStudentIDs()
    tokens = Firebase.getTokens()

    # Start the update_grades function in a separate thread if it's not already running
    if update_thread is None or not update_thread.is_alive():
      update_thread = Thread(target=update_grades)
      update_thread.start()
    logging.info("Received Data")
    return "User information updated."
  except Exception as e:
    # Log the error
    logging.exception("Error in new_user(): %s", str(e))
    return "Error occurred while updating user information."


# WSGI application entry point
application = app.wsgi_app


def run():
  app.run(host="0.0.0.0", port=1111)


def keep_alive():
  t = Thread(target=run)
  t.start()
