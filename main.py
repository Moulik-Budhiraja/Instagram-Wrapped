from typing import *
from messages import *
import os
from features import *

conversations: list[Conversation] = []

for user in os.listdir(FILE_PATH):
    conversation = Conversation(os.path.join(FILE_PATH, user))
    conversations.append(conversation)


directMessages = [
    conversation for conversation in conversations if len(conversation.participants) == 2 and conversation.title in conversation.participants
]


allFeatures = computeFeatures(directMessages)

print("********** Instagram DM Wrapped **********")
print("Total Messages:", allFeatures.TotalMessages)
print("Total Messages Sent:", allFeatures.TotalMessagesSent)
print("Total Messages Received:", allFeatures.TotalMessagesReceived)
print()
print("Top 5 Senders:")
for sender, count in allFeatures.Top5Senders:
    print(f"\t{sender}: {count}")
print()

print("Top 5 Receivers:")
for receiver, count in allFeatures.Top5Receivers:
    print(f"\t{receiver}: {count}")
print()

print("Most Active Month:", allFeatures.MostActiveMonth)
print()

print("Down Bad User:", allFeatures.DownBadUser)  # Sent this many messages to the user from 12am to 4am
print("King Of Slurs:", allFeatures.KingOfSlurs)  # User sent you this many slurs
print("Ghost Victim:", allFeatures.GhostVictim)  # You left this user on read this many times

# print("Biggest Simp:", allFeatures.BiggestSimp)
# print("Most Freaky:", allFeatures.MostFreaky)
# print("Fake Friend:", allFeatures.FakeFriend)
# print("Biggest Hater:", allFeatures.BiggestHater)
# print("Most Desperate:", allFeatures.MostDesperate)
