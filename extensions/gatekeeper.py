import os
from core.base import CustomClient

from dotenv import load_dotenv
from pymongo import MongoClient
from naff import listen, Extension, Task, IntervalTrigger
from naff.api.events.discord import MemberAdd

load_dotenv()

cluster = MongoClient(os.getenv("MONGODB_URL"))
guestbook = cluster["dagelan"]["guestbook"]

class EventExtension(Extension):
    bot: CustomClient

    @listen()
    async def on_member_join(self, event: MemberAdd):
        """This event is called when a user is joined to the server."""
        member = event.member
        user = event.member
        guild = event.member.guild

        user_in_db = guestbook.find_one({"uid": member.id})
        if user_in_db is None:
            # if user is in our discord server, change the status to True inside database
            newuser = {
                "id": member.id,
                "username": member.username,
                "discrim": member.discriminator,
                "verified": False,
            }
            guestbook.insert_one(newuser)
            self.verify_wait.start(member)

    @Task.create(IntervalTrigger(seconds=30))
    async def verify_wait(self, member):
        """this task is to check if a user is verified or not, if yes.. then give verified role to user"""
        user_in_db = guestbook.find_one({"uid": member.id})
        verified = user_in_db["verified"]
        verified_id = 922878963817263154
        if verified is False:
            return
        else:
            member.add_role(verified_id, "User requested to add role")
            self.verify_wait.stop()





def setup(bot: CustomClient):
    """Let naff load the extension"""

    EventExtension(bot)