from DummyRequests import DummyRequests
from Requests import Requests
from Scrapes import Scrapes
from Firebase import Firebase
from Crypto import Crypto
import time
import os


def _safe_list_get(lst, idx, default=None):
  try:
    return lst[idx]
  except Exception:
    return default


"""Simple server loop that polls student grade pages and sends notifications.

This module is the existing prototype loop used by the project. Changes made
here are intentionally minimal: we rename Firebase helper calls to the new
snake_case names and add a few guards to avoid IndexError when Firestore
documents have unexpected shapes.
"""


students = Firebase.get_students()
listOfOldAssignmentGradeLens = [s.grades_length or [] for s in students]


while True:
  print("Starting Loop")
  print("Retrieved Data")

  # Iterate over students and check for updates
  for i, student in enumerate(students):
    username = student.email or ""
    encrypted_password = student.password or ""
    student_id = student.student_id or ""
    token = student.fcm_token

    if not token:
      # Skip entries without an FCM token
      continue

    # Decrypt password and login
    try:
      decrypted_password = Crypto.decrypt_string(encrypted_password, os.environ.get("KEY", ""))
    except Exception:
      decrypted_password = ""

    # Try to decrypt token if it appears to be hex data, fall back to raw
    try:
      try:
        token = Crypto.decrypt_fcm_token(token, os.environ.get("KEY", ""))
      except Exception:
        # If that fails, assume token is already plaintext
        pass
    except Exception:
      pass

    Requests.login(username, decrypted_password)
    gradebookPage = Requests.getGradebookPage(student_id)
    classPages = Requests.getClassPages(Scrapes.scrapeClassCodes(gradebookPage), student_id)
    print("Requests Complete")

    # Gather assignments per class and compare lengths
    for j, page in enumerate(classPages):
      grades = Scrapes.scrapeAssignmentGrades(page)

      old_lengths_for_student = _safe_list_get(listOfOldAssignmentGradeLens, i, []) or []
      old_len = _safe_list_get(old_lengths_for_student, j, 0)

      if len(grades) > old_len:
        assignmentNames = Scrapes.scrapeAssignmentNames(page)
        assignmentTypes = Scrapes.scrapeAssignmentTypes(page)
        averageGrades = Scrapes.scrapeAverageGrades(gradebookPage)
        classNames = Scrapes.scrapeClassNames(gradebookPage)
        averageGrades, classNames = Scrapes.cleanUp(averageGrades, classNames)

        # Build a short notification body; guard against missing fields
        first_grade = _safe_list_get(grades, 0, "")
        first_name = _safe_list_get(assignmentNames, 0, "")
        class_name = _safe_list_get(classNames, j, "")
        avg_grade = _safe_list_get(averageGrades, j, "")

        body = f"{first_grade} on {first_name} in {class_name}\nNew Average Grade: {avg_grade}"
        print(body)
        Firebase.send_notif(token, "New Grade", body)

        # Update the cached length in both the local list and student object
        try:
          listOfOldAssignmentGradeLens[i][j] = len(grades)
        except Exception:
          if i >= len(listOfOldAssignmentGradeLens):
            while len(listOfOldAssignmentGradeLens) <= i:
              listOfOldAssignmentGradeLens.append([])
          inner = listOfOldAssignmentGradeLens[i]
          while len(inner) <= j:
            inner.append(0)
          listOfOldAssignmentGradeLens[i][j] = len(grades)

        # Keep the in-memory student record up to date
        try:
          if not student.grades_length:
            student.grades_length = []
          while len(student.grades_length) <= j:
            student.grades_length.append(0)
          student.grades_length[j] = len(grades)
        except Exception:
          pass

    print("Checking for Updates Complete")
    time.sleep(5)
        


  