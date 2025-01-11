import os
import discord  # type: ignore
import logging  # type: ignore
import pandas as pd  # type: ignore

from dotenv import load_dotenv

from datetime import datetime
from discord.ext import tasks  # type: ignore
from discord.ext import commands  # type: ignore

from bot.package import (
    get_future_events,
    clean_events,
    get_top_10_teams,
    get_team_object,
)

# Configure logging
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] | %(message)s",
    level=logging.DEBUG,  # You can change this to INFO, WARNING, ERROR, etc.
)

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ENV = os.getenv("ENV")

# Variables
RESTRICTION_LIST = [
    "Open",
    "Individual",
    "High-school",
]  # Filter the CTF you're interested in depending on the restriction types

USELESS_COLUMNS = [
    "ctf_id",
    "weight",
    "logo",
    "live_feed",
    "format",
    "participants",
    "public_votable",
    "is_votable_now",
    "prizes",
    "organizers",
    "format_id",
    "duration",
    "onsite",
    "location",
    "ctftime_url",
    "restrictions",
]

CTF_TO_PLAY = []

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
intents.message_content = True
intents.typing = False
intents.presences = False


@bot.command(name="status")
async def status(ctx):
    await ctx.send(f"Je suis en ligne !\nJe tourne depuis l'env de {ENV}🚀")


@bot.command(name="commandes")
async def commandes(ctx):
    message = "```markdown\n"
    message += "🚀 BIENVENUE SUR LE BOT CTF-TIME 🚀\n"
    message += "Voici la liste des commandes disponibles :\n"
    message += "************************************************************************************************\n"
    message += "- !commandes : Affiche la liste des commandes disponibles\n"
    message += "- !status : Affiche le statut du bot\n"
    message += "************************************************************************************************\n"
    message += "- !top10 : Affiche le top 10 des équipes pour l'année en cours\n"
    message += "- !top10 <année> : (param non obligatoire) Affiche le top 10 des équipes pour l'année donnée\n"
    message += "************************************************************************************************\n"
    message += "- !newctf : Affiche les prochains CTFs pour les 14 prochains jours à venir\n"
    message += "- !newctf <jours> : (param non obligatoire) Affiche les prochains CTFs pour les jours à venir\n"
    message += "- !details <CTF ID> : (param obligatoire) Affiche les détails d'un CTF spécifique\n"
    message += "************************************************************************************************\n"
    message += "- !team : Affiche le classement d'0xECE sur les 3 dernières années\n"
    message += "- !team <team_id> : Affiche le classement d'une équipe donnée sur les 3 dernières années\n"
    message += "************************************************************************************************\n"
    message += "```"
    await ctx.send(message)

@bot.command(name="newctf")
async def newctf(ctx, days: int = 14):
    """
    Affiche les prochains CTFs pour les jours à venir
    """
    if days < 1:
        await ctx.send("Le nombre de jours doit être supérieur à 0.")
        return

    if days > 100:
        await ctx.send("Le nombre de jours doit être inférieur à 100.")
        return

    events = get_future_events(day_limit=days)
    logging.info(f"Retrieved {len(events)} CTFs for the next {days} days")

    events_df = clean_events(
        events=events, restriction_list=RESTRICTION_LIST, useless_columns=USELESS_COLUMNS
    )
    logging.info(f"After data cleaning we found {events_df.shape[0]} interesting CTFs for you.")
    
    #remove columns ctftime_id 'organizer_name', 'duration_hours', 'open', 'individual' 'high-school'
    events_df = events_df.drop(columns=['organizer_name', 'duration_hours', 'open', 'individual', 'high-school'])
    message = "```markdown\n"
    message += "🚀 PROCHAINS CTFs 🚀\n"
    message += f"Voici les prochains CTFs pour les {days} jours à venir :\n\n"
    message += f"{'Nom du CTF':<20} {'Début':<30} {'Fin':<30} {'CTF ID':<30}\n"
    message += "-" * 90 + "\n"
    for index, row in events_df.iterrows():
        message += f"{row['title']:<20} {row['start']:<30} {row['finish']:<30} {row['ctftime_id']:<30}\n"
    message += "\n\nUtilisez !details <CTF ID> pour plus de détails sur un CTF spécifique."
    message += "```"
    
    await ctx.send(message)

