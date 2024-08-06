import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import configparser

# Inicializar o objeto de configuração
config = configparser.ConfigParser()

# Função para carregar configurações
def load_config(file_name):
    config.read(file_name)
    apply_saved_config()

# Função para salvar configurações
def save_config():
    config_name = simpledialog.askstring("Salvar Configuração", "Digite um nome para a configuração:")
    if config_name:
        config['DEFAULT'] = {
            'ffmpeg_path': ffmpeg_path_entry.get(),
            'default_format': format_var.get(),
            'default_output_dir': output_dir_entry.get(),
            'default_video_codec': video_codec_var.get(),
            'default_audio_codec': audio_codec_var.get(),
            'default_resolution': resolution_var.get(),
            'video_bitrate': video_bitrate_entry.get(),
            'audio_bitrate': audio_bitrate_entry.get(),
            'frame_rate': frame_rate_entry.get(),
            'audio_sample_rate': audio_sample_rate_entry.get(),
            'audio_channels': audio_channels_var.get(),
            'use_same_directory': use_same_directory_var.get()
        }
        config_file_path = os.path.join(os.getcwd(), f'{config_name}.ini')  # Salvar no diretório atual
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Configuração", f"Configuração '{config_name}' salva com sucesso em {config_file_path}!")


# Função para definir configurações padrão
def set_default_options():
    format_var.set("wmv")
    resolution_var.set("320x240")
    video_codec_var.set("wmv2")
    audio_codec_var.set("wmav2")
    video_bitrate_entry.delete(0, tk.END)
    video_bitrate_entry.insert(0, "204800")
    audio_bitrate_entry.delete(0, tk.END)
    audio_bitrate_entry.insert(0, "65536")
    frame_rate_entry.delete(0, tk.END)
    frame_rate_entry.insert(0, "20")
    audio_sample_rate_entry.delete(0, tk.END)
    audio_sample_rate_entry.insert(0, "22050")
    audio_channels_var.set("1")
    output_dir_entry.delete(0, tk.END)
    ffmpeg_path_entry.delete(0, tk.END)
    use_same_directory_var.set(False)
    update_command_display()

# Função para aplicar opções salvas
def apply_saved_config():
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, config.get('DEFAULT', 'ffmpeg_path', fallback=''))
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, config.get('DEFAULT', 'default_output_dir', fallback=''))
    format_var.set(config.get('DEFAULT', 'default_format', fallback='wmv'))
    video_codec_var.set(config.get('DEFAULT', 'default_video_codec', fallback='wmv2'))
    audio_codec_var.set(config.get('DEFAULT', 'default_audio_codec', fallback='wmav2'))
    resolution_var.set(config.get('DEFAULT', 'default_resolution', fallback='320x240'))
    video_bitrate_entry.delete(0, tk.END)
    video_bitrate_entry.insert(0, config.get('DEFAULT', 'video_bitrate', fallback='204800'))
    audio_bitrate_entry.delete(0, tk.END)
    audio_bitrate_entry.insert(0, config.get('DEFAULT', 'audio_bitrate', fallback='65536'))
    frame_rate_entry.delete(0, tk.END)
    frame_rate_entry.insert(0, config.get('DEFAULT', 'frame_rate', fallback='20'))
    audio_sample_rate_entry.delete(0, tk.END)
    audio_sample_rate_entry.insert(0, config.get('DEFAULT', 'audio_sample_rate', fallback='22050'))
    audio_channels_var.set(config.get('DEFAULT', 'audio_channels', fallback='1'))
    use_same_directory_var.set(config.getboolean('DEFAULT', 'use_same_directory', fallback=False))
    toggle_output_directory()
    update_command_display()

# Função para selecionar arquivo de vídeo
def select_file():
    file_path = filedialog.askopenfilename(title="Selecione o arquivo de vídeo")
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)
    update_command_display()

# Função para selecionar diretório de saída
def select_output_directory():
    directory = filedialog.askdirectory(title="Selecione o diretório de saída")
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)
    update_command_display()

# Função para selecionar o executável do FFmpeg
def select_ffmpeg_executable():
    ffmpeg_path = filedialog.askopenfilename(filetypes=[("Executáveis", "*.exe"), ("Todos os arquivos", "*.*")], title="Selecione FFmpeg.exe")
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, ffmpeg_path)
    update_command_display()

# Função para carregar uma configuração
def load_config_from_file():
    config_file = filedialog.askopenfilename(title="Carregar Configuração", filetypes=[("Configurações", "*.ini")])
    if config_file:
        load_config(config_file)
        messagebox.showinfo("Carregar Configuração", "Configuração carregada com sucesso!")

