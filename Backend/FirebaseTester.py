from Firebase import Firebase
from Crypto import Crypto
import os

emails = Firebase.getEmails()
print("emails:" + str(emails))
for email in emails:
   print(str(email) + " : " + str(Crypto.decrypt_fcm_token("email",  "7dg35shfbckwytwhamo1w35dbdg472hn")))