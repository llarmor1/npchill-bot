import discord
from discord.ext import commands

import traceback

import config


class BaseCog(commands.Cog, name="Base"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Iniciado")
        print(self.bot.user)

        game = discord.Game(f"nove")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound)

        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            time_left = int(ctx.command.get_cooldown_retry_after(ctx) + 1)

            if time_left > 3600:
                num_hours = int(time_left / 3600)
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_hours} hours**."
                )
            elif time_left > 60:
                num_minutes = int(time_left / 60)
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_minutes} minutes**."
                )
            else:
                num_seconds = time_left + 1
                warn_msg = (
                    f"Command on **cooldown**. Try again in **{num_seconds} seconds**."
                )

            await ctx.send(warn_msg)
            return


        text_0 = f"Usuario: {ctx.author} ({ctx.author.id})"

        channel_fails = self.bot.get_channel(config.channel_fails_id)
        text_1 = ctx.message.content

        lines_list = traceback.format_exception(type(error), error, error.__traceback__)

        parrafos_list = []

        i = 0
        while i < len(lines_list):
            parrafo = ""

            while i < len(lines_list) and len(parrafo + lines_list[i]) < 1900:
                parrafo = parrafo + "\n" + lines_list[i]
                i += 1

            parrafos_list.append(parrafo)

        await channel_fails.send(f"{text_0}\n```{text_1}```")

        for parrafo in parrafos_list:
            await channel_fails.send(f"```py\n{parrafo}```")


    @commands.command(name="ping")
    async def ping(self, ctx) -> None:
        await ctx.send(f"{(round(self.bot.latency, 4))*1000} ms")



async def setup(bot):
    await bot.add_cog(BaseCog(bot))
    print("Base Cog LOADED")