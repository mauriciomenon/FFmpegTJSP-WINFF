import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import configparser
import threading
import json
import platform

# Inicializar o objeto de configuração
config = configparser.ConfigParser()
config_file = 'config.ini'

# Função para obter o caminho padrão do ffmpeg
def get_default_ffmpeg_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'ffmpeg.exe')

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
    config_file_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Salvar Configuração", defaultextension=".ini", filetypes=[("Arquivos INI", "*.ini")])
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

# Função para selecionar múltiplos arquivos de vídeo
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
    ffmpeg_path = filedialog.askopenfilename(filetypes=[("Todos os Arquivos", "*.*")], title="Selecione o executável FFmpeg")
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

# Função para converter vídeos em lote
def convert_videos():
    files = file_list.get(0, tk.END)
    total_files = len(files)

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

        # Verificar se o arquivo já existe e se deve sobrescrever
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
            individual_progress['value'] = (index + 1) * (100 / total_files)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Falha ao converter {input_file}.\nErro: {e}")

        # Atualizar barra de progresso total
        total_progress['value'] += 100 / total_files
    
    for index, file in enumerate(files):
        threading.Thread(target=convert_file, args=(file, index)).start()

# Função para atualizar a exibição do comando FFmpeg
def update_command_display():
    if file_list.size() == 0:
        return
    
    first_file = file_list.get(0)
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
        output_dir = os.path.dirname(first_file)
    else:
        output_dir = output_dir_entry.get()

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(first_file))[0] + '.' + output_format)

    command = f"\"{ffmpeg_path}\" -y -i \"{first_file}\""

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

# Função para exibir informações sobre o programa
def show_about():
    messagebox.showinfo("About", "Mauricio Menon (+AI) \ngithub.com/mauriciomenon\nPython 3.10 + tk \nVersão 8.3.0 \n07/08/2024")

# Função para exibir informações do arquivo de vídeo
def show_video_info():
    input_file = file_list.get(tk.ACTIVE)
    if not input_file:
        messagebox.showwarning("Atenção", "Nenhum arquivo de vídeo selecionado.")
        return

    ffmpeg_path = ffmpeg_path_entry.get()
    ffprobe_path = ffmpeg_path.replace('ffmpeg', 'ffprobe')

    if not os.path.exists(ffprobe_path):
        messagebox.showerror("Erro", "Caminho do ffprobe não encontrado. Verifique se o caminho está correto.")
        return

    try:
        command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', input_file]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            raise ffmpeg.Error('ffprobe', out, err)

        info_data = json.loads(out)
        info_text = f"Informações do Arquivo: {os.path.basename(input_file)}\n\n"
        audio_count = 0
        for stream in info_data.get('streams', []):
            if stream['codec_type'] == 'video':
                info_text += "Stream de Vídeo\n"
                info_keys = ['codec_long_name', 'display_aspect_ratio', 'width', 'height', 'r_frame_rate']
            elif stream['codec_type'] == 'audio':
                audio_count += 1
                info_text += f"Stream de Áudio {audio_count}\n"
                info_keys = ['codec_long_name', 'channels', 'sample_rate', 'bit_rate']

            for key in info_keys:
                if key in stream:
                    value = stream[key]
                    if key == 'codec_long_name':
                        description = "Codec"
                    elif key == 'display_aspect_ratio':
                        description = "Proporção de Exibição"
                    elif key == 'width':
                        description = "Largura"
                        value = f"{value} pixels"
                    elif key == 'height':
                        description = "Altura"
                        value = f"{value} pixels"
                    elif key == 'channels':
                        description = "Canais"
                        value = f"{value} ({'mono' if value == '1' else 'stereo' if value == '2' else 'multi-channel'})"
                    elif key == 'sample_rate':
                        description = "Taxa de Amostragem"
                        value += " Hz"
                    elif key == 'r_frame_rate':
                        description = "FPS"
                    elif key == 'bit_rate':
                        description = "Taxa de Bits"
                        value = f"{int(value)/1000:.2f} kbps"
                    info_text += f"{description}: {value}\n"
            info_text += "\n"

        if 'format' in info_data:
            info_text += "Informações do Formato\n"
            for key in ['format_name', 'duration', 'size', 'bit_rate']:
                if key in info_data['format']:
                    value = info_data['format'][key]
                    if key == 'format_name':
                        description = "Formato"
                    elif key == 'duration':
                        description = "Duração"
                        value = f"{float(value):.2f} segundos"
                    elif key == 'size':
                        description = "Tamanho"
                        value = f"{int(value)/1024/1024:.2f} MB"
                    elif key == 'bit_rate':
                        description = "Taxa de Bits"
                        value = f"{int(value)/1000:.2f} kbps"
                    info_text += f"{description}: {value}\n"

        # Criação da janela de informações copiáveis
        info_window = tk.Toplevel()
        info_window.title("Informações Detalhadas do Vídeo")
        text_widget = tk.Text(info_window, wrap='word', height=30, width=80)
        text_widget.insert('end', info_text)
        text_widget.pack(side='top', fill='both', expand=True)
        text_widget.config(state='normal')  # Permite edição para facilitar a cópia
        tk.Button(info_window, text="Fechar", command=info_window.destroy).pack(side='bottom')
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível obter informações do vídeo.\nErro: {str(e)}")