def true_false(value):
    if value:
        return "Oui"
    return "Non"

@bot.command(name="details")
async def details(ctx, ctftime_id: int):
    """
    Affiche les détails d'un CTF spécifique
    """
    if ctftime_id:
        events = get_future_events(day_limit=100)
        events_df = clean_events(
            events=events, restriction_list=RESTRICTION_LIST, useless_columns=USELESS_COLUMNS
        )
        # search for the event in the df
        event = events_df[events_df['ctftime_id'] == ctftime_id]
        if event.empty:
            await ctx.send(f"CTF avec l'ID {ctftime_id} non trouvé.")
        else:
            event = event.iloc[0]
            message = "```markdown\n"
            message += f"🚀 DETAILS CTF - {event['title']} 🚀\n"
            message += f"Voici les détails du CTF {event['title']} :\n\n"
            message += "-" * 45 + "\n"
            message += f"{'Nom du CTF':<20} {event['title']:<30}\n"
            message += f"{'Individuel':<20} {true_false(event['individual']):<30}\n"
            message += f"{'Universitaire':<20} {true_false(event['high-school']):<30}\n"
            message += f"{'Début':<20} {event['start']:<30}\n"
            message += f"{'Fin':<20} {event['finish']:<30}\n"
            message += f"{'\nDescription:':<20}\n\n{event['description']}\n"
            message += f"{'\nURL':<20} {event['url']}\n"
            message += "```"
            await ctx.send(message)
            
# TODO : reparer le bug de l'ajout de CTF
@bot.command(name="play")
async def play(ctx, ctftime_id: int):
    """
    Affiche les détails d'un CTF spécifique
    """
    if ctftime_id:
        events = get_future_events(day_limit=100)
        events_df = clean_events(
            events=events, restriction_list=RESTRICTION_LIST, useless_columns=USELESS_COLUMNS
        )
        # search for the event in the df
        event = events_df[events_df['ctftime_id'] == ctftime_id]
        print(event)
        if event.empty:
            await ctx.send(f"CTF avec l'ID {ctftime_id} non trouvé.")
        else:
            # convert the event to a dictionary
            event = event.iloc[0].to_dict()
            for event in CTF_TO_PLAY:
                print(event["ctftime_id"], ctftime_id)
                if event["ctftime_id"] == ctftime_id:
                    await ctx.send(f"CTF '{event['title']}' déjà ajouté à la liste.")
                    return
            CTF_TO_PLAY.append(event)
            await ctx.send(f"CTF '{event['title']}' ajouté à la liste.")
    else:
        await ctx.send("Veuillez spécifier un ID de CTF.")

@bot.command(name="purge")
async def purge(ctx, ctftime_id: int):
    """
    Affiche les détails d'un CTF spécifique
    """
    if ctftime_id:
        if CTF_TO_PLAY:
            for event in CTF_TO_PLAY:
                if event["ctftime_id"] == ctftime_id:
                    CTF_TO_PLAY.remove(event)
                    await ctx.send(f"CTF '{event['title']}' supprimé de la liste.")
                    return
            await ctx.send(f"CTF avec l'ID {ctftime_id} non trouvé.")
    else:
        await ctx.send("Veuillez spécifier un ID de CTF.")


@bot.command(name="registered")
async def play(ctx):
    """
    Affiche tout les CTFs ajoutés à la liste
    """
    if CTF_TO_PLAY:
        message = "```markdown\n"
        message += "🚀 CTFs À JOUER 🚀\n"
        message += "Voici la liste des CTFs à jouer :\n\n"
        message += f"{'Nom du CTF':<20} {'Début':<30} {'Fin':<30} {'CTF ID':<30}\n"
        message += "-" * 90 + "\n"
        for event in CTF_TO_PLAY:
            message += f"{event['title']:<20} {event['start']:<30} {event['finish']:<30} {event['ctftime_id']:<30}\n"
        message += "```"
        await ctx.send(message)
    else:
        await ctx.send("Aucun CTF à jouer pour le moment.")
    

