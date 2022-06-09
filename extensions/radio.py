# Credits to NAFTeam/Dis-Secretary (https://github.com/NAFTeam/Dis-Secretary)
import asyncio

from naff import Extension, GuildVoice, listen
from naff.api.events import VoiceStateUpdate
from naff.api.voice.audio import AudioVolume
from naff.client.utils import find
from naff_audio import YTAudio


class radio(Extension):
    async def async_start(self):
        for guild in self.bot.guilds:
            if channel := find(
                lambda c: c.id == 984499314619449358 and len(c.voice_members) != 0,
                guild.channels,
            ):
                asyncio.create_task(self.start_radio(channel))

    @listen()
    async def on_voice_state_update(self, event: VoiceStateUpdate):
        channel_id = event.before.channel.id if event.before else event.after.channel.id
        channel = self.bot.get_channel(channel_id)
        member = event.before.member if event.before else event.after.member

        if member.id != self.bot.user.id:
            if channel.id == 984499314619449358:
                vc = self.bot.get_bot_voice_state(channel.guild.id)
                if not vc and event.after is not None:
                    return await self.start_radio(channel)
                else:
                    asyncio.create_task(self.should_leave(channel))

    async def start_radio(self, channel: GuildVoice):
        vc = await channel.connect(deafened=True)
        vc.play_no_wait(
            await YTAudio.from_url("https://www.youtube.com/watch?v=5qap5aO4i9A")
        )

    async def should_leave(self, channel: GuildVoice):
        await asyncio.sleep(5)
        if len(channel.voice_members) == 1:
            if vc := self.bot.get_bot_voice_state(channel.guild.id):
                await vc.disconnect()


def setup(bot):
    radio(bot)
