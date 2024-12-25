from typing import *
from messages import *
import os

for user in os.listdir(FILE_PATH):
    conversation = Conversation(os.path.join(FILE_PATH, user))

    print(os.path.join(FILE_PATH, user))
    print(len(conversation.messages))

    for message in conversation.messages:
        print(message)

    break


# Total messages sent: (full number)

# Most Messages Sent
# 1 (Dm only)
# 2
# 3
# 4
# 5
#
#
#
#
