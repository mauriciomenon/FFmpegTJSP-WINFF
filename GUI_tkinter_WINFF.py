import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import configparser

# Função para carregar configurações
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

# Função para salvar configurações
def save_config():
    config['DEFAULT'] = {
        'ffmpeg_path': ffmpeg_path_entry.get(),
        'default_format': format_var.get(),
        'default_output_dir': output_dir_entry.get(),
        'default_video_codec': video_codec_var.get(),
        'default_audio_codec': audio_codec_var.get(),
        'use_same_directory': use_same_directory_var.get()
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Função para selecionar arquivo de vídeo
def select_file():
    file_path = filedialog.askopenfilename(title="Selecione o arquivo de vídeo")
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

# Função para selecionar diretório de saída
def select_output_directory():
    directory = filedialog.askdirectory(title="Selecione o diretório de saída")
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)

# Função para selecionar o executável do FFmpeg
def select_ffmpeg_executable():
    ffmpeg_path = filedialog.askopenfilename(filetypes=[("Executáveis", "*.exe"), ("Todos os arquivos", "*.*")], title="Selecione o executável do FFmpeg")
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, ffmpeg_path)

# Função para converter vídeo
def convert_video():
    input_file = input_entry.get()
    output_format = format_var.get()
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    video_codec = video_codec_var.get()
    audio_codec = audio_codec_var.get()
    ffmpeg_path = ffmpeg_path_entry.get()

    if use_same_directory_var.get():
        output_dir = os.path.dirname(input_file)
    else:
        output_dir = output_dir_entry.get()

    if not input_file or not output_dir or not ffmpeg_path:
        messagebox.showwarning("Erro de Entrada", "Por favor, certifique-se de que todos os campos estão preenchidos.")
        return

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + output_format)

    command = f"\"{ffmpeg_path}\" -i \"{input_file}\""

    if video_bitrate:
        command += f" -b:v {video_bitrate}"

    if audio_bitrate:
        command += f" -b:a {audio_bitrate}"

    if resolution != "original":
        command += f" -s {resolution}"

    if video_codec != "auto":
        command += f" -c:v {video_codec}"

    if audio_codec != "auto":
        command += f" -c:a {audio_codec}"

    command += f" \"{output_file}\""
    
    try:
        subprocess.run(command, check=True, shell=True)
        messagebox.showinfo("Sucesso", f"Vídeo convertido para o formato {output_format} com sucesso!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro", f"Falha ao converter vídeo.\\nErro: {e}")

# Função para alternar a habilitação do campo de diretório de saída
def toggle_output_directory():
    if use_same_directory_var.get():
        output_dir_entry.config(state=tk.DISABLED)
        output_dir_button.config(state=tk.DISABLED)
    else:
        output_dir_entry.config(state=tk.NORMAL)
        output_dir_button.config(state=tk.NORMAL)

# Carregar configurações
config = load_config()

# Criar janela principal
root = tk.Tk()
root.title("Conversor de Vídeo Avançado")

# Entrada para o arquivo de vídeo
tk.Label(root, text="Selecione o Arquivo de Vídeo:").grid(row=0, column=0, padx=10, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Procurar", command=select_file).grid(row=0, column=2, padx=10, pady=5)

# Diretório de saída
tk.Label(root, text="Selecione o Diretório de Saída:").grid(row=1, column=0, padx=10, pady=5)
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.insert(0, config.get('DEFAULT', 'default_output_dir', fallback=''))
output_dir_entry.grid(row=1, column=1, padx=10, pady=5)
output_dir_button = tk.Button(root, text="Procurar", command=select_output_directory)
output_dir_button.grid(row=1, column=2, padx=10, pady=5)

# Caixa de seleção para usar o mesmo diretório do arquivo de vídeo
use_same_directory_var = tk.BooleanVar(value=config.getboolean('DEFAULT', 'use_same_directory', fallback=False))
use_same_directory_check = tk.Checkbutton(root, text="Usar o mesmo diretório do arquivo de vídeo", variable=use_same_directory_var, command=toggle_output_directory)
use_same_directory_check.grid(row=2, column=0, columnspan=3, pady=5)

# Formato de saída
tk.Label(root, text="Selecione o Formato de Saída:").grid(row=3, column=0, padx=10, pady=5)
format_var = tk.StringVar(value=config.get('DEFAULT', 'default_format', fallback='mp4'))
format_options = ["mp4", "avi", "mkv", "flv", "mov", "mp3", "wma"]
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.grid(row=3, column=1, padx=10, pady=5)

# Bitrate de vídeo
tk.Label(root, text="Bitrate de Vídeo (ex.: 1000k):").grid(row=4, column=0, padx=10, pady=5)
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=4, column=1, padx=10, pady=5)

# Bitrate de áudio
tk.Label(root, text="Bitrate de Áudio (ex.: 128k):").grid(row=5, column=0, padx=10, pady=5)
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=5, column=1, padx=10, pady=5)

# Resolução
tk.Label(root, text="Selecione a Resolução:").grid(row=6, column=0, padx=10, pady=5)
resolution_var = tk.StringVar(value="original")
resolution_options = ["original", "1920x1080", "1280x720", "640x480"]
resolution_menu = tk.OptionMenu(root, resolution_var, *resolution_options)
resolution_menu.grid(row=6, column=1, padx=10, pady=5)

# Codec de vídeo
tk.Label(root, text="Selecione o Codec de Vídeo:").grid(row=7, column=0, padx=10, pady=5)
video_codec_var = tk.StringVar(value=config.get('DEFAULT', 'default_video_codec', fallback='auto'))
video_codec_options = ["auto", "libx264", "libx265", "mpeg4"]
video_codec_menu = tk.OptionMenu(root, video_codec_var, *video_codec_options)
video_codec_menu.grid(row=7, column=1, padx=10, pady=5)

# Codec de áudio
tk.Label(root, text="Selecione o Codec de Áudio:").grid(row=8, column=0, padx=10, pady=5)
audio_codec_var = tk.StringVar(value=config.get('DEFAULT', 'default_audio_codec', fallback='auto'))
audio_codec_options = ["auto", "aac", "mp3", "ac3", "wmav2"]
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, *audio_codec_options)
audio_codec_menu.grid(row=8, column=1, padx=10, pady=5)

# Caminho do FFmpeg
tk.Label(root, text="Caminho do Executável FFmpeg:").grid(row=9, column=0, padx=10, pady=5)
ffmpeg_path_entry = tk.Entry(root, width=50)
ffmpeg_path_entry.insert(0, config.get('DEFAULT', 'ffmpeg_path', fallback='ffmpeg'))
ffmpeg_path_entry.grid(row=9, column=1, padx=10, pady=5)
tk.Button(root, text="Procurar", command=select_ffmpeg_executable).grid(row=9, column=2, padx=10, pady=5)

# Botão para converter vídeo
convert_button = tk.Button(root, text="Converter", command=convert_video)
convert_button.grid(row=11, column=0, columnspan=3, pady=20)

# Configurar estado inicial do campo de diretório de saída
toggle_output_directory()

# Salvar configurações ao sair
root.protocol("WM_DELETE_WINDOW", lambda: (save_config(), root.destroy()))

# Executar o loop principal da interface
root.mainloop()
