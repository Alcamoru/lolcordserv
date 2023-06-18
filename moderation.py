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
            self.button_callback(announcement_button, )
            self.bot: commands.Bot = bot

        async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
            response: discord.InteractionResponse = interaction.response
            rules_channel = self.bot.get_channel(1119542979896557599)
            await response.send_message("Test")

    @commands.slash_command(name="sendembed")
    async def sendembed(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Bienvenue sur Lolcord", description="Attribuez vous des rôles")
        embed.add_field(name="✅ Membre", value="Pour accéder aux principaux salons du serveur")
        embed.add_field(name="🎮 LOLEUR", value="Vous jouez à League of Legends et souhaitez accéder aux salons de LOL",
                        inline=False)
        channel: discord.TextChannel = self.bot.get_channel(1119546314007519302)
        await channel.send(embed=embed)


    @commands.slash_command(name="button")
    async def button(self, ctx: discord.ApplicationContext):
        rules_embed = discord.Embed(title="Règles du serveur", description="Merci de lire ces règles et de les "
                                                                           "respecter",
                                    color=discord.Color(0xff0000))
        rules_embed.add_field(name="Messages", value="Les messages et contenus injurieux sont interdits")
        rules_embed.add_field(name="Mentions", value="Merci de ne pas mentionner inutilement les membres ou les "
                                                     "modérateurs", inline=False)
        rules_embed.set_footer(text="Cliquez sur le boutton ci-desssous pour accéder aux rôles")
        await ctx.send("**Bip Boup** \n Je suis le maitre de ce serveur \n"
                       "**Bip Boup**", view=self.AnnouncementsButton(self.bot), embed=rules_embed)


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