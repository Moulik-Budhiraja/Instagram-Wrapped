from typing import *
from messages import *
from helpers import *
from collections import Counter
import os
from datetime import datetime, timedelta
import calendar
import csv
import re
from dataclasses import dataclass

YEAR = 2024

swearwords: list[str] = []

with open("assets/swearwords.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if "Mild" in row["Level of offensiveness"]:
            continue

        if "word" in row["Level of offensiveness"]:
            swearwords.append(row["Word"].lower())


@dataclass
class ComputedFeatures:
    TotalMessages: int
    TotalMessagesSent: int
    TotalMessagesReceived: int
    Top5Senders: list[tuple[User, int]]
    Top5Receivers: list[tuple[User, int]]
    MostActiveMonth: tuple[int, int]

    DownBadUser: tuple[User, int]
    KingOfSlurs: tuple[User, int]
    GhostVictim: tuple[User, int]

    BiggestSimp: tuple[User, int]
    MostFreaky: tuple[User, int]
    FakeFriend: tuple[User, int]
    BiggestHater: tuple[User, int]
    MostDesperate: tuple[User, int]


def computeFeatures(directMessages: list[Conversation]) -> ComputedFeatures:
    mainUser = predictUser(directMessages)

    basicFeatures = computeBasicFeatures(directMessages, mainUser)
    advancedFeatures = computeAdvancedFeatures(directMessages, mainUser)
    aiFeatures = computeAIFeatures(directMessages, mainUser)

    return ComputedFeatures(
        TotalMessages=basicFeatures.TotalMessages,
        TotalMessagesSent=basicFeatures.TotalMessagesSent,
        TotalMessagesReceived=basicFeatures.TotalMessagesReceived,
        Top5Senders=basicFeatures.Top5Senders,
        Top5Receivers=basicFeatures.Top5Receivers,
        MostActiveMonth=basicFeatures.MostActiveMonth,
        DownBadUser=advancedFeatures.DownBadUser,
        KingOfSlurs=advancedFeatures.KingOfSlurs,
        GhostVictim=advancedFeatures.GhostVictim,
        BiggestSimp=aiFeatures.BiggestSimp,
        MostFreaky=aiFeatures.MostFreaky,
        FakeFriend=aiFeatures.FakeFriend,
        BiggestHater=aiFeatures.BiggestHater,
        MostDesperate=aiFeatures.MostDesperate,
    )


def computeBasicFeatures(directMessages: list[Conversation], mainUser: User) -> ComputedFeatures:
    totalMessages = 0
    totalMessagesSent = 0
    totalMessagesReceived = 0
    sentToCounts = Counter()
    receivedFromCounts = Counter()

    monthCounts = Counter()

    for conv in directMessages:
        totalMessages += len(conv.messages)
        totalMessagesSent += len(conv.messagesFrom(mainUser).messages)
        totalMessagesReceived += len(conv.messages) - len(conv.messagesFrom(mainUser).messages)

        otherUser = User(conv.title)
        sentToCounts[otherUser] = len(conv.messagesFrom(mainUser).messages)
        receivedFromCounts[otherUser] = len(conv.messagesFrom(otherUser).messages)

    for conv in directMessages:
        for message in conv.messages:
            monthCounts[datetime.fromtimestamp(message.timestamp / 1000).month] += 1

    return ComputedFeatures(
        TotalMessages=totalMessages,
        TotalMessagesSent=totalMessagesSent,
        TotalMessagesReceived=totalMessagesReceived,
        Top5Senders=sentToCounts.most_common(5),
        Top5Receivers=receivedFromCounts.most_common(5),
        MostActiveMonth=monthCounts.most_common(1)[0],
        DownBadUser=None,
        KingOfSlurs=None,
        GhostVictim=None,
        BiggestSimp=None,
        MostFreaky=None,
        FakeFriend=None,
        BiggestHater=None,
        MostDesperate=None,
    )


def computeAdvancedFeatures(directMessages: list[Conversation], mainUser: User) -> ComputedFeatures:
    # Find the most down bad user
    downBadMessages = Counter()

    for conv in directMessages:
        for day in range(366 if calendar.isleap(YEAR) else 365):
            # 1-4 each day
            startTimestamp = (datetime(YEAR, 1, 1) + timedelta(day)).timestamp()
            endTimeStamp = (datetime(YEAR, 1, 1, 4) + timedelta(day)).timestamp()

            otherUser = User(conv.title)

            downBadMessages[otherUser] += len(conv.messagesFrom(mainUser).messagesBetweenTime(startTimestamp * 1000, endTimeStamp * 1000).messages)

    # Find the slur king
    kingOfSlurs = Counter()

    for conv in directMessages:
        otherUser = User(conv.title)
        for message in conv.messagesFrom(otherUser).messages:
            if message.messageType != MessageType.TEXT:
                continue

            messageLower = message.content.lower()

            for word in swearwords:
                if re.search(rf"\b{word}\b", messageLower):
                    kingOfSlurs[otherUser] += 1

    # Find the ghost victim
    ghostVictim = Counter()

    for conv in directMessages:
        otherUser = User(conv.title)
        for i, lastMessage in enumerate(conv.messages):
            if i + 1 == len(conv.messages):
                break

            currMessage = conv.messages[i + 1]

            if (
                currMessage.sender == mainUser
                and lastMessage.sender == otherUser
                and (currMessage.timestamp - lastMessage.timestamp) / 1000 > 60 * 60 * 24
            ):
                ghostVictim[otherUser] += 1

    return ComputedFeatures(
        TotalMessages=None,
        TotalMessagesSent=None,
        TotalMessagesReceived=None,
        Top5Senders=None,
        Top5Receivers=None,
        MostActiveMonth=None,
        DownBadUser=downBadMessages.most_common(1)[0],
        KingOfSlurs=kingOfSlurs.most_common(1)[0],
        GhostVictim=ghostVictim.most_common(1)[0],
        BiggestSimp=None,
        MostFreaky=None,
        FakeFriend=None,
        BiggestHater=None,
        MostDesperate=None,
    )


def computeAIFeatures(directMessages: list[Conversation], mainUser: User) -> ComputedFeatures:
    return ComputedFeatures(
        TotalMessages=None,
        TotalMessagesSent=None,
        TotalMessagesReceived=None,
        Top5Senders=None,
        Top5Receivers=None,
        MostActiveMonth=None,
        DownBadUser=None,
        KingOfSlurs=None,
        GhostVictim=None,
        BiggestSimp=None,
        MostFreaky=None,
        FakeFriend=None,
        BiggestHater=None,
        MostDesperate=None,
    )
