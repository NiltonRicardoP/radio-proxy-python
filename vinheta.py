from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Texto da vinheta
texto_vinheta = "Você está ouvindo... Rádio Psico rock! Onde a mente encontra o som."

# Gerar voz usando Google Text-to-Speech
tts = gTTS(texto_vinheta, lang='pt-br')
tts.save("voz.mp3")

# Carregar voz e efeito sonoro
voz = AudioSegment.from_mp3("voz.mp3")

# Música de fundo sem copyright
instrumental = AudioSegment.from_file("instrumental.mp3")

# Ajustar volume da música de fundo e da voz
instrumental = instrumental - 20
voz = voz + 5

# Combinar voz com instrumental
vinheta_final = instrumental.overlay(voz, position=1500)

# Adicionar um silêncio de 2 segundos ao final para evitar cortes
silencio = AudioSegment.silent(duration=2000)
vinheta_final_completa = vinheta_final + silencio

# Exportar a vinheta completa
vinheta_final_completa.export("vinheta_psicorock.mp3", format="mp3")

# Opcional: tocar para teste
play(vinheta_final_completa)

print("✅ Vinheta gerada com sucesso: vinheta_psicorock.mp3")