# Criar janela principal
root = tk.Tk()
root.title("Conversor de Vídeo Avançado")

# Ajustar o tamanho da janela com base no sistema operacional
if platform.system() == "Darwin":  # macOS
    root.geometry("1200x850")
else:  # Windows
    root.geometry("870x720")

# Entrada para o arquivo de vídeo
tk.Label(root, text="Selecione os Arquivos de Vídeo:").grid(row=0, column=0, padx=10, pady=5, sticky="n")
file_list = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
file_list.grid(row=0, column=1, padx=10, pady=5, sticky="n")
tk.Button(root, text="Adicionar Arquivos", command=select_files).grid(row=0, column=2, padx=10, pady=5)
tk.Button(root, text="Remover Arquivo", command=lambda: file_list.delete(tk.ANCHOR)).grid(row=1, column=2, padx=10, pady=5)

# Diretório de saída
tk.Label(root, text="Selecione o Diretório de Saída:").grid(row=2, column=0, padx=10, pady=5)
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=2, column=1, padx=10, pady=5)
output_dir_entry.bind("<KeyRelease>", lambda event: update_command_display())
output_dir_button = tk.Button(root, text="Procurar", command=select_output_directory)
output_dir_button.grid(row=2, column=2, padx=10, pady=5)

# Caixa de seleção para usar o mesmo diretório do arquivo de vídeo
use_same_directory_var = tk.BooleanVar()
use_same_directory_check = tk.Checkbutton(root, text="Utilizar o mesmo diretório do arquivo de entrada", variable=use_same_directory_var, command=toggle_output_directory)
use_same_directory_check.grid(row=3, column=0, pady=5)

# Checkbox para sobrescrever arquivos
overwrite_var = tk.BooleanVar()
overwrite_check = tk.Checkbutton(root, text="Sobrescrever arquivos existentes", variable=overwrite_var)
overwrite_check.grid(row=3, column=1, pady=5)

# Formato de saída
tk.Label(root, text="Selecione o Formato de Saída:").grid(row=4, column=0, padx=10, pady=5)
format_var = tk.StringVar()
format_menu = tk.OptionMenu(root, format_var, "mp4", "avi", "mkv", "flv", "mov", "mp3", "wmv", command=lambda _: update_command_display())
format_menu.grid(row=4, column=1, padx=10, pady=5)

# Bitrate de vídeo
tk.Label(root, text="Bitrate de Vídeo (ex.: 204800):").grid(row=5, column=0, padx=10, pady=5)
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=5, column=1, padx=10, pady=5)
video_bitrate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Bitrate de áudio
tk.Label(root, text="Bitrate de Áudio (ex.: 65536):").grid(row=6, column=0, padx=10, pady=5)
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=6, column=1, padx=10, pady=5)
audio_bitrate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Resolução
tk.Label(root, text="Selecione a Resolução:").grid(row=7, column=0, padx=10, pady=5)
resolution_var = tk.StringVar()
resolution_menu = tk.OptionMenu(root, resolution_var, "original", "1920x1080", "1280x720", "640x480", "320x240", command=lambda _: update_command_display())
resolution_menu.grid(row=7, column=1, padx=10, pady=5)

