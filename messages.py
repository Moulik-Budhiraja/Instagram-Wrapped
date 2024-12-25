import json
import os
import datetime
from typing import *
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

FILE_PATH = os.getenv("FILE_PATH")


class MessageType(Enum):
    UNKNOWN = 0
    TEXT = 1
    MEDIA = 2


class ReactionDict(TypedDict):
    reaction: str
    actor: str


class MediaDict(TypedDict):
    uri: str


class MessageDict(TypedDict):
    sender_name: str
    timestamp_ms: int
    reactions: list[ReactionDict]


class TextMessageDict(TypedDict, MessageDict):
    content: str


class MediaMessageDict(TypedDict, MessageDict):
    photos: Optional[list[MediaDict]]
    videos: Optional[list[MediaDict]]


class User:
    def __init__(self, username: str):
        self.username = username

    def __eq__(self, other: "User") -> bool:
        return self.username == other.username

    def __str__(self):
        return f'User("{self.username}")'

    def __repr__(self):
        return f'User("{self.username}")'

    def __hash__(self):
        return hash(self.username)


class Reaction:
    def __init__(self, reaction: str, actor: User):
        self.reaction = reaction
        self.actor = actor


class Message:
    def __init__(self, sender: User, timestamp: int, reactions: list[Reaction] | None = None):
        self.messageType: MessageType = MessageType.UNKNOWN
        self.sender = sender
        self.timestamp = timestamp
        self.reactions = reactions if reactions else []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\n\tsender: {self.sender}, \n\ttimestamp: {self.timestamp})\n"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(sender: {self.sender})\n"

    @staticmethod
    def parseMessage(messageDict: TextMessageDict | MediaMessageDict, participants: dict[str, User]) -> "TextMessage | MediaMessage":
        # If sender doesn't exist, then add it, participantsArray is a reference
        if not messageDict["sender_name"] in participants:
            participants[messageDict["sender_name"]] = User(messageDict["sender_name"])

        sender = participants[messageDict["sender_name"]]
        timestamp = messageDict["timestamp_ms"]

        reactions = []
        for reaction_dict in messageDict.get("reactions", []):
            # If actor not in participants, do the same
            if not reaction_dict["actor"] in participants:
                participants[reaction_dict["actor"]] = User(reaction_dict["actor"])

            actor = participants[reaction_dict["actor"]]
            reaction = Reaction(reaction_dict["reaction"], actor)
            reactions.append(reaction)

        if messageDict.get("content") != None:
            # Text Message
            content = messageDict["content"]
            message = TextMessage(sender, timestamp, reactions, content)
            return message
        else:
            # Media Message
            imageLinks = []
            videoLinks = []

            for imageDict in messageDict.get("photos", []):
                imageLinks.append(imageDict["uri"])

            for videoDict in messageDict.get("videos", []):
                imageLinks.append(videoDict["uri"])

            message = MediaMessage(sender, timestamp, reactions, imageLinks, videoLinks)
            return message


class TextMessage(Message):
    def __init__(self, sender: User, timestamp: int, reactions: list[Reaction] | None = None, content: str = ""):
        super().__init__(sender, timestamp, reactions)

        self.messageType = MessageType.TEXT
        self.content = content

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\n\tsender: {self.sender}, \n\ttimestamp: {self.timestamp}, \n\tcontent: {self.content}\n)\n"


class MediaMessage(Message):
    def __init__(
        self,
        sender: User,
        timestamp: int,
        reactions: list[Reaction] | None = None,
        imageLinks: list[str] | None = None,
        videoLinks: list[str] | None = None,
    ):
        super().__init__(sender, timestamp, reactions)

        self.messageType = MessageType.MEDIA
        self.imageLinks = imageLinks if imageLinks else []
        self.videoLinks = videoLinks if videoLinks else []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\n\tsender: {self.sender}, \n\ttimestamp: {self.timestamp}, \n\tobjects: {len(self.imageLinks) + len(self.videoLinks)}\n)\n"


class Conversation:
    def __init__(self, conversationPath: str | None):
        title = None
        participants = None
        messages = None

        if conversationPath != None:
            title, participants, messages = Conversation.load_messages(conversationPath)

        self.title = title
        self.participants: dict[str, User] = participants
        self.messages: list[TextMessage | MediaMessage] = messages

    def copy(self) -> Self:
        newConv = Conversation(None)

        newConv.title = self.title
        newConv.participants = self.participants
        newConv.messages = self.messages

        return newConv

    def messagesBetweenTime(self, startTimestampMs: int, endTimestampMs: int) -> Self:
        newConv = self.copy()
        newConv.messages = [message for message in self.messages if startTimestampMs <= message.timestamp <= endTimestampMs]
        return newConv

    def messagesFrom(self, user: User) -> Self:
        newConv = self.copy()
        newConv.messages = [message for message in self.messages if message.sender == user]
        return newConv

    def excludeParticipant(self, user: User) -> Self:
        newConv = self.copy()
        newConv.participants = {n: u for n, u in self.participants.items() if u != user}
        newConv.messages = [message for message in self.messages if message.sender != user]
        return newConv

    @staticmethod
    def load_messages(conversationPath: str) -> tuple[str, list[User], list[TextMessage | MediaMessage]]:
        filePaths = []

        for file in os.listdir(conversationPath):
            if not file.endswith(".json"):
                continue

            filePaths.append(os.path.join(conversationPath, file))

        messages: list[TextMessage | MediaMessage] = []
        participants: dict[str, User] = {}
        title = ""

        for path in filePaths:
            with open(path, "r") as f:
                file = json.load(f)

                # Setup participants and title
                if len(participants) == 0:
                    title = file["title"]

                    for userDict in file["participants"]:
                        participants[userDict["name"]] = User(userDict["name"])

                # Add Messages
                messageDict: TextMessageDict | MediaMessageDict
                for messageDict in file["messages"]:
                    try:
                        messages.append(Message.parseMessage(messageDict, participants))
                    except Exception as e:
                        print(messageDict, participants, sep="\n")
                        raise e

        messages.sort(key=lambda x: x.timestamp)

        return title, participants, messages
