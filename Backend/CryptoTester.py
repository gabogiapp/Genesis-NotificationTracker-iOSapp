from Crypto import Crypto
import os

x = Crypto.encrypt_string("gabriele", os.environ["KEY"])
print(x)
y = Crypto.decrypt_string(x, os.environ["KEY"])
print(y)

#fVH_AdW3ZEk1h1a72qVbdw:APA91bHaXVktNUwuUhWPorujcg6fJxUtUmX3KmVPGKigdhH2hiDOcy8kzN-3jffpsTf6tFnI9W7jNnCNPJA_vtIEtp__8JamjBNI5YMCuh6pf5qA7rLD1HfY-oooH-vFuvFLDVhtwpbK

y = Crypto.decrypt_fcm_token("QArnvBhc9cqoQgRGaq6ojV6m9lZU1TJRqjuk4pePiQXFgcnOx/RH9Nn0Dv7QCUXTJoqwk68Zf95l1cqp70+7wJQBmmp32Rz1mM0ipQnsh2L5sIvi//Nulis6pSnmqzE3pdcsDK6mrf7Cvyx2yTCf4845ItR3U3ZkzGXBfssbS9/fxg9j+KS1feNypx2MFGCYKrlSH+598EXoWn8kUMfNSUzR06TMy/LFetTx+++0Fu69dMptvz54E49ySrhuaD4=", os.environ["KEY"])

print(y)
print(Crypto.decrypt_fcm_token("Hnz/zE+RZe7DA2RNX/sJe+UNGnuUBotwMOA3fIPl3rpVl2p3oEJnxjPtcu6OJ1iKdOs=", os.environ["KEY"]))
print(Crypto.decrypt_fcm_token("5gKCYqhQw5jfpRbin4kz71luYNu0EgkB649qO74G+Ezl7LA=", os.environ["KEY"]))