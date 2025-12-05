import requests
from typing import List


class DummyRequests:
    """A small stubbed requests client used for local testing.

    This mirrors the structure of `Requests` but points to local/demo pages
    hosted on `genesis-login.gabrielelisci.repl.co`.
    """

    session = requests.Session()
    headers = {
        "authority": "genesis-login.gabrielelisci.repl.co",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://genesis-login.gabrielelisci.repl.co",
        "referer": "https://genesis-login.gabrielelisci.repl.co/",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    cookies = ""

    @staticmethod
    def login(username: str = "", password: str = "") -> str:
        data = {"idTokenString": "", "j_username": username, "j_password": password}
        response = DummyRequests.session.post(
            "https://genesis-login.gabrielelisci.repl.co/HomePage.html", headers=DummyRequests.headers, data=data
        )
        DummyRequests.cookies = DummyRequests.session.cookies.get_dict()
        return response.text

    @staticmethod
    def getGradebookPage(student_id: int = 0) -> str:
        response = DummyRequests.session.post("https://genesis-login.gabrielelisci.repl.co/gradebook.html", headers=DummyRequests.headers)
        return response.text

    @staticmethod
    def getClassPages() -> List[str]:
        results: List[str] = []
        for path in ("Health.html", "Amstud.html", "French.html", "Math.html", "Physics.html", "CompSci.html"):
            response = DummyRequests.session.get(f"https://genesis-login.gabrielelisci.repl.co/{path}", cookies=DummyRequests.cookies, headers=DummyRequests.headers)
            results.append(response.text)
        return results