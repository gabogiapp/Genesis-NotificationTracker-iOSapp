from DummyRequests import DummyRequests
from Scrapes import Scrapes

DummyRequests.login()
gradebookPage = DummyRequests.getGradebookPage()
classPages = DummyRequests.getClassPages()

# print(Scrapes.scrapeAverageGrades(gradebookPage))
# print(Scrapes.scrapeClassNames(gradebookPage))

# print(Scrapes.scrapeAssignmentGrades(classPages[5]))
# print(Scrapes.scrapeAssignmentNames(classPages[5]))
# print(Scrapes.scrapeAssignmentTypes(classPages[5]))

lens = []
for x in range(len(classPages)):
    lens.append(len(Scrapes.scrapeAssignmentGrades(classPages[x])))
print(lens)