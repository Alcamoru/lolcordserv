import discord

from discord.ext import commands
from discord.ui import Item


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    class AnnouncementsButton(discord.ui.View):
        def __init__(self, bot, *items: Item):
            super().__init__(*items)
            announcement_button = discord.ui.Button(label="Accéder aux rôles", style=discord.ButtonStyle.link,
                                                    emoji="✅",
                                                    url="https://discord.com/channels/1117482753076776982/1119546314007519302",
                                                    )
            self.add_item(announcement_button)
            self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        message_content = message.content

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(1117482753076776982)
        user: discord.Member = guild.get_member(payload.user_id)

        if payload.message_id == 1119618619404468236:
            if payload.emoji.name == "✅":
                member_role: discord.Role = guild.get_role(1119559385820176404)
                await user.add_roles(member_role)
            if payload.emoji.name == "🎮":
                loleur_role = guild.get_role(1117486329446531195)
                await user.add_roles(loleur_role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(1117482753076776982)
        user: discord.Member = guild.get_member(payload.user_id)

        if payload.message_id == 1119618619404468236:
            if payload.emoji.name == "✅":
                member_role: discord.Role = guild.get_role(1119559385820176404)
                await user.remove_roles(member_role)
            if payload.emoji.name == "🎮":
                loleur_role = guild.get_role(1117486329446531195)
                await user.remove_roles(loleur_role)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))