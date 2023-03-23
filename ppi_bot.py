import discord
from discord.ext import tasks, commands
from discord.utils import get
from dotenv import load_dotenv
import asyncio
import os
import googletrans 
from discord import Embed


translator = googletrans.Translator()
intents = discord.Intents.default()
intents.members = True

# Create a dictionary of flag emojis and their corresponding language codes
flag_emoji_dict = {
"🇺🇸": "en",
"🇩🇪": "de",
"🇫🇷": "fr",
"🇪🇸": "es",
"🇮🇹": "it",
"🇵🇹": "pt",
"🇷🇺": "ru",
"🇦🇱": "sq",
"🇸🇦": "ar",
"🇧🇦": "bs",
"🇨🇳": "zh-CN",
"🇹🇷": "tr",
"🇵🇱": "pl",
"🇳🇴": "no",
"🇸🇬": "sv",
"🇯🇵": "ja",
"🇰🇷": "ko",
}

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

intents=discord.Intents.all()
prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)


#------------------------------------------------번역기------------------------------------------------------#

@bot.event
async def on_reaction_add(reaction, user):
  
    # Check if the reaction is a flag emoji
    if reaction.emoji in flag_emoji_dict:
        # Get the language code corresponding to the flag emoji
        lang_code = flag_emoji_dict[reaction.emoji]
        # Get the original message
        message = reaction.message
        # Translate the message to the desired language
        detected_lang = translator.detect(message.content)
        translated_message = translator.translate(message.content, dest=lang_code).text
        pronunciation_message = translator.translate(message.content, dest=lang_code).pronunciation

        embed = Embed(title='번역된 문장', description=f'{translated_message}', color=0x00ff00)
        embed.add_field(name="원문", value=message.content, inline=False)
        embed.add_field(name="발음", value=pronunciation_message, inline=False)
       # await reaction.message.channel.send(content=f'{reaction.user.mention}',embed=embed)
        await reaction.message.channel.send(content=f'{user.mention}',embed=embed)



#------------------------------------------------Events------------------------------------------------------#
intents.typing = False
intents.presences = False

class CustomView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.user_mentions = {}

    def add_button(self, button):
        self.add_item(button)
        self.user_mentions[button.custom_id] = []
        
class ButtonClick(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, custom_id=label)

    async def callback(self, interaction: discord.Interaction):
        view = interaction.view
        user = interaction.user
        user_mentions = view.user_mentions[self.custom_id]

        if user in user_mentions:
            user_mentions.remove(user)
        else:
            user_mentions.append(user)

        embed = discord.Embed(title="말하기 스터디 참여 현황")
        for button in view.children:
            mentions_str = " ".join([f"{user.mention}" for user in view.user_mentions[button.custom_id]])
            embed.add_field(name=button.label, value=mentions_str if mentions_str else "No one has clicked yet!", inline=True)
        await interaction.response.edit_message(embed=embed)
        
@bot.command(name='말하기')
async def speak(ctx):
    buttons = [
        ButtonClick("스페인어"),
        ButtonClick("중국어"),
        ButtonClick("일본어"),
        ButtonClick("영어"),
        ButtonClick("프랑스어"),
        ButtonClick("독일어"),
    ]

    view = CustomView()
    for button in buttons:
        view.add_button(button)

    embed = discord.Embed(title="말하기 스터디 참여 현황")
    for button in buttons:
        embed.add_field(name=button.label, value="No one has clicked yet!", inline=True)
    await ctx.send(embed=embed, view=view)
    
#------------------------------------------------Events------------------------------------------------------#


@bot.command(name='복제')
async def replicate(ctx, role_id: int):
    role_to_replicate = discord.utils.get(ctx.guild.roles, id=role_id)

    if not role_to_replicate:
        await ctx.send(f"Could not find the role with ID '{role_id}'.")
        return

    new_role = await ctx.guild.create_role(name=f"{role_to_replicate.name} (Replicate)", permissions=role_to_replicate.permissions)

    for member in role_to_replicate.members:
        await member.add_roles(new_role)

    await ctx.send(f"Role '{role_to_replicate.name}' has been replicated, and the new role has been assigned to the members with the original role.")


#Run the bot
bot.run(TOKEN)
