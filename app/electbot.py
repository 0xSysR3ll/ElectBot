#!/usr/bin/env python3

import discord
from discord import Embed
from discord.ext import commands
from utils.config import Config
from utils.database import ElectionDatabase
from utils.logger_config import setup_logger
from pretty_help import PrettyHelp
import time
import asyncio

NUMBER_EMOJIS = {
    0: "0️⃣",
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "🔟"
}

# Instantiate Config class and load data
config = Config("config/config.yml")
config.load()

# Setup logger
logger = setup_logger()

# Get Discord configuration
discord_config = config.get_config('discord')
TOKEN = discord_config['token']
GUILD_ID = discord_config['guild_id']
EMBED_IMAGE = discord_config['embed_image']

# Get database configuration
database_config = config.get_config('database')
db_parameters = {
    'host': database_config['host'],
    'port': database_config['port'],
    'username': database_config['username'],
    'password': database_config['password'],
    'database': database_config['database']
}

# Get candidates configuration
candidates_list = config.get_config('candidates')

# Instantiate the bot
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.help_command = PrettyHelp(ending_note="Développé avec ❤️ par @0xsysr3ll",
                              show_index=False, image_url=EMBED_IMAGE, no_category="Commandes disponibles", color=discord.Color.blue())
# Create tables
logger.info("Creating tables")
with ElectionDatabase(**db_parameters) as db:
    db.prepare_database()


@bot.event
async def on_ready():
    logger.info(f"Bot logged as {bot.user}")
    logger.info(f"Getting guild {GUILD_ID}")
    guild = bot.get_guild(GUILD_ID)
    logger.info(f"Guild name: {guild.name}")
    allowed_users = guild.members
    logger.info(f"Guild members: {len(allowed_users)}")
    logger.info("Adding candidates to database")
    with ElectionDatabase(**db_parameters) as db:
        for candidate in candidates_list:
            if not db.candidate_exists(candidate):
                db.add_candidate(candidate)
                logger.info(f"Added candidate {candidate['name']} to database")
            else:
                logger.info(
                    f"Candidate {candidate['name']} already exists in database")
        for user in allowed_users:
            user_id = user.id
            if not db.voter_exists(user_id):
                db.add_voter(user_id)
                logger.info(f"Added voter {user} to database")
            else:
                logger.info(f"Voter {user} already exists in database")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Erreur !",
            description=f"La commande `{ctx.invoked_with}`n'existe pas !",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name="candidats", help="📃 Afficher la liste les candidats ")
async def candidats(ctx):
    embed = Embed(title="Liste des candidats à l'élection",
                  color=discord.Color.blue(), timestamp=ctx.message.created_at)
    with ElectionDatabase(**db_parameters) as db:
        for candidate in db.get_candidates():
            embed.add_field(name=candidate[1],
                            value=candidate[2], inline=False)
    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    await ctx.send(embed=embed)


@bot.command(name="vote", help="🗳️ Voter pour une liste (disponible uniquement en message privé 💬)")
async def vote(ctx):
    allowed_users = bot.get_guild(GUILD_ID).members
    if ctx.author not in allowed_users:
        embed = discord.Embed(
            title="Erreur !",
            description="Vous n'êtes pas autorisé à voter. Si vous pensez que c'est une erreur, contactez @0xsysr3ll.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if ctx.channel.type != discord.ChannelType.private:
        embed = discord.Embed(
            title="Erreur !",
            description="Veuillez voter en message privé.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    embed = Embed(title="Bienvenue dans la cellule de vote de l'ESNA", color=discord.Color.blue(),
                  description="Pour voter pour une liste, réagissez avec le numéro correspondant.\nVous ne pouvez voter qu'une seule fois et toute tentative de triche sera sanctionnée.", timestamp=ctx.message.created_at)

    with ElectionDatabase(**db_parameters) as db:
        candidates = db.get_candidates()
        for candidate in candidates:
            candidate_id = candidate[0]
            embed.add_field(
                name=f"{candidate[1]} : {NUMBER_EMOJIS[candidate_id]}", value=candidate[2], inline=False)
    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    message = await ctx.send(embed=embed)

    for candidate in candidates:
        candidate_id = candidate[0]
        if candidate_id in NUMBER_EMOJIS:
            await message.add_reaction(NUMBER_EMOJIS[candidate_id])


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    logger.info(f"{user} reacted with {reaction}")
    total_seconds = 5
    with ElectionDatabase(**db_parameters) as db:
        if db.has_voted(user.id):
            embed = discord.Embed(
                title="Erreur !",
                description=f"Vous avez déjà voté !\nSi vous pensez que c'est une erreur, contactez @0xsysr3ll.\nCe message ainsi que l'urne vont s'auto détruire dans {total_seconds} secondes.",
                color=discord.Color.red()
            )
            warning = await user.send(embed=embed)

           # Update the embed description every second
            for i in range(total_seconds, 0, -1):
                await asyncio.sleep(1)  # Wait for 1 second
                embed.description = f"Vous avez déjà voté !\nSi vous pensez que c'est une erreur, contactez @0xsysr3ll.\nCe message ainsi que l'urne vont s'auto détruire dans {i-1} secondes."
                await warning.edit(embed=embed)

            # Delete the message after the countdown
            await warning.delete()
            await reaction.message.delete()

            return
        else:
            candidate_id = next(
                (key for key, value in NUMBER_EMOJIS.items() if value == reaction.emoji), None)
            embed = discord.Embed(
                title="À voter !",
                description=f"Votre vote pour pour la liste {candidate_id} a bien été pris en compte !",
                color=discord.Color.green()
            )
            await user.send(embed=embed)

            db.add_vote(user.id, candidate_id)
            logger.info(f"Added vote for candidate {candidate_id} to database")


@bot.command(name="resultats", help="📊 Afficher le résultat de l'élection (staff only 😛) ")
async def resultats(ctx):
    guild = bot.get_guild(GUILD_ID)
    role_names = [role.name for role in guild.get_member(ctx.author.id).roles]
    if "BDE" not in role_names:
        embed = discord.Embed(
            title="Erreur !",
            description="Vous n'êtes pas autorisé à voir les résultats. Si vous pensez que c'est une erreur, contactez @0xsysr3ll.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    embed = Embed(title="Résultats de l'élection",
                  color=discord.Color.blue(), timestamp=ctx.message.created_at)
    with ElectionDatabase(**db_parameters) as db:
        results = db.get_results()
        for result in results:
            embed.add_field(name=result[0],
                            value=f"Nombre de voix : {result[1]}", inline=False)

    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
