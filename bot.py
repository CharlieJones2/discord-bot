import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import typing
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re


ints = discord.Intents.all()

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='SPOTIFY_CLIENT_ID',
                                                    client_secret='SPOTIFY_SECRET_ID',
                                                    redirect_uri='http://localhost:8888/callback',
                                                    scope='playlist-modify-public playlist-modify-private '
                                                              'user-read-currently-playing user-read-recently-played '
                                                              'user-top-read'))


async def not_playing(interaction: discord.Interaction):
    await interaction.response.send_message('You aren\'t currently playing anything! Start playing a '
                                            'song and try again, or paste a link in the `link` parameter')


async def invalid_input(interaction: discord.Interaction):
    await interaction.response.send_message('You have provided an invalid input. Please note that this bot is only '
                                            'able to accept Spotify links as valid inputs.')


async def chart(interaction: discord.Interaction, data=None, timeframe=None, song_or_artist=None):
    sns.set(style='darkgrid')
    plt.figure(figsize=(10, 6))
    sns.barplot(x=str(song_or_artist), y='Popularity', data=data, palette=sns.color_palette("muted", len(data)))
    plt.gcf().set_facecolor("none")
    plt.title(f"Top {song_or_artist}s - {timeframe}", color='white')
    plt.xlabel(song_or_artist, color='white')
    plt.ylabel(f"Popularity of your top {song_or_artist}s", color='white')
    plt.xticks(rotation=45, ha="right", color='white')
    plt.yticks(color='white')
    plt.tight_layout()
    plt.savefig('chart.png')
    await interaction.response.send_message(file=discord.File('chart.png'))


async def get_cover(interaction: discord.Interaction, link=None):
    pattern = r'open\.spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)'
    match = re.search(pattern, link)
    try:
        cover_type = match.group(1)
        cover_id = match.group(2)
        spotify_uri = f'spotify:{cover_type}:{cover_id}'

        if cover_type == 'track':
            cover_id = spotify.track(spotify_uri)
            cov = cover_id['album']['images'][0]['url']
        elif cover_type == 'album':
            cover_id = spotify.album(spotify_uri)
            cov = cover_id['images'][0]['url']
        elif cover_type == 'playlist':
            cover_id = spotify.playlist(spotify_uri)
            cov = cover_id['images'][0]['url']
        else:
            cov = invalid_input(interaction)
        await interaction.response.send_message(cov)

    except AttributeError:
        await invalid_input(interaction)


