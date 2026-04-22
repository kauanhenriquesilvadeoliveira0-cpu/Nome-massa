import discord
from discord.ext import commands
import random
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

PLACAR_FILE = "placar.json"

def carregar_placar():
    if os.path.exists(PLACAR_FILE):
        with open(PLACAR_FILE, "r") as f:
            return json.load(f)
    return {}

def salvar_placar(placar):
    with open(PLACAR_FILE, "w") as f:
        json.dump(placar, f)

@bot.event
async def on_ready():
    print(f"Bot ligado como {bot.user}")

@bot.command()
async def duelar(ctx, oponente: discord.Member):
    if oponente == ctx.author:
        await ctx.send("Você não pode duelar contra si mesmo!")
        return
    if oponente.bot:
        await ctx.send("Você não pode duelar contra um bot!")
        return

    vencedor = random.choice([ctx.author, oponente])
    perdedor = oponente if vencedor == ctx.author else ctx.author

    placar = carregar_placar()
    vid = str(vencedor.id)
    placar[vid] = placar.get(vid, 0) + 1
    salvar_placar(placar)

    await ctx.send(f"⚔️ **{ctx.author.display_name}** vs **{oponente.display_name}**\n🏆 O vencedor é **{vencedor.display_name}**! {perdedor.display_name} foi derrotado!")

@bot.command()
async def placar(ctx):
    placar = carregar_placar()
    if not placar:
        await ctx.send("Nenhum duelo foi realizado ainda!")
        return

    top = sorted(placar.items(), key=lambda x: x[1], reverse=True)[:3]

    medals = ["🥇", "🥈", "🥉"]
    resultado = "**🏆 Top 3 Duelistas:**\n"
    for i, (uid, vitorias) in enumerate(top):
        try:
            usuario = await bot.fetch_user(int(uid))
            nome = usuario.display_name
        except:
            nome = "Usuário desconhecido"
        resultado += f"{medals[i]} **{nome}** — {vitorias} vitória(s)\n"

    await ctx.send(resultado)

bot.run("SEU_TOKEN_AQUI")