# Função para converter vídeo
def convert_video():
    input_file = input_entry.get()
    output_format = format_var.get()
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    video_codec = video_codec_var.get()
    audio_codec = audio_codec_var.get()
    frame_rate = frame_rate_entry.get()
    audio_sample_rate = audio_sample_rate_entry.get()
    audio_channels = audio_channels_var.get()
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
        command += f" -b {video_bitrate}"

    if audio_bitrate:
        command += f" -ab {audio_bitrate}"

    if resolution != "original":
        command += f" -s {resolution}"

    if frame_rate:
        command += f" -r {frame_rate}"

    if audio_sample_rate:
        command += f" -ar {audio_sample_rate}"

    if audio_channels:
        command += f" -ac {audio_channels}"

    if video_codec != "auto":
        command += f" -vcodec {video_codec}"

    if audio_codec != "auto":
        command += f" -acodec {audio_codec}"

    command += f" \"{output_file}\""
    
    try:
        subprocess.run(command, check=True, shell=True)
        messagebox.showinfo("Sucesso", f"Vídeo convertido para o formato {output_format} com sucesso!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Erro", f"Falha ao converter vídeo.\nErro: {e}")

# Função para atualizar a exibição do comando FFmpeg
def update_command_display():
    input_file = input_entry.get()
    output_format = format_var.get()
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    video_codec = video_codec_var.get()
    audio_codec = audio_codec_var.get()
    frame_rate = frame_rate_entry.get()
    audio_sample_rate = audio_sample_rate_entry.get()
    audio_channels = audio_channels_var.get()
    ffmpeg_path = ffmpeg_path_entry.get()

    if use_same_directory_var.get():
        output_dir = os.path.dirname(input_file)
    else:
        output_dir = output_dir_entry.get()

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + output_format)

    command = f"\"{ffmpeg_path}\" -i \"{input_file}\""

    if video_bitrate:
        command += f" -b {video_bitrate}"

    if audio_bitrate:
        command += f" -ab {audio_bitrate}"

    if resolution != "original":
        command += f" -s {resolution}"

    if frame_rate:
        command += f" -r {frame_rate}"

    if audio_sample_rate:
        command += f" -ar {audio_sample_rate}"

    if audio_channels:
        command += f" -ac {audio_channels}"

    if video_codec != "auto":
        command += f" -vcodec {video_codec}"

    if audio_codec != "auto":
        command += f" -acodec {audio_codec}"

    command += f" \"{output_file}\""
    
    command_display.delete(1.0, tk.END)
    command_display.insert(tk.END, command)

# Função para alternar a habilitação do campo de diretório de saída
def toggle_output_directory():
    if use_same_directory_var.get():
        output_dir_entry.config(state=tk.DISABLED)
        output_dir_button.config(state=tk.DISABLED)
    else:
        output_dir_entry.config(state=tk.NORMAL)
        output_dir_button.config(state=tk.NORMAL)
    update_command_display()

# Criar janela principal
root = tk.Tk()
root.title("Conversor de Vídeo Avançado")
root.geometry("750x660")  # Ajustar o tamanho da janela

# Entrada para o arquivo de vídeo
tk.Label(root, text="Selecione o Arquivo de Vídeo:").grid(row=0, column=0, padx=10, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)
input_entry.bind("<KeyRelease>", lambda event: update_command_display())
tk.Button(root, text="Procurar", command=select_file).grid(row=0, column=2, padx=10, pady=5)

# Diretório de saída
tk.Label(root, text="Selecione o Diretório de Saída:").grid(row=1, column=0, padx=10, pady=5)
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=5)
output_dir_entry.bind("<KeyRelease>", lambda event: update_command_display())
output_dir_button = tk.Button(root, text="Procurar", command=select_output_directory)
output_dir_button.grid(row=1, column=2, padx=10, pady=5)

# Caixa de seleção para usar o mesmo diretório do arquivo de vídeo
use_same_directory_var = tk.BooleanVar()
use_same_directory_check = tk.Checkbutton(root, text="Usar o mesmo diretório do arquivo de vídeo", variable=use_same_directory_var, command=toggle_output_directory)
use_same_directory_check.grid(row=2, column=0, columnspan=3, pady=5)

# Formato de saída
tk.Label(root, text="Selecione o Formato de Saída:").grid(row=3, column=0, padx=10, pady=5)
format_var = tk.StringVar()
format_menu = tk.OptionMenu(root, format_var, "mp4", "avi", "mkv", "flv", "mov", "mp3", "wmv", command=lambda _: update_command_display())
format_menu.grid(row=3, column=1, padx=10, pady=5)

