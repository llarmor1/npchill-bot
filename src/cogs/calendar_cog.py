import asyncio
import copy
from datetime import date
import time

import aiohttp
import discord
from discord.ext import commands

import config
import src.util.CONSTANTS as CONSTANTS
from src.util.calendar_generator import CalendarGenerator
from src.util.StringService import StringService

PREFIX = config.prefix


class BirthdayCog(commands.Cog, name="Birthday"):
    def __init__(self, bot):
        self.bot = bot
        self.cg = CalendarGenerator()
        self.stringService = StringService()
        self.bot.loop.create_task(self.check_birthday())

    @commands.command(aliases=['cumpleaños', 'cum'])
    async def setbirthday(self, ctx):
        args = ctx.message.content.split()[2:]

        # DIA - MES

        if len(args) == 0:
            await ctx.send(f"Uso correcto `{PREFIX}setbirthday día/mes`")
        else:
            string = " ".join(args)
            numbers_list = self.stringService.findNumbers(string)

            if len(numbers_list) < 2:
                await ctx.send(f"Uso correcto `{PREFIX}setbirthday día/mes`")
            else:
                # MES
                if numbers_list[1] < 1 or numbers_list[1] > 12:
                    await ctx.send("El número de mes solo toma valores entre 1 y 12")
                elif (
                    numbers_list[0] < 1
                    or numbers_list[0] > CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]
                ):
                    await ctx.send(
                        f"El número de día para el mes de **{CONSTANTS.MONTH_STRING[numbers_list[1]]}** solo toma valores entre 1 y {CONSTANTS.MAX_DAYS_BY_MONTH[numbers_list[1]]}"
                    )
                else:
                    profile = self.bot.database.get_profile(ctx.author.id)
                    self.bot.database.update_birthday( # DYNAMODB FUNC
                        ctx.author.id, numbers_list[0], numbers_list[1]
                    )
                    await ctx.send(
                        f"Día de cumpleaños guardado: **{numbers_list[0]} de {CONSTANTS.MONTH_STRING[numbers_list[1]]}**"
                        )



    async def calendar(self, ctx):
        args = ctx.message.content.split()[2:]

        month_num = None

        if len(args) > 0:
            if args[0].isdigit():
                arg_int = int(args[0])

                if arg_int > 0 and arg_int < 13:
                    month_num = arg_int

        if not month_num:
            month_num = time.gmtime().tm_mon

        users_birthday = self.bot.database.get_users_birthday(month_num)

        bytes_dict = {}

        for profile in users_birthday:
            member = ctx.guild.get_member(int(profile["user_id"]))


            if member:
                asset = member.avatar.with_size(128)
                avatar_bytes = await asset.read()

                
                if (profile["birthday_date_day"] not in bytes_dict.keys()): # Primera iteracion
                    bytes_dict[int(profile["birthday_date_day"])] = [] 


                bytes_dict[int(profile["birthday_date_day"])].append(avatar_bytes)

        

        img_buffer = self.cg.new_calendar_img(month_num, bytes_dict)

        await ctx.send(file=discord.File(fp=img_buffer, filename="hb.png"))



    async def check_birthday(self):
        while not self.bot.is_closed():
            await asyncio.sleep(600) # 10 min

            guild_npchill = self.bot.get_guild(config.npchill_id)
            role = guild_npchill.get_role(config.role_birthday_id)
            birthday_members = guild_npchill.get_role(
                config.role_birthday_id
            ).members  # Los que tienen el rol del cumpleaños
            result = self.bot.database.get_all_profiles()

            users = [
                x["user_id"]
                for x in result
                if x["birthday_date_day"] == date.today().day
                and x["birthday_date_month"] == date.today().month
            ]
            new_birthday_members = [
                guild_npchill.get_member(y) for y in users
            ]  # Los que cumplen

            for busr in birthday_members:
                if busr not in new_birthday_members:
                    await busr.remove_roles(role)

            for usr in new_birthday_members:
                if role not in usr.roles:
                    await usr.add_roles(role)


async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
    print("Birthday Cog LOADED")
