import discord

from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # Called when a reaction is added
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

    # Called when a reaction is removed
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

    # Called when a message is sent
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ban_words = ["putes", "connard", "enculé", "pute", "con", "merde"]
        split_message = message.content.split(" ")
        for word in split_message:
            if word in ban_words:
                embed_bad_word = discord.Embed(title="Modération",
                                               description=f"Evenement interdit, {message.author.mention}",
                                               color=discord.Color.from_rgb(255, 255, 0))
                embed_bad_word.add_field(name="Mot banni", value="Vous avez utilisé un mot banni.")
                await message.channel.send(embed=embed_bad_word)
                await message.delete(reason="Mot interdit")

    # This command remove n messages from a channel
    @commands.has_any_role("Modérateur", "Administrateur")
    @commands.slash_command(name="suppr", description="Supprimer un certain nombre de messages d'un salon")
    async def suppr(self, ctx: discord.ApplicationContext, n_messages: int):
        channel: discord.TextChannel = ctx.channel
        embed = discord.Embed(title="Modération", description=f"{n_messages} supprimés",
                              color=discord.Color.from_rgb(51, 73, 255))
        await channel.purge(limit=n_messages)
        await ctx.respond(embed=embed)

    # This command mutes a user
    @commands.has_any_role("Modérateur", "Administrateur")
    @commands.slash_command(name="mute", description="Rend muet l'utilisateur")
    async def mute(self, ctx: discord.ApplicationContext, member: discord.Member, reason):
        embed = discord.Embed(title="Modération", description="Musellement d'un membre",
                              color=discord.Color.from_rgb(255, 255, 0))
        embed.add_field(name="Notification d'expulsion", value=f"{member.mention} a bien été rendu muet pour"
                                                               f" la raison suivante: {reason}")
        guild = self.bot.get_guild(1117482753076776982)
        mute_role = guild.get_role(1123157727284305991)
        for role in member.roles[1:]:
            print(role.name)
            await member.remove_roles(role)
        await member.add_roles(mute_role)
        await ctx.respond(embed=embed)
        await member.send(embed=embed)

    # This command kick a user from the server
    @commands.has_any_role("Modérateur", "Administrateur")
    @commands.slash_command(name="kick", description="Explusion de l'utilisateur")
    async def kick(self, ctx: discord.ApplicationContext, member: discord.Member, reason):
        embed_kick = discord.Embed(title="Modération", description="Expulsion d'un membre",
                                   color=discord.Color.from_rgb(255, 255, 0))
        embed_kick.add_field(name="Notification d'expulsion", value=f"{member.mention} a bien été banni du serveur pour"
                                                                    f" la raison suivante {reason}")
        await ctx.respond(embed=embed_kick)
        await member.send(embed=embed_kick)
        await member.kick(reason=reason)

    # This command ban a user from the server
    @commands.has_any_role("Modérateur", "Administrateur")
    @commands.slash_command(name="ban", description="Bannissement de l'utilisateur")
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason):
        embed_ban = discord.Embed(title="Modération", description="Bannissement d'un membre",
                                  color=discord.Color.from_rgb(255, 255, 0))
        embed_ban.add_field(name="Notification de bannissement", value=f"{member.mention} a bien été banni pour la"
                                                                       f"raison suivante: {reason}")
        await ctx.respond(embed=embed_ban)
        await member.send(embed=embed_ban)
        await member.ban(reason=reason)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
