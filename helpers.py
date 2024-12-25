from typing import *
from messages import *
from collections import Counter


def predictUser(directMessages: list[Conversation]) -> User:
    """Attempts to determine who the 'main' user is"""
    possibleUsers: list[User] = []

    for conv in directMessages:
        for name, user in conv.participants.items():
            if name != conv.title:
                possibleUsers.append(user)

    return max(Counter(possibleUsers))
