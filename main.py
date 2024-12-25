from typing import *
from messages import *
import os

conversations: list[Conversation] = []

for user in os.listdir(FILE_PATH):
    conversation = Conversation(os.path.join(FILE_PATH, user))

    conversations.append(conversation)