# Codec de vídeo
tk.Label(root, text="Selecione o Codec de Vídeo:").grid(row=8, column=0, padx=10, pady=5)
video_codec_var = tk.StringVar()
video_codec_menu = tk.OptionMenu(root, video_codec_var, "auto", "libx264", "libx265", "mpeg4", "wmv2", command=lambda _: update_command_display())
video_codec_menu.grid(row=8, column=1, padx=10, pady=5)

# Codec de áudio
tk.Label(root, text="Selecione o Codec de Áudio:").grid(row=9, column=0, padx=10, pady=5)
audio_codec_var = tk.StringVar()
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, "auto", "aac", "mp3", "ac3", "wmav2", command=lambda _: update_command_display())
audio_codec_menu.grid(row=9, column=1, padx=10, pady=5)

# Taxa de quadros
tk.Label(root, text="Taxa de Quadros (ex.: 20):").grid(row=10, column=0, padx=10, pady=5)
frame_rate_entry = tk.Entry(root, width=20)
frame_rate_entry.grid(row=10, column=1, padx=10, pady=5)
frame_rate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Taxa de amostragem de áudio
tk.Label(root, text="Taxa de Amostragem de Áudio (ex.: 22050):").grid(row=11, column=0, padx=10, pady=5)
audio_sample_rate_entry = tk.Entry(root, width=20)
audio_sample_rate_entry.grid(row=11, column=1, padx=10, pady=5)
audio_sample_rate_entry.bind("<KeyRelease>", lambda event: update_command_display())

# Canais de áudio
tk.Label(root, text="Canais de Áudio:").grid(row=12, column=0, padx=10, pady=5)
audio_channels_var = tk.StringVar()
audio_channels_menu = tk.OptionMenu(root, audio_channels_var, "1", "2", command=lambda _: update_command_display())
audio_channels_menu.grid(row=12, column=1, padx=10, pady=5)

# Caminho do FFmpeg
tk.Label(root, text="Caminho do Executável FFmpeg:").grid(row=13, column=0, padx=10, pady=5)
ffmpeg_path_entry = tk.Entry(root, width=70)  # Aumentar a largura da entrada
ffmpeg_path_entry.grid(row=13, column=1, padx=10, pady=5)
ffmpeg_path_entry.bind("<KeyRelease>", lambda event: update_command_display())
ffmpeg_path_entry.insert(0, config.get('DEFAULT', 'ffmpeg_path', fallback=get_default_ffmpeg_path()))
tk.Button(root, text="Procurar", command=select_ffmpeg_executable).grid(row=13, column=2, padx=10, pady=5)

# Caixa do comando do FFmpeg
tk.Label(root, text="Comando FFmpeg:").grid(row=14, column=0, padx=10, pady=5, sticky="w")
command_display = tk.Text(root, height=4, width=90, font=("TkDefaultFont", 9))
command_display.grid(row=15, column=0, columnspan=3, padx=10, pady=5)

# Botão para aplicar opções padrão
default_button = tk.Button(root, text="Opções Padrão", command=set_default_options)
default_button.grid(row=16, column=0, pady=10)

# Botão para carregar opções salvas
load_button = tk.Button(root, text="Carregar Configuração", command=load_config_from_file)
load_button.grid(row=16, column=1, pady=10)

# Botão para salvar configurações
save_button = tk.Button(root, text="Salvar Configuração", command=save_config)
save_button.grid(row=16, column=2, pady=10)

# Botão para converter vídeo
convert_button = tk.Button(root, text="Converter", command=convert_videos, font=("TkDefaultFont", 11, "bold"))
convert_button.grid(row=17, column=0, columnspan=3, pady=10, ipadx=10, ipady=5)

# Barras de progresso
individual_progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
individual_progress.grid(row=18, column=0, columnspan=2, pady=5)

total_progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
total_progress.grid(row=19, column=0, columnspan=2, pady=5)

# Botão "About"
about_button = tk.Button(root, text="About", command=show_about, font=("TkDefaultFont", 9))
about_button.grid(row=20, column=0, padx=10, pady=5, sticky="w")

# Botão "Info"
info_button = tk.Button(root, text="Informações do video", command=show_video_info, font=("TkDefaultFont", 9))
info_button.grid(row=20, column=2, padx=10, pady=5, sticky="e")

# Aplicar configurações padrão no início, sem exibir mensagem
set_default_options()

# Executar o loop principal da interface
root.mainloop()