def run_bot():
    token = 'DISCORD_TOKEN'
    bot = commands.Bot(command_prefix='!', intents=ints, permissions=2147535872)
    name = 'Playlist Creator'

    @bot.event
    async def on_ready():
        synced = await bot.tree.sync()
        print(f'Logged in as {name}!\n'
              f'synced {len(synced)} command(s)')

    @bot.tree.command(name='help')
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message('Here is a list of the commands you can use this bot for!\n\n'
                                                '`/song` - Allows you to add a song to the specified playlist. '
                                                'Defaults to the current song if no link is provided\n\n'
                                                '`/playlist` - Returns the playlist with the songs members of your '
                                                'server have added using the `/song` command.\n\n'
                                                '`/cover` - Returns the album cover of a song, album or playlist. '
                                                'Defaults to the current song if no link is provided.'
                                                '`/chart-top-artists` returns graphical info on your top artists.\n\n'
                                                '`/chart-top-songs` does the same for your top songs.')

    @bot.tree.command(name='chart-top-artists')
    @app_commands.describe(size='how many artists would you like the chart to display? (1-50)',
                           order='select the parameter for ordering the results (Default is `Your Top Artists`')
    async def chart_top_artists(interaction: discord.Interaction,
                                size: int,
                                order: typing.Literal['Your Top Artists', 'Artist Popularity'],
                                timeframe: typing.Literal['Short Term', 'Medium Term']):
        time_frame = timeframe.replace(' ', '_').lower()
        if size > 50 or size <= 0:
            await interaction.response.send_message('Please specify a valid size value.\n'
                                                    'Choose any integer between `1` and `50`')
        else:
            top_artists = spotify.current_user_top_artists(time_range=time_frame, limit=50)
            artist_names = [artist['name'] for artist in top_artists['items']]
            artist_popularity = [artist['popularity'] for artist in top_artists['items']]
            top_artists_dict = {'Artist': artist_names, 'Popularity': artist_popularity}
            df = pd.DataFrame(top_artists_dict)

            if order == 'Your Top Artists':
                df_top = df.head(size)
                await chart(interaction, data=df_top, timeframe=timeframe, song_or_artist='Artist')

            elif order == 'Artist Popularity':
                df_pop = df.sort_values(by='Popularity', ascending=False)
                df_pop = df_pop.head(size)
                await chart(interaction, data=df_pop, timeframe=timeframe, song_or_artist='Artist')

    @bot.tree.command(name='chart-top-songs')
    @app_commands.describe(size='how many songs would you like the chart to display? (1-50)',
                           order='select the parameter for ordering the results (Default is `Your Top Songs`')
    async def chart_top_songs(interaction: discord.Interaction,
                              size: int,
                              order: typing.Literal['Your Top Songs', 'Song Popularity'],
                              timeframe: typing.Literal['Short Term', 'Medium Term']):
        time_frame = timeframe.replace(' ', '_').lower()
        if size > 50 or size <= 0:
            await interaction.response.send_message('Please specify a valid size value.\n'
                                                    'Choose any integer between `1` and `50`')
        else:
            top_songs = spotify.current_user_top_tracks(time_range=time_frame, limit=50)
            song_names = [top_song['name'] for top_song in top_songs['items']]
            song_popularity = [top_song['popularity'] for top_song in top_songs['items']]
            top_songs_dict = {'Song': song_names, 'Popularity': song_popularity}
            df = pd.DataFrame(top_songs_dict)

            if order == 'Your Top Songs':
                df_top = df.head(size)
                await chart(interaction, data=df_top, timeframe=timeframe, song_or_artist='Song')

            elif order == 'Song Popularity':
                df_pop = df.sort_values(by='Popularity', ascending=False)
                df_pop = df_pop.head(size)
                await chart(interaction, data=df_pop, timeframe=timeframe, song_or_artist='Song')

    @bot.tree.command(name='playlist')
    async def playlist(interaction: discord.Interaction):
        await interaction.response.send_message('Here is the link to your playlist :)\n\n'
                                                'https://open.spotify.com/playlist/PLAYLIST_ID')

    @bot.tree.command(name='cover')
    @app_commands.describe(link='provide the link to the song or album you want the cover of')
    async def cover(interaction: discord.Interaction, link: typing.Optional[str]):
        if interaction.user == bot.user:
            return

        if link is None:
            track = spotify.current_playback()
            if track is None:
                await not_playing(interaction)
            else:
                album_cover = track['item']['album']['images'][0]['url']
                await interaction.response.send_message(album_cover)

        else:
            await get_cover(interaction, link)

    @bot.tree.command(name='song')
    @app_commands.describe(link='provide the link to your song')
    async def song(interaction: discord.Interaction, link: typing.Optional[str]):
        if interaction.user == bot.user:
            return

        if link is None:
            track = spotify.current_playback()
            if track is None:
                await not_playing(interaction)
            else:
                spotify_uri = track['item']['uri']
                track = spotify.track(spotify_uri)
                playlist_id = 'https://open.spotify.com/playlist/PLAYLIST_ID'
                spotify.playlist_add_items(playlist_id, items=[spotify_uri])

                image_url = f'{track['album']['images'][0]['url']}'
                embed = discord.Embed()
                embed_img = embed.set_image(url=image_url)

                await interaction.response.send_message(content=
                                                        f'Successfully added the following track to your playlist: \n\n'
                                                        f'Song:     `{track["name"]}`\n'
                                                        f'Artist:   `{track["artists"][0]["name"]}`\n\n',
                                                        embed=embed_img)

        else:
            if 'open.spotify.com/track/' in link:
                track_id = link.split('open_spotify.com/track/*?')[0].split('/track/')[1].split('?')[0]
                spotify_uri = f'spotify:track:{track_id}'
                track = spotify.track(spotify_uri)
                playlist_id = 'https://open.spotify.com/playlist/PLAYLIST_ID'
                spotify.playlist_add_items(playlist_id, items=[spotify_uri])

                image_url = f'{track['album']['images'][0]['url']}'
                embed = discord.Embed()
                embed_img = embed.set_image(url=image_url)

                await interaction.response.send_message(f'Successfully added the following track to your playlist: \n\n'
                                                        f'Song: `{track["name"]}`\n'
                                                        f'Artist: `{track["artists"][0]["name"]}`\n\n',
                                                        embed=embed_img)
            else:
                await invalid_input(interaction)

        return

    bot.run(token)
