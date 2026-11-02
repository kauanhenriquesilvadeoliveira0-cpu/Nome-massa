import discord
from discord.ext import commands
import requests
from PIL import Image, ImageDraw
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

EMOJI_MAP = {
    (255, 0, 0): (239, 83, 80),     # Vermelho
    (0, 0, 255): (66, 165, 245),    # Azul
    (0, 255, 0): (102, 187, 106),   # Verde
    (255, 255, 0): (255, 238, 88),  # Amarelo
    (255, 165, 0): (255, 167, 38),  # Laranja
    (128, 0, 128): (171, 71, 188),  # Roxo
    (165, 42, 42): (141, 110, 99),   # Marrom
    (0, 0, 0): (33, 33, 33),        # Preto
    (255, 255, 255): (238, 238, 238)# Branco
}

def cor_mais_proxima(r, g, b):
    melhor_cor = (33, 33, 33)
    menor_distancia = float("inf")
    for key, val in EMOJI_MAP.items():
        dist = (r - key[0])**2 + (g - key[1])**2 + (b - key[2])**2
        if dist < menor_distancia:
            menor_distancia = dist
            melhor_cor = val
    return melhor_cor

@bot.command(name="pixel")
async def pixelize(ctx, usuario: discord.Member = None):
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
    else:
        alvo = usuario or ctx.author
        image_url = alvo.display_avatar.url

    await ctx.send("🎨 Pixelando imagem para mobile...")

    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGB")

        # Grade de pixels (ex: 32x32 para maior detalhe)
        grid_size = 32
        img_small = img.resize((grid_size, grid_size))

        # Tamanho do bloco em pixels na imagem final renderizada
        block_size = 20
        final_size = grid_size * block_size
        
        # Cria a imagem final
        out_img = Image.new("RGB", (final_size, final_size), color=(15, 15, 15))
        draw = ImageDraw.Draw(out_img)

        # Desenha cada bloco quadrado com cantos arredondados simulando os emojis
        for y in range(grid_size):
            for x in range(grid_size):
                r, g, b = img_small.getpixel((x, y))
                color = cor_mais_proxima(r, g, b)
                
                x0 = x * block_size + 1
                y0 = y * block_size + 1
                x1 = (x + 1) * block_size - 1
                y1 = (y + 1) * block_size - 1
                
                draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=color)

        # Salva em memória e envia pro Discord
        buffer = BytesIO()
        out_img.save(buffer, format="PNG")
        buffer.seek(0)

        await ctx.send(file=discord.File(buffer, filename="pixel_art.png"))

    except Exception as e:
        await ctx.send(f"❌ Erro ao processar: {e}")

import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
import random

# Armazena estado do mapa escavado atual (3x3)
mapa_terra = [[True, True, True], [True, True, True], [True, True, True]]
tesouro_x = random.randint(0, 2)
tesouro_y = random.randint(0, 2)

