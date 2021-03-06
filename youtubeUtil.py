import youtube_dl,discord,asyncio
from functools import partial
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
ytdl.cache.remove()

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        #data = await loop.run_in_executor(None, lambda: #ytdl.extract_info(url, download=not stream))
        to_run = partial(ytdl.extract_info, url=url, download=not stream)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        data['filename'] = data['url'] if stream else ytdl.prepare_filename(data)
        return data
        #return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)