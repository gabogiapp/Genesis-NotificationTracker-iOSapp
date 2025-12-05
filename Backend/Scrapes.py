from bs4 import BeautifulSoup
import re
from typing import List, Tuple


class Scrapes:
    """Collection of small HTML scraping helpers used to parse gradebook pages.

    Each method accepts an HTML string and returns Python structures (lists)
    with the scraped values. Methods perform small safety checks to avoid
    AttributeError when expected containers are missing.
    """

    @staticmethod
    def scrapeClassNames(response: str) -> List[str]:
        """Return the list of class names found in the gradebook page HTML."""
        soup = BeautifulSoup(response, "html.parser")
        spans = soup.find_all("span", class_="categorytab") or []
        return [span.get_text(strip=True) for span in spans]

    @staticmethod
    def scrapeAverageGrades(response: str) -> List[str]:
        """Return a list of average grade strings for each class.

        If a grade element is missing for a class the string "No Grades" is
        returned for that class to keep the output aligned with class names.
        """
        soup = BeautifulSoup(response, "html.parser")
        container = soup.find(class_="itemContainer")
        if not container:
            return []
        twocolflex_elements = container.find_all("div", class_="twoColFlex") or []
        average_grades: List[str] = []
        for twocolflex in twocolflex_elements:
            percentage_element = twocolflex.find("span", style="font-size:20pt")
            average_grades.append(percentage_element.get_text(strip=True) if percentage_element else "No Grades")
        return average_grades

    @staticmethod
    def scrapeClassCodes(response: str) -> List[str]:
        """Extract course code pairs from onclick handlers and return as "code,section" strings."""
        soup = BeautifulSoup(response, "html.parser")
        container = soup.find(class_="itemContainer")
        if not container:
            return []
        codes: List[str] = []
        pattern = re.compile(r"showAssignmentsByMPAndCourse\('(\w+)','(\w+)'\)")
        elements_with_pattern = container.find_all(lambda tag: tag.has_attr("onclick") and pattern.search(tag["onclick"]))
        for element in elements_with_pattern:
            onclick_text = element.get("onclick", "")
            match = pattern.search(onclick_text)
            if match:
                x_value, y_value = match.groups()
                codes.append(f"{x_value},{y_value}")
        return codes

    @staticmethod
    def scrapeAssignmentNames(response: str) -> List[str]:
        soup = BeautifulSoup(response, "html.parser")
        cell_centers = soup.find_all(class_="cellCenter", attrs={"style": "font-weight:bold;border: 1px solid black;"}) or []
        return [cell.get_text(strip=True) for cell in cell_centers]

    @staticmethod
    def scrapeAssignmentTypes(response: str) -> List[str]:
        soup = BeautifulSoup(response, "html.parser")
        types_elements = soup.find_all("div", style="font-size: 8pt;font-style: italic;") or []
        return [ele.get_text(strip=True) for ele in types_elements]

    @staticmethod
    def scrapeAssignmentGrades(response: str) -> List[str]:
        soup = BeautifulSoup(response, "html.parser")
        grade_elements = soup.find_all("div", style="font-weight: bold;") or []
        return [g.get_text(strip=True) for g in grade_elements]

    @staticmethod
    def cleanUp(averageGrades: List[str], classNames: List[str]) -> Tuple[List[str], List[str]]:
        """Remove classes that have no meaningful grade data.

        Returns a tuple (averageGrades_filtered, classNames_filtered) with
        entries removed where the average grade indicates no data.
        """
        if not averageGrades or not classNames:
            return [], []
        ignore_values = {"Not Graded MP4", "Not Graded MP3", "Not Graded MP2", "Not Graded MP1", "No Grades"}
        filtered_avgs: List[str] = []
        filtered_names: List[str] = []
        for avg, name in zip(averageGrades, classNames):
            if avg not in ignore_values:
                filtered_avgs.append(avg)
                filtered_names.append(name)
        return filtered_avgs, filtered_names