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

        async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
            response: discord.InteractionResponse = interaction.response
            rules_channel = self.bot.get_channel(1119542979896557599)
            await response.send_message("Test")

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
    async def on_raw_raction_add(self, payload: discord.RawReactionActionEvent):
        user = self.bot.get_user(payload.user_id)
        if payload.emoji: discord.Emoji == discord.Emoji()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        message_content = message.content

def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))