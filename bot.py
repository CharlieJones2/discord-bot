import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import typing

ints = discord.Intents.all()


async def not_playing(interaction: discord.Interaction):
    await interaction.response.send_message('You aren\'t currently playing anything! Start playing a '
                                            'song and try again, or paste a link in the `link` parameter')


async def invalid_input(interaction: discord.Interaction):
    await interaction.response.send_message('You have provided an invalid input. Please note that this bot is only '
                                            'able to accept Spotify links as valid inputs.')


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
# initiate bot
    async def on_ready():
        synced = await bot.tree.sync()

# display number of active commands the bot can use

        print(f'Logged in as {name}!\n'
              f'synced {len(synced)} command(s)')

    @bot.tree.command(name='help')
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message('Here is a list of the commands you can use this bot for!\n\n'
                                                '`/song` - Allows you to add a song to the specified playlist. '
                                                'Defaults to the current song if no link is provided\n\n'
                                                '`/playlist` - Returns the playlist with the songs members of your '
                                                'server have added using the `/song` command.\n\n'
                                                '`/cover` - Returns the album cover of a song. '
                                                'Defaults to the current song if no link is provided.')

    @bot.tree.command(name='playlist')
# initiate command
    async def playlist(interaction: discord.Interaction):

        # send message with playlist link

        await interaction.response.send_message('Here is the link to your playlist :)\n\n'
                                                'https://open.spotify.com/playlist/...')

    @bot.tree.command(name='cover')
    @app_commands.describe(link='provide the link to the song or album you want the cover of')
# initiate command and prevent the bot responding to itself
    async def cover(interaction: discord.Interaction, link: typing.Optional[str]):
        if interaction.user == bot.user:
            return

# defaults to current song if no link is provided

        if link is None:
            track = spotify.current_playback()
            if track is None:
                await not_playing(interaction)
            else:
                album_cover = track["item"]["album"]["images"][0]["url"]
                await interaction.response.send_message(album_cover)

# parse message for link and extract details

        else:
            if 'open.spotify.com/track/' in link:
                track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
                spotify_uri = f'spotify:track:{track_id}'
                track = spotify.track(spotify_uri)

                # return album cover

                await interaction.response.send_message(track["album"]["images"][0]["url"])
            elif 'open.spotify.com/album/' in link:
                album_id = link.split('open_spotify.com/album/')[0].split('/album/')[1].split('?')[0]
                spotify_uri = f'spotify:album:{album_id}'
                album = spotify.album(spotify_uri)

                # return album cover

                await interaction.response.send_message(album["images"][0]["url"])
            else:
                await invalid_input()

    @bot.tree.command(name='song')
    @app_commands.describe(link='provide the link to your song')
# initiate command and prevent bot responding to itself
    async def song(interaction: discord.Interaction, link: typing.Optional[str]):
        if interaction.user == bot.user:
            return

# defaults to current song if no link is provided

        if link is None:
            track = spotify.current_playback()
            if track is None:
                await not_playing()
            else:
                spotify_uri = track["item"]["uri"]
                track = spotify.track(spotify_uri)
                playlist_id = 'https://open.spotify.com/playlist/...'
                spotify.playlist_add_items(playlist_id, items=[spotify_uri])

# send response confirming track has been added

                await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                        f'Song: `{track["name"]}`\n'
                                                        f'Artist: `{track["artists"][0]["name"]}`\n\n'
                                                        f'{track["album"]["images"][0]["url"]}')

# parse message for link and extract details

        else:
            if 'open.spotify.com/track/' in link:
                track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
                spotify_uri = f'spotify:track:{track_id}'
                track = spotify.track(spotify_uri)
                playlist_id = 'https://open.spotify.com/playlist/...'
                spotify.playlist_add_items(playlist_id, items=[spotify_uri])

# send response confirming track has been added

                await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                        f'Song: `{track["name"]}`\n'
                                                        f'Artist: `{track["artists"][0]["name"]}`\n\n'
                                                        f'{track["album"]["images"][0]["url"]}')
            else:
                await invalid_input()

        return

    bot.run(token)