@bot.command(name="top10")
async def top10(ctx, year: int = datetime.now().year):
    """
    Affiche le top 10 des équipes
    """
    top_10 = get_top_10_teams(year)
    if(top_10.empty):
        await ctx.send(f"Top 10 des équipes non trouvé pour l'année {year}.")
        return
    message = "```markdown\n"
    message += f"🚀 TOP 10 DES ÉQUIPES pour {year} 🚀\n"
    message += "Voici le top 10 des équipes :\n\n"
    message += f"{'ID':<10} {'Team Name':<30} {'Score':<20}\n"
    message += "-" * 60 + "\n"
    for index, row in top_10.iterrows():
        message += f"{row['team_id']:<10} {row['team_name']:<30} {row['points']:<20}\n"
    message += "```"
    await ctx.send(message)

@bot.command(name="team")
async def team(ctx, team_id: str ="216659"):
    """
    Affiche le score d'une équipe donnée pour une année donnée
    """
    team = get_team_object(team_id)
    if team:
        message = "```markdown\n"
        message += f"🚀 SCORE DE L'ÉQUIPE {team.name} pour l'année 🚀\n"
        message += f"\n{'Année':<10} | {'Classement':<30}\n" + "-" * 25 + "\n"
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 1):
            if str(year) in team.rating and 'rating_place' in team.rating[str(year)]:
                message += f"{year:<10} | {team.rating[str(year)]['rating_place']:<30}\n"
            else:
                message += f"{year:<10} | {'N/A':<30}\n"
        message += "```"
        await ctx.send(message)
    else:
        await ctx.send(f"Équipe {team_id} non trouvée.")

@tasks.loop(hours=24)
async def periodic_task():

    # check if the list is empty
    if CTF_TO_PLAY:
        # get the current date
        current_date = datetime.now().date()
        logging.debug("Periodic task running")
        logging.info(f"Checking CTFs to play at {current_date}")    
        for event in CTF_TO_PLAY:
            # convert the start date to a datetime object
            start_date = datetime.strptime(event['start'], "%Y-%m-%dT%H:%M:%S%z")
            start_date = start_date.date()
            type(start_date)
            # check if the current date is equal to the start date
            if current_date > start_date:
                # remove the event from the list
                CTF_TO_PLAY.remove(event)
                # send a message to the channel
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f"CTF '{event['title']} supprimé de la liste car il a déjà commencé.")
            # check if the CTF is in exactly 5 days
            days_until_start = (start_date - current_date).days
            if days_until_start == 5 or days_until_start == 3:
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f"CTF '{event['title']}' commence dans quelques jours ! Pensez à inscrire l'équipe.")
            elif days_until_start == 1:
                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(f"CTF '{event['title']}' commence demain ! Pensez à inscrire l'équipe.")
    else:
        logging.info("Aucun CTF à jouer")


@bot.event
async def on_ready():
    logging.info(f"{bot.user} is online!")

    periodic_task.start()

    # ID du channel où le bot doit envoyer le message
    channel_id = CHANNEL_ID  # Remplace par l'ID de ton channel
    channel = bot.get_channel(channel_id)

    logging.info(f"{bot.user} est connecté à {len(bot.guilds)} serveur(s) :")
    for guild in bot.guilds:
        logging.info(f"- {guild.name} (ID: {guild.id})")

    if channel:
        await channel.send("Yo, je suis la V2 🚀")
        await channel.send(f"Je tourne depuis l'env de {ENV}🚀\nPour voir la liste des commandes disponibles, tapez !commandes")
    else:
        logging.error("Channel introuvable !")

bot.run(TOKEN)