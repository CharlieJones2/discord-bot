import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import typing

ints = discord.Intents.all()


def run_bot():
    token = 'DISCORD_TOKEN'

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='SPOTIFY_TOKEN',
                                                        client_secret='SPOTIFY_SECRET',
                                                        redirect_uri='http://localhost:8888/callback',
                                                        scope='playlist-modify-public playlist-modify-private '
                                                              'user-read-currently-playing'))

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
                                                'https://open.spotify.com/playlist/...')

    @bot.tree.command(name='cover')
    @app_commands.describe(link='provide the link to the song or album you want the cover of')
    async def cover(interaction: discord.Interaction, link: typing.Optional[str]):
        if interaction.user == bot.user:
            return
        if link is None:
            track = spotify.current_playback()
            album_cover = track["item"]["album"]["images"][0]["url"]
            await interaction.response.send_message(album_cover)
        else:
            if 'open.spotify.com/track/' in link:
                track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
                spotify_uri = f'spotify:track:{track_id}'
                track = spotify.track(spotify_uri)
                await interaction.response.send_message(track["album"]["images"][0]["url"])
            elif 'open.spotify.com/album/' in link:
                album_id = link.split('open_spotify.com/album/')[0].split('/album/')[1].split('?')[0]
                spotify_uri = f'spotify:album:{album_id}'
                album = spotify.album(spotify_uri)
                await interaction.response.send_message(album["images"][0]["url"])
            else:
                pass

    @bot.tree.command(name='song')
    @app_commands.describe(link='provide the link to your song')
    async def song(interaction: discord.Interaction, link: typing.Optional[str]):
        print(interaction.user)
        if interaction.user == bot.user:
            return
        if link is None:
            track = spotify.current_playback()
            spotify_uri = track["item"]["uri"]
            track = spotify.track(spotify_uri)
            playlist_id = 'https://open.spotify.com/playlist/...'
            spotify.playlist_add_items(playlist_id, items=[spotify_uri])
            await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                    f'Song: `{track["name"]}`\n'
                                                    f'Artist: `{track["artists"][0]["name"]}`\n\n'
                                                    f'{track["album"]["images"][0]["url"]}')
        # parse message for spotify link
        else:
            if 'open.spotify.com/track/' in link:
                track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
                spotify_uri = f'spotify:track:{track_id}'
                track = spotify.track(spotify_uri)
                playlist_id = 'https://open.spotify.com/playlist/...'
                spotify.playlist_add_items(playlist_id, items=[spotify_uri])

                await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                        f'Song: `{track["name"]}`\n'
                                                        f'Artist: `{track["artists"][0]["name"]}`\n\n'
                                                        f'{track["album"]["images"][0]["url"]}')
            else:
                pass

        return

    bot.run(token)