# Bitrate de vídeo
tk.Label(root, text="Bitrate de Vídeo (ex.: 204800):").grid(row=4, column=0, padx=10, pady=5)
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=4, column=1, padx=10, pady=5)
video_bitrate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Bitrate de áudio
tk.Label(root, text="Bitrate de Áudio (ex.: 65536):").grid(row=5, column=0, padx=10, pady=5)
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=5, column=1, padx=10, pady=5)
audio_bitrate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Resolução
tk.Label(root, text="Selecione a Resolução:").grid(row=6, column=0, padx=10, pady=5)
resolution_var = tk.StringVar()
resolution_menu = tk.OptionMenu(root, resolution_var, "original", "1920x1080", "1280x720", "640x480", "320x240", command=lambda _: update_command_display())
resolution_menu.grid(row=6, column=1, padx=10, pady=5)

# Codec de vídeo
tk.Label(root, text="Selecione o Codec de Vídeo:").grid(row=7, column=0, padx=10, pady=5)
video_codec_var = tk.StringVar()
video_codec_menu = tk.OptionMenu(root, video_codec_var, "auto", "libx264", "libx265", "mpeg4", "wmv2", command=lambda _: update_command_display())
video_codec_menu.grid(row=7, column=1, padx=10, pady=5)

# Codec de áudio
tk.Label(root, text="Selecione o Codec de Áudio:").grid(row=8, column=0, padx=10, pady=5)
audio_codec_var = tk.StringVar()
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, "auto", "aac", "mp3", "ac3", "wmav2", command=lambda _: update_command_display())
audio_codec_menu.grid(row=8, column=1, padx=10, pady=5)

# Taxa de quadros
tk.Label(root, text="Taxa de Quadros (ex.: 20):").grid(row=9, column=0, padx=10, pady=5)
frame_rate_entry = tk.Entry(root, width=20)
frame_rate_entry.grid(row=9, column=1, padx=10, pady=5)
frame_rate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Taxa de amostragem de áudio
tk.Label(root, text="Taxa de Amostragem de Áudio (ex.: 22050):").grid(row=10, column=0, padx=10, pady=5)
audio_sample_rate_entry = tk.Entry(root, width=20)
audio_sample_rate_entry.grid(row=10, column=1, padx=10, pady=5)
audio_sample_rate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Canais de áudio
tk.Label(root, text="Canais de Áudio:").grid(row=11, column=0, padx=10, pady=5)
audio_channels_var = tk.StringVar()
audio_channels_menu = tk.OptionMenu(root, audio_channels_var, "1", "2", command=lambda _: update_command_display())
audio_channels_menu.grid(row=11, column=1, padx=10, pady=5)

# Caminho do FFmpeg
tk.Label(root, text="Caminho do Executável FFmpeg:").grid(row=12, column=0, padx=10, pady=5)
ffmpeg_path_entry = tk.Entry(root, width=50)
ffmpeg_path_entry.grid(row=12, column=1, padx=10, pady=5)
ffmpeg_path_entry.bind("<KeyRelease>", lambda event: update_command_display())
tk.Button(root, text="Procurar", command=select_ffmpeg_executable).grid(row=12, column=2, padx=10, pady=5)

# Caixa do comando do FFmpeg
tk.Label(root, text="Comando FFmpeg:").grid(row=13, column=0, padx=10, pady=5, sticky="w")
command_display = tk.Text(root, height=2, width=90, font=("TkDefaultFont", 9))
command_display.grid(row=14, column=0, columnspan=3, padx=10, pady=5)

# Botão para aplicar opções padrão
default_button = tk.Button(root, text="Opções Padrão", command=set_default_options)
default_button.grid(row=15, column=0, pady=10)

# Botão para carregar opções salvas
load_button = tk.Button(root, text="Carregar Configuração", command=load_config_from_file)
load_button.grid(row=15, column=1, pady=10)

# Botão para salvar configurações
save_button = tk.Button(root, text="Salvar Configuração", command=save_config)
save_button.grid(row=15, column=2, pady=10)

# Botão para converter vídeo
convert_button = tk.Button(root, text="Converter", command=convert_video, font=("TkDefaultFont", 10, "bold"))
convert_button.grid(row=16, column=0, columnspan=3, pady=10, ipadx=10, ipady=5)

# Aplicar configurações padrão no início, sem exibir mensagem
set_default_options()

# Executar o loop principal da interface
root.mainloop()
