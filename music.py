import discord
from discord.ext import commands
import youtube_dl
import asyncio


ytdl = youtube_dl.YoutubeDL()
musics = {}
Stx=""


class music (commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    class Video:
        def __init__(self, link):
            if link[0:4]=="http"or link[0:3]=="wwww":
                video = ytdl.extract_info(link, download=False)
            else:
                video = ytdl.extract_info("ytsearch:%s" % link, download=False)['entries'][0]
            video_format = video["formats"][0]
            self.url = video["webpage_url"]
            self.stream_url = video_format["url"]

    def play_song(self,client, queue, song):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
            , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
        
        def next (_):
            if len(queue) > 0:
                new_song = queue[0]
                del queue[0]
                self.play_song(client, queue, new_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)

        client.play(source, after = next)
        
    @commands.command(aliases= ['p'])
    async def play(self,ctx, *url):
        Sctx=ctx
        urla = str(" ".join(url))
        client = ctx.guild.voice_client

        if client and client.channel:
            video = self.Video(urla)
            musics[ctx.guild].append(video)
#            embed= discord.Embed(
#                title="La musique suivante à été ajoutée à la queue:",
#                description=f"{video['title']}"
#            )
#            await ctx.send (embed=embed,delete_after=10)   
        elif ctx.author.voice!=None:
            channel = ctx.author.voice.channel
            video = self.Video(urla)
            musics[ctx.guild]=[]
            client = await channel.connect()
            await ctx.send(f"Je lance : {video.url}",delete_after = 15)
            await ctx.message.delete()
            self.play_song(client, musics[ctx.guild], video)
        else:
            embed= discord.Embed(
                title=f"Utilisateur non connecté",
                description=f"{ctx.author.mention} Veuillez vous connecter à un salon vocal \n||Cette requête s'arrêtera dans 10 secondes||"
            )
            sent=await ctx.send (embed=embed,delete_after=10)     


    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("Music paused.")

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Music resumed.")        

async def setup(bot):
    await bot.add_cog(music(bot)) 