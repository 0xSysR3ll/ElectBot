#!/usr/bin/env python3
"""
This module provides functionalities related to the ElectBot.
"""
import discord
from discord import Embed
from discord.ext import commands
from utils.config import Config
from utils.database import ElectionDatabase
from utils.logger_config import setup_logger
from pretty_help import PrettyHelp

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
bot.help_command = PrettyHelp(
    ending_note="Développé avec ❤️ par @0xsysr3ll",
    show_index=False,
    image_url=EMBED_IMAGE,
    no_category="Commandes disponibles",
    color=discord.Color.blue()
)
# Create tables
logger.info("Creating tables")
with ElectionDatabase(db_parameters) as election_db:
    election_db.prepare_database()


@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info("Bot logged as %s", bot.user)
    logger.info("Getting guild %s", GUILD_ID)
    guild = bot.get_guild(GUILD_ID)
    logger.info("Guild name : %s", guild.name)
    allowed_users = guild.members
    logger.info("Guild members : %s", len(allowed_users))
    logger.info("Adding candidates to database")
    with ElectionDatabase(db_parameters) as prep_db:
        for candidate in candidates_list:
            if not prep_db.candidate_exists(candidate):
                prep_db.add_candidate(candidate)
                logger.info("Added candidate %s to database",
                            candidate['name'])
            else:
                logger.info(
                    "Candidate %s already exists in database", candidate['name'])
        for user in allowed_users:
            user_id = user.id
            if not prep_db.voter_exists(user_id):
                prep_db.add_voter(user_id)
                logger.info("Added voter %s to database", user)
            else:
                logger.info("Voter %s already exists in database", user)


@bot.event
async def on_command_error(error):
    """
    Handles command errors and sends a message to the user if the command is not found.

    Args:
        ctx: The context in which the command was called.
        error: The error raised by the command.
    """
    if isinstance(error, commands.CommandNotFound):
        return


@bot.command(
    name="candidats",
    help="📃 Afficher la liste les candidats"
)
async def candidats(ctx):
    """
    Sends an embedded message to the user displaying the list of election candidates.

    Args:
        ctx: The context in which the command was called.

    Uses:
        ElectionDatabase: To fetch the list of candidates.
    """
    embed = Embed(
        title="Liste des candidats à l'élection",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at
    )
    with ElectionDatabase(db_parameters) as db_get:
        for candidate in db_get.get_candidates():
            embed.add_field(name=candidate[1],
                            value=candidate[2], inline=False)
    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    await ctx.send(embed=embed)


@bot.command(
    name="vote",
    help="🗳️ Voter pour une liste (disponible uniquement en message privé 💬)"
)
async def vote(ctx):
    """
    Allows a user to vote for a candidate via private message. 

    The command checks if the user is allowed to vote and whether
    the command was invoked in a private message.
    An embedded message will be sent to the user displaying the list of candidates to vote for.
    The user can then react to the message to cast their vote.

    Args:
        ctx: The context in which the command was called.

    Uses:
        ElectionDatabase: To fetch the list of candidates.
    """
    allowed_users = bot.get_guild(GUILD_ID).members
    if ctx.author not in allowed_users:
        ctx.send("Erreur ! Vous n'êtes pas autorisé à voter.")
        return

    if ctx.channel.type != discord.ChannelType.private:
        error = await ctx.send("Erreur ! Vous ne pouvez voter qu'en message privé.")
        await error.delete(delay=1)
        return

    embed = Embed(
        title="Bienvenue dans la cellule de vote de l'ESNA",
        color=discord.Color.blue(),
        description=
        "Pour voter pour une liste, réagissez avec le numéro correspondant.\n"
        "Vous ne pouvez voter qu'une seule fois et toute tentative de triche sera sanctionnée.",
        timestamp=ctx.message.created_at
    )

    with ElectionDatabase(db_parameters) as list_db:
        candidates = list_db.get_candidates()
        for candidate in candidates:
            candidate_id = candidate[0]
            embed.add_field(
                name=f"{candidate[1]} : {NUMBER_EMOJIS[candidate_id]}",
                value=candidate[2],
                inline=False
            )
    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    message = await ctx.send(embed=embed)

    for candidate in candidates:
        candidate_id = candidate[0]
        if candidate_id in NUMBER_EMOJIS:
            await message.add_reaction(NUMBER_EMOJIS[candidate_id])


@bot.event
async def on_reaction_add(reaction, user):
    """
    Handles the event when a user reacts to a message.

    If the user reacts with a valid emoji corresponding to a candidate, 
    their vote is recorded in the database. If the user has already voted,
    they are notified with an error message.

    Args:
        reaction: The reaction object that was added.
        user: The user who added the reaction.

    Uses:
        ElectionDatabase: To check if a user has already voted and to record the vote.
    """
    if user == bot.user:
        return
    logger.info("%s reacted with %s", user, reaction.emoji)
    with ElectionDatabase(db_parameters) as vote_db:
        if vote_db.has_voted(user.id):
            error = await user.send("Erreur ! Vous avez déjà voté.")
            await error.delete(delay=1)
            return

        candidate_id = next(
            (key for key, value in NUMBER_EMOJIS.items() if value == reaction.emoji), None)
        embed = discord.Embed(
            title="À voter !",
            description=
            f"Votre vote pour pour la liste {candidate_id} "
            "a bien été pris en compte !",
            color=discord.Color.green()
        )
        await user.send(embed=embed)

        vote_db.add_vote(user.id, candidate_id)
        logger.info("Added vote for candidate %s to database", candidate_id)


@bot.command(
    name="resultats",
    help="📊 Afficher le résultat de l'élection (staff only 😛) "
)
async def resultats(ctx):
    """
    Sends an embedded message displaying the election results.

    Only members with the "BDE" role can view the election results. If a member without the "BDE" 
    role tries to view the results, they will receive an error message.

    Args:
        ctx: The context in which the command was called.

    Uses:
        ElectionDatabase: To fetch the election results.
    """
    guild = bot.get_guild(GUILD_ID)
    role_names = [role.name for role in guild.get_member(ctx.author.id).roles]
    if "BDE" not in role_names:
        error = await ctx.send("Erreur ! Vous n'êtes pas autorisé à voir les résultats.")
        await error.delete(delay=1)
        return
    embed = Embed(
        title="Résultats de l'élection",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at
    )
    with ElectionDatabase(db_parameters) as result_db:
        results = result_db.get_results()
        for result in results:
            embed.add_field(
                name=result[0],
                value=f"Nombre de voix : {result[1]}",
                inline=False
            )

    embed.set_image(url=EMBED_IMAGE)
    embed.set_footer(text="Développé avec ❤️ par @0xsysr3ll")
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
