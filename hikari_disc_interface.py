import hikari 
import lightbulb
import asyncio
from dotenv import load_dotenv
import os

# hikari documentation
# https://docs.hikari-py.dev/en/stable/

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
print(ACCESS_TOKEN)

PREFIX = "!"

bot = lightbulb.BotApp(
    token = ACCESS_TOKEN, 
    intents = hikari.Intents.ALL, 
    prefix = PREFIX)

"""

START EVENT AND INITIALIZATION

"""
@bot.listen(hikari.StartingEvent)
async def on_starrting(event: hikari.StartingEvent):
    print('bot is starting')
 
@bot.listen(hikari.StartingEvent)
async def on_started(event: hikari.StartingEvent):
    user = await bot.rest.fetch_my_user()
    print(f'started sucessfully {user.username}')

"""

EXCEPTIONS

"""
@bot.listen(hikari.ExceptionEvent)
async def on_exception(event: hikari.ExceptionEvent):
    print(event.exception)







"""

VOICE 

need to refactor when further functionalities are added especially, make the join and leave into their own helper functions
"""

@bot.command
@lightbulb.command("join", "a")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: lightbulb.Context):
    guild_id = ctx.guild_id

    #early exit check to see prereq
    if not guild_id:
        await ctx.respond("invalid command")
        return 

    #checks state of calling user -> if user is in a call or not
    voice_state = ctx.bot.cache.get_voice_state(guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id: 
        await ctx.respond("join a voice channel first")

    try:
        await bot.update_voice_state(guild_id, voice_state.channel_id, self_deaf=False)
        await ctx.resopnd(f"joined:{ {voice_state.channel_id}}")
    except Exception as e:
        await ctx.respond(f"error: failed to join call {e}") 



@bot.command
@lightbulb.command("leave", "a")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def leave(ctx: lightbulb.Context):
    guild_id = ctx.guild_id

    if not guild_id:
        await ctx.respond("invalid command")
        return 

    try:
        await bot.update_voice_state(guild_id, None)
        await ctx.respond("left")
    except Exception as e:
        await ctx.respond(f"failed to leave {e}")





"""

SAMPLE

"""







#placeholder -> for testing purposes
def process_mention(message: str) -> str:
    return f'mentioned! {message}'

@bot.listen(hikari.DMMessageCreateEvent)
async def detect_dm_mentions(event: hikari.DMMessageCreateEvent):
    if event.author_id == bot.get_me().id:
        return 


    if bot.get_me().mention in (event.message.content or ""):
        response = process_mention(event.message.content)
        await event.message.respond(response)



if __name__ == "__main__":
    bot.run()
