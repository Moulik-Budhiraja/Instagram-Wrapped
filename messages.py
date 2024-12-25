import json
import os
import datetime
from typing import *
from dotenv import load_dotenv

load_dotenv()

FILE_PATH = os.getenv("FILE_PATH")


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


class Reaction:
    def __init__(self, reaction: str, actor: User):
        self.reaction = reaction
        self.actor = actor


class Message:
    def __init__(self, sender: User, timestamp: int, reactions: list[Reaction] | None = None):
        self.sender = sender
        self.timestamp = timestamp
        self.reactions = reactions if reactions else []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(sender: {self.sender}, \ntimestamp: {self.timestamp})\n"

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

        self.imageLinks = imageLinks if imageLinks else []
        self.videoLinks = videoLinks if videoLinks else []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\n\tsender: {self.sender}, \n\ttimestamp: {self.timestamp}, \n\tobjects: {len(self.imageLinks) + len(self.videoLinks)}\n)\n"


class Conversation:
    def __init__(self, conversationPath: str):
        participants, messages = Conversation.load_messages(conversationPath)

        self.participants: list[User] = participants
        self.messages: list[TextMessage | MediaMessage] = messages

    @staticmethod
    def load_messages(conversationPath: str) -> tuple[list[User], list[TextMessage | MediaMessage]]:
        filePaths = []

        for file in os.listdir(conversationPath):
            if not file.endswith(".json"):
                continue

            filePaths.append(os.path.join(conversationPath, file))

        messages: list[TextMessage | MediaMessage] = []
        participants: dict[str, User] = {}

        for path in filePaths:
            with open(path, "r") as f:
                file = json.load(f)

                # Setup participants
                if len(participants) == 0:
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

        return participants, messages