@bot.command(name="escavar")
async def escavar(ctx, coord: str = None):
    global mapa_terra, tesouro_x, tesouro_y

    if not coord or len(coord) < 2:
        await ctx.send("Use o formato da coordenada! Exemplo: `!escavar A1`, `!escavar B3`")
        return

    col_map = {'A': 0, 'B': 1, 'C': 2}
    col_char = coord[0].upper()
    
    try:
        x = col_map[col_char]
        y = int(coord[1]) - 1
        if y not in [0, 1, 2]: raise ValueError
    except (KeyError, ValueError):
        await ctx.send("Coordenada inválida! Use colunas A, B, C e linhas 1, 2, 3.")
        return

    # Revela o bloco escavado
    mapa_terra[y][x] = False

    # Renderiza o mapa visual
    img = Image.new("RGB", (300, 300), color=(100, 70, 40)) # Cor do tesouro/fundo
    draw = ImageDraw.Draw(img)

    # Desenha o ícone do tesouro revelado no centro do slot correto
    tx_center = tesouro_x * 100 + 50
    ty_center = tesouro_y * 100 + 50
    draw.ellipse([tx_center-30, ty_center-30, tx_center+30, ty_center+30], fill=(255, 215, 0)) # Ouro

    # Desenha os blocos de terra por cima que ainda não foram cavados
    for row in range(3):
        for col in range(3):
            if mapa_terra[row][col]:
                x0, y0 = col * 100, row * 100
                x1, y1 = x0 + 100, y0 + 100
                draw.rectangle([x0, y0, x1, y1], fill=(139, 69, 19), outline=(80, 40, 10), width=2)
                # Escreve o nome da coordenada na terra
                letras = ['A', 'B', 'C']
                draw.text((x0 + 40, y0 + 40), f"{letras[col]}{row+1}", fill=(200, 200, 200))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Checa vitória
    if x == tesouro_x and y == tesouro_y:
        await ctx.send(
            content=f"🎉 **INCRÍVEL!** {ctx.author.mention} cavou em `{col_char}{y+1}` e encontrou o **Tesouro Dourado**!",
            file=discord.File(buffer, filename="mapa.png")
        )
        # Reseta o jogo
        mapa_terra = [[True, True, True], [True, True, True], [True, True, True]]
        tesouro_x = random.randint(0, 2)
        tesouro_y = random.randint(0, 2)
    else:
        await ctx.send(
            content=f"⛏️ {ctx.author.mention} cavou em `{col_char}{y+1}`, mas só encontrou pedras...",
            file=discord.File(buffer, filename="mapa.png")
        )

import discord
from discord.ext import commands
from PIL import Image, ImageDraw
from io import BytesIO
import random
import asyncio
import math

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

silenciados = set()

# Guarda o estado do tambor por canal: {"id_do_canal": {"bala": pos_bala, "atual": pos_atual}}
tambores_canais = {}

def get_ou_cria_tambor(channel_id):
    if channel_id not in tambores_canais:
        tambores_canais[channel_id] = {
            "bala": random.randint(0, 5), # A bala fica fixa em uma das 6 câmaras
            "atual": 0                    # Começa da câmara 0
        }
    return tambores_canais[channel_id]

@bot.command(name="roleta")
async def roleta_russa(ctx):
    if ctx.author.id in silenciados:
        await ctx.send(f"👻 {ctx.author.mention}, fantasmas não atiram!", delete_after=5)
        return

    tambor = get_ou_cria_tambor(ctx.channel.id)
    pos_bala = tambor["bala"]
    pos_atual = tambor["atual"]

    # Renderiza o visual do tambor
    img = Image.new("RGB", (300, 300), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    for i in range(6):
        angle = math.radians(i * 60 - 90) # Ajusta o topo do tambor
        x = 150 + int(80 * math.cos(angle))
        y = 150 + int(80 * math.sin(angle))
        
        # Desenha a câmara atual em amarelo, o resto em cinza
        if i == pos_atual:
            color = (255, 215, 0) # Destaque para onde o gatilho bateu
        else:
            color = (60, 60, 60)
            
        draw.ellipse([x-25, y-25, x+25, y+25], fill=color, outline=(200, 200, 200), width=3)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Checa se a câmara atual bate com a bala
    disparou = (pos_atual == pos_bala)

    if disparou:
        silenciados.add(ctx.author.id)
        # Reseta o tambor do canal para a próxima rodada de jogo
        del tambores_canais[ctx.channel.id]
        
        await ctx.send(
            content=f"💥 **BANG!** A bala disparou na câmara {pos_atual + 1}! {ctx.author.mention} foi pro Além por 1 minuto! O tambor foi recarregado.",
            file=discord.File(buffer, filename="tambor.png")
        )
        await asyncio.sleep(60)
        silenciados.discard(ctx.author.id)
        await ctx.send(f"😇 {ctx.author.mention} ressuscitou do Além!")
    else:
        # Avança o tambor para o próximo jogador
        tambor["atual"] += 1
        chances_restantes = 6 - tambor["atual"]
        
        await ctx.send(
            content=f"*CLIC!* Câmara {pos_atual + 1} vazia. {ctx.author.mention} sobreviveu! (Restam {chances_restantes} câmaras no tambor)",
            file=discord.File(buffer, filename="tambor.png")
        )

import keep_alive
keep_alive.keep_alive()
import os
bot.run(os.environ.get("DISCORD_TOKEN"))
  
