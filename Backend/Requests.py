from Scrapes import Scrapes
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple


class Requests:
  """Small wrapper around requests.Session used to interact with the
  Genesis gradebook endpoints.

  The class keeps a single `Session` and cookie jar at class-level so the
  rest of the code can call login/getGradebookPage/getClassPages without
  passing a session object around.
  """

  session = requests.Session()
  cookies = {}

  @staticmethod
  def login(username: str, password: str) -> str:
    """Authenticate and return the response body from the login POST.

    Side effects:
      - stores session cookies in `Requests.cookies` for later requests.
    """
    headers = {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "max-age=0",
      "Connection": "keep-alive",
      "Content-Type": "application/x-www-form-urlencoded",
      "Origin": "https://parents.westfieldnjk12.org",
      "Referer": "https://parents.westfieldnjk12.org/genesis/sis/view?gohome=true",
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "same-origin",
      "Sec-Fetch-User": "?1",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    data = {"idTokenString": "", "j_username": username, "j_password": password}

    response = Requests.session.post(
      "https://parents.westfieldnjk12.org/genesis/sis/j_security_check",
      headers=headers,
      data=data,
    )

    Requests.cookies = Requests.session.cookies.get_dict()
    return response.text

  @staticmethod
  def getGradebookPage(student_id: str) -> str:
    """Fetch the gradebook 'weekly summary' page for `student_id` and return HTML text."""
    headers = {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "max-age=0",
      "Connection": "keep-alive",
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "none",
      "Sec-Fetch-User": "?1",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    params = {"tab1": "studentdata", "tab2": "gradebook", "tab3": "weeklysummary", "action": "form", "studentid": student_id}

    response = Requests.session.post(
      "https://parents.westfieldnjk12.org/genesis/parents", params=params, cookies=Requests.cookies, headers=headers
    )
    return response.text

  @staticmethod
  def getClassPages(codes: List[str], student_id: str) -> List[str]:
    """Fetch and return the list of HTML pages for each class code.

    The `codes` argument is expected as a list of strings of the form
    "courseCode,courseSection" (matching the output of
    `Scrapes.scrapeClassCodes`).
    """
    results: List[str] = []

    headers = {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "max-age=0",
      "Connection": "keep-alive",
      "Referer": f"https://parents.westfieldnjk12.org/genesis/parents?tab1=studentdata&tab2=gradebook&action=form&studentid={student_id}",
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "same-origin",
      "Sec-Fetch-User": "?1",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    for idx, code in enumerate(codes):
      if "," not in code:
        # skip malformed codes but preserve ordering
        results.append("")
        continue
      code1, code2 = code.split(",", 1)
      classes_url = (
        f"https://parents.westfieldnjk12.org/genesis/parents?tab1=studentdata&tab2=gradebook&tab3=coursesummary&studentid={student_id}&action=form&courseCode={code1}&courseSection={code2}"
      )
      response = Requests.session.get(classes_url, cookies=Requests.cookies, headers=headers)
      results.append(response.text)

    return results

  @staticmethod
  def checkUpdates(oldAssignmentGradesLens: List[List[int]]) -> Optional[Tuple[List[int], int]]:
    """Example helper that checks for assignment length changes and returns (newLens, index) when a class grows.

    This method appears to be sample/demo code in the repo. It logs in with a hard-coded account and compares lengths.
    Returns a tuple (newLengths, index_of_changed_class) when a change is detected, otherwise None.
    """
    Requests.login("loredana.disalvio@basf.com", "gabriele")

    gradebookPage = Requests.getGradebookPage("2401224")
    classPages = Requests.getClassPages(Scrapes.scrapeClassCodes(gradebookPage), "2401224")

    newAssignmentGradesLens: List[int] = [len(Scrapes.scrapeAssignmentGrades(p)) for p in classPages]
    for i, length in enumerate(newAssignmentGradesLens):
      # Guard against index errors if old list shape differs
      try:
        if length > oldAssignmentGradesLens[i]:
          return newAssignmentGradesLens, i
      except Exception:
        # If oldAssignmentGradesLens doesn't contain expected structure, skip
        continue
    return None