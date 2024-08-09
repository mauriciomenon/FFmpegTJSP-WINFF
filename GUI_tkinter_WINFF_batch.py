import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import configparser
import threading
import json

# Função para obter o caminho padrão do FFmpeg
def get_default_ffmpeg_path():
    if os.name == 'nt':  # Windows
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ffmpeg.exe')
    else:  # Mac/Linux
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ffmpeg')

# Inicializar o objeto de configuração
config = configparser.ConfigParser()
config_file = 'config.ini'

# Carregar a configuração inicial se existir
if os.path.exists(config_file):
    config.read(config_file)
else:
    config['DEFAULT']['ffmpeg_path'] = get_default_ffmpeg_path()
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Função para carregar configurações
def load_config(file_name):
    config.read(file_name)
    apply_saved_config()

# Função para salvar configurações
def save_config():
    config_file_path = filedialog.asksaveasfilename(
        initialdir=os.getcwd(),
        title="Salvar Configuração",
        defaultextension=".ini",
        filetypes=[("Arquivos INI", "*.ini")]
    )
    if not config_file_path:
        messagebox.showwarning("Atenção", "Nenhum arquivo selecionado. Configuração não salva.")
        return

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
        'use_same_directory': use_same_directory_var.get(),
        'overwrite_existing': overwrite_var.get()
    }
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("Configuração", f"Configuração salva com sucesso em {config_file_path}.")

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
    ffmpeg_path_entry.insert(0, get_default_ffmpeg_path())
    use_same_directory_var.set(False)
    overwrite_var.set(True)
    update_command_display()

# Função para aplicar opções salvas
def apply_saved_config():
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, config.get('DEFAULT', 'ffmpeg_path', fallback=get_default_ffmpeg_path()))
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
    overwrite_var.set(config.getboolean('DEFAULT', 'overwrite_existing', fallback=True))
    toggle_output_directory()
    update_command_display()

# Função para selecionar arquivos de vídeo
def select_files():
    file_paths = filedialog.askopenfilenames(title="Selecione arquivos de vídeo")
    file_list.delete(0, tk.END)
    for path in file_paths:
        file_list.insert(tk.END, path)
    update_command_display()

# Função para selecionar diretório de saída
def select_output_directory():
    directory = filedialog.askdirectory(title="Selecione o diretório de saída")
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)
    update_command_display()

# Função para selecionar o executável do FFmpeg
def select_ffmpeg_executable():
    ffmpeg_path = filedialog.askopenfilename(title="Selecione FFmpeg", filetypes=[("Todos os arquivos", "*.*")])
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, ffmpeg_path)
    config['DEFAULT']['ffmpeg_path'] = ffmpeg_path
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_command_display()

# Função para carregar uma configuração
def load_config_from_file():
    config_file = filedialog.askopenfilename(title="Carregar Configuração", filetypes=[("Configurações", "*.ini")])
    if config_file:
        load_config(config_file)
        messagebox.showinfo("Carregar Configuração", "Configuração carregada com sucesso!")

# Função para converter vídeos
def convert_videos():
    files = file_list.get(0, tk.END)
    total_files = len(files)

    if total_files == 0:
        messagebox.showwarning("Atenção", "Nenhum arquivo selecionado para conversão.")
        return

    def convert_file(file, index):
        input_file = file
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

        if not overwrite_var.get() and os.path.exists(output_file):
            messagebox.showerror("Erro", f"O arquivo '{output_file}' já existe e não pode ser sobrescrito.")
            return

        command = f"\"{ffmpeg_path}\" -y -i \"{input_file}\""

        if video_bitrate:
            command += f" -b:v {video_bitrate}"

        if audio_bitrate:
            command += f" -b:a {audio_bitrate}"

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
            individual_progress['value'] = 100
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Falha ao converter {file}.\nErro: {e}")

        total_progress['value'] += 100 / total_files

    total_progress['value'] = 0
    for index, file in enumerate(files):
        individual_progress['value'] = 0
        threading.Thread(target=convert_file, args=(file, index)).start()

#
