from Requests import Requests
from Scrapes import Scrapes

Requests.login("loredana.disalvio@basf.com", "gabriele")
x = Requests.getGradebookPage(2401224)
print(Scrapes.scrapeClassNames(x))
print(Scrapes.scrapeAverageGrades(x))
print(Scrapes.scrapeClassCodes(x))
y = Requests.getClassPages(Scrapes.scrapeClassCodes(x), 2401224)
for p in y:
  print(Scrapes.scrapeAssignmentGrades(p))
  print(Scrapes.scrapeAssignmentTypes(p))
  print(Scrapes.scrapeAssignmentNames(p))
  
