import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth

ints = discord.Intents.all()


def run_bot():
    token = 'DISCORD_TOKEN'

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='SPOTIFY_CLIENT_ID',
                                                        client_secret='SPOTIFY_SECRET_ID',
                                                        redirect_uri='http://localhost:8888/callback',
                                                        scope='playlist-modify-public playlist-modify-private '
                                                              'user-library-modify playlist-read-private '
                                                              'user-library-read playlist-read-collaborative'))

    bot = commands.Bot(command_prefix='!', intents=ints, permissions=2147535872)
    name = 'Playlist Creator'

    @bot.event
    async def on_ready():
        synced = await bot.tree.sync()
        print(f'Logged in as {name}!\n'
              f'synced {len(synced)} command(s)')

    @bot.tree.command(name='playlist')
    async def playlist(interaction: discord.Interaction):
        await interaction.response.send_message('Here is the link to your playlist :)\n\n'
                                                'https://open.spotify.com/playlist/38vx6xTz81I2zLTvGtafxJ?si=4a20084278264090')
        message = await interaction.original_response()
        print(message)

    @bot.tree.command(name='cover')
    @app_commands.describe(link='provide the link to the song or album you want the cover of')
    async def cover(interaction: discord.Interaction, link: str):
        if interaction.user == bot.user:
            return
        if 'open.spotify.com/track/' in link:
            track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
            spotify_uri = f'spotify:track:{track_id}'
            track = spotify.track(spotify_uri)
            await interaction.response.send_message(track["album"]["images"][0]["url"])
        elif 'open.spotify.com/album/' in link:
            album_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
            spotify_uri = f'spotify:track:{album_id}'
            album = spotify.track(spotify_uri)
            await interaction.response.send_message(album["album"]["images"][0]["url"])
        else:
            pass

    @bot.tree.command(name='song')
    @app_commands.describe(link='provide the link to your song')
    async def song(interaction: discord.Interaction, link: str):
        print(interaction.user)
        if interaction.user == bot.user:
            return
        
        if 'open.spotify.com/track/' in link:
            track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
            spotify_uri = f'spotify:track:{track_id}'
            track = spotify.track(spotify_uri)
            playlist_id = 'https://open.spotify.com/playlist/38vx6xTz81I2zLTvGtafxJ?si=c4e41135dbd54d52'
            spotify.playlist_add_items(playlist_id, items=[spotify_uri])

            await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                    f'Song: `{track["name"]}`\n'
                                                    f'Artist: `{track["artists"][0]["name"]}`\n\n'
                                                    f'{track["album"]["images"][0]["url"]}')
        else:
            pass

        return

    bot.run(token)
