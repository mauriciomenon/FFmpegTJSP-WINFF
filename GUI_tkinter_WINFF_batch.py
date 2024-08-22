import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import configparser
import json
import threading
import platform
import requests
import zipfile
import shutil
import tempfile
import sys

# Caminho padrão em subpasta bin para o ffmpeg
def get_default_ffmpeg_path():
    if getattr(sys, 'frozen', False):  # Verifica se o programa está empacotado pelo PyInstaller
        # Se empacotado, use o diretório _MEIPASS para localizar a pasta bin
        base_path = os.path.join(sys._MEIPASS, 'bin')
    else:
        # Se não empacotado, usa a localização do script Python
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
    
    executable_name = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
    return os.path.join(base_path, executable_name)

# Inicializar o objeto de configuração
config = configparser.ConfigParser()
config_file = 'config.ini'

# Função para carregar o idioma selecionado
def load_language(lang_code):
    locales_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locales')
    try:
        with open(os.path.join(locales_folder, f"{lang_code}.json"), "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Language file {lang_code}.json not found.")
        return {}

# Carregar o idioma padrão (Português)
language = load_language("pt_br")

# Função para carregar ou criar configuração
def load_or_create_config():
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        config['DEFAULT'] = {
            'ffmpeg_path': get_default_ffmpeg_path(),
            'default_format': 'wmv',
            'default_output_dir': '',
            'default_video_codec': 'wmv2',
            'default_audio_codec': 'wmav2',
            'default_resolution': '320x240',
            'video_bitrate': '204800',
            'audio_bitrate': '65536',
            'frame_rate': '20',
            'audio_sample_rate': '22050',
            'audio_channels': '1',
            'use_same_directory': 'False',
            'overwrite_existing': 'True'
        }
        with open(config_file, 'w') as configfile:
            config.write(configfile)

load_or_create_config()

# Função para carregar configurações
def load_config(file_name):
    config.read(file_name)
    apply_saved_config()

# Função para salvar configurações
def save_config():
    config_file_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title=language["save_config"], defaultextension=".ini", filetypes=[("Arquivos INI", "*.ini")])
    if not config_file_path:
        messagebox.showwarning(language["warning"], language["no_file_selected"])
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
    messagebox.showinfo(language["config"], f"{language['config_saved']} {config_file_path}.")

# Função para carregar uma configuração
def load_config_from_file():
    config_file = filedialog.askopenfilename(title=language["load_config"], filetypes=[(language["configurations"], "*.ini")])
    if config_file:
        load_config(config_file)
        messagebox.showinfo(language["load_config"], language["config_loaded"])

# Função para definir configurações padrão
def set_default_options():
    format_var.set("asf")
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
    files = filedialog.askopenfilenames(title=language["select_files"])
    if files:
        current_files = file_list.get(0, tk.END)
        for file in files:
            if file not in current_files:
                file_list.insert(tk.END, file)
    update_command_display()

# Função para selecionar diretório de saída
def select_output_directory():
    directory = filedialog.askdirectory(title=language["output_directory"])
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)
    update_command_display()

# Função para selecionar o executável do FFmpeg
def select_ffmpeg_executable():
    ffmpeg_path = filedialog.askopenfilename(title=language["ffmpeg_path"], filetypes=[(language["executables"], "*.*")])
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, ffmpeg_path)
    config['DEFAULT']['ffmpeg_path'] = ffmpeg_path
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_command_display()

def show_installing_window(install_path):
    installing_window = tk.Toplevel(root)
    installing_window.title(language["installing"])
    installing_window.geometry("400x150")
    installing_window.resizable(False, False)
    
    tk.Label(installing_window, text=language["installing_message"]).pack(pady=10)
    tk.Label(installing_window, text=f"{language['installing_in']}: {install_path}").pack(pady=5)
    
    progress_bar = ttk.Progressbar(installing_window, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(pady=10)
    
    return installing_window, progress_bar

def download_ffmpeg():
    download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    dest_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')

    # Verificar se a pasta bin já existe
    if os.path.exists(dest_folder):
        result = messagebox.askyesno(language["confirmation"], language["bin_exists"])
        if not result:
            return

    try:
        # Criar a janela de "Instalando, aguarde..."
        installing_window, progress_bar = show_installing_window(dest_folder)

        # Criar um diretório temporário para o download
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")

        # Baixar o arquivo zip com acompanhamento de progresso
        response = requests.get(download_url, stream=True)
        total_length = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_percentage = int(100 * downloaded / total_length)
                    progress_bar['value'] = progress_percentage
                    installing_window.update()

        # Extrair o conteúdo do zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Caminho para a pasta interna dentro do ZIP
        internal_bin_path = os.path.join(temp_dir, "ffmpeg-master-latest-win64-gpl", "bin")

        # Criar a pasta /bin no diretório do programa, se não existir
        os.makedirs(dest_folder, exist_ok=True)

        # Mover o conteúdo da pasta interna /bin para a pasta /bin do programa
        for item in os.listdir(internal_bin_path):
            s = os.path.join(internal_bin_path, item)
            d = os.path.join(dest_folder, item)
            shutil.move(s, d)

        messagebox.showinfo(language["success"], f"{language['ffmpeg_installed']} {dest_folder}.")
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror(language["download_error"], f"{language['download_error_message']} {e}")
    
    except zipfile.BadZipFile:
        messagebox.showerror(language["extraction_error"], language["extraction_error_message"])

    except Exception as e:
        messagebox.showerror(language["error"], f"{language['ffmpeg_installation_error']} {e}")
    
    finally:
        # Limpar o diretório temporário
        shutil.rmtree(temp_dir)
        
        # Fechar a janela de instalação
        installing_window.destroy()

def start_download_ffmpeg():
    download_thread = threading.Thread(target=download_ffmpeg)
    download_thread.start()

import threading

def show_ffmpeg_info():
    # Subfunção para gerar mensagens de erro personalizadas
    def get_error_message(item):
        return f"{language['error_getting']} {item} {language['from_ffmpeg']}: "

    ffmpeg_path = ffmpeg_path_entry.get()
    ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe' if platform.system() == 'Darwin' else 'ffprobe.exe')

    results = {}
    
    def run_command(command, key, error_message):
        try:
            result = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW).strip()
        except Exception as e:
            result = error_message + str(e)
        results[key] = result

    # Criar e iniciar threads para cada comando
    threads = [
        threading.Thread(target=run_command, args=([ffmpeg_path, "-version"], "ffmpeg_version_output", get_error_message("versão"))),
        threading.Thread(target=run_command, args=([ffprobe_path, "-version"], "ffprobe_output", get_error_message("ffprobe"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-buildconf"], "ffmpeg_buildconf", get_error_message("configuração de build"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-codecs"], "ffmpeg_codecs", get_error_message("codecs"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-formats"], "ffmpeg_formats", get_error_message("formatos"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-protocols"], "ffmpeg_protocols", get_error_message("protocolos"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-filters"], "ffmpeg_filters", get_error_message("filtros"))),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    ffmpeg_version = results["ffmpeg_version_output"].split()[2] if "ffmpeg_version_output" in results else language["unknown"]

    version_info = (
        f"FFmpeg:\n{results.get('ffmpeg_version_output', '')}\n\n"
        f"{language['build_configuration']}:\n{results.get('ffmpeg_buildconf', '')}\n\n"
    )
    
    # Cria a janela com a versão do FFmpeg no título
    info_window = tk.Toplevel(root)
    info_window.title(f"{language['ffmpeg_info']} - {ffmpeg_version}")
    
    notebook = ttk.Notebook(info_window)
    notebook.pack(fill='both', expand=True)
    
    # Função para adicionar uma aba com um Text widget e Scrollbar
    def add_tab(title, content):
        frame = tk.Frame(notebook)
        text_widget = tk.Text(frame, wrap='word', height=40, width=100)
        text_widget.insert('end', content)
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        notebook.add(frame, text=title)

    # Adicionar abas com as informações
    add_tab(language["version_and_config"], version_info)
    add_tab(language["codecs"], results.get('ffmpeg_codecs', ''))
    add_tab(language["formats"], results.get('ffmpeg_formats', ''))
    add_tab(language["protocols"], results.get('ffmpeg_protocols', ''))
    add_tab(language["filters"], results.get('ffmpeg_filters', ''))
    add_tab("ffprobe", results.get('ffprobe_output', ''))


# Função para converter vídeos em lote
def convert_videos():
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning(language["warning"], language["no_video_selected"])
        return

    ffmpeg_path = ffmpeg_path_entry.get()
    if not os.path.exists(ffmpeg_path):
        messagebox.showerror(language["error"], language["ffmpeg_path_not_found"])
        return

    # Verificação de diretório de saída
    if not use_same_directory_var.get() and not output_dir_entry.get():
        messagebox.showerror(language["error"], language["output_directory_error"])
        return
    
    output_format = format_var.get()
    video_codec = video_codec_var.get()
    if video_codec == "wmv2":
        output_format = "asf"
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    audio_codec = audio_codec_var.get()
    frame_rate = frame_rate_entry.get()
    audio_sample_rate = audio_sample_rate_entry.get()
    audio_channels = audio_channels_var.get()

    def run_conversion():
        total_files = len(files)
        total_progress['maximum'] = total_files
        total_progress['value'] = 0

        # Criar a subpasta "Arquivos Convertidos"
        if use_same_directory_var.get():
            output_dir = os.path.dirname(files[0])
        else:
            output_dir = output_dir_entry.get()

        output_dir = os.path.join(output_dir, language["converted_files_folder"])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for index, input_file in enumerate(files):
            
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, base_name + '.' + output_format)

            if not overwrite_var.get() and os.path.exists(output_file):
                messagebox.showerror(language["error"], f"{language['file_exists_error']} '{output_file}'.")
                return

            command = [
                ffmpeg_path, '-y', '-i', input_file,
                '-b:v', video_bitrate,
                '-b:a', audio_bitrate,
                '-s', resolution,
                '-r', frame_rate,
                '-ar', audio_sample_rate,
                '-ac', audio_channels,
                '-vcodec', video_codec,
                '-acodec', audio_codec,
                output_file
            ]

            # Atualizar a exibição do nome do arquivo em conversão
            individual_progress_label.config(text=f"{language['converting']}: {os.path.basename(input_file)}")

            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                while True:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break
                    root.update_idletasks()

                process.wait()

            except Exception as e:
                messagebox.showerror(language["error"], f"{language['conversion_error']} {e}")
                return

            total_progress['value'] += 1
            root.update_idletasks()

        # Mostrar a mensagem de conclusão com o caminho completo
        success_message = f"{language['conversion_complete']}\n{language['files_saved_in']}: {output_dir}"
        result = messagebox.askyesno(language["success"], success_message + f"\n\n{language['open_folder']}?")

        if result:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            else:  # Linux ou outros
                subprocess.Popen(["xdg-open", output_dir])

    conversion_thread = threading.Thread(target=run_conversion)
    conversion_thread.start()

# Função para atualizar a exibição do comando FFmpeg
def update_command_display():
    files = file_list.get(0, tk.END)
    if not files:
        command_display.delete(1.0, tk.END)
        return

    first_file = files[0]
    output_format = format_var.get()
    video_codec = video_codec_var.get()
    if video_codec == "wmv2":
        output_format = "asf"
    else:
        output_format = format_var.get()
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    audio_codec = audio_codec_var.get()
    frame_rate = frame_rate_entry.get()
    audio_sample_rate = audio_sample_rate_entry.get()
    audio_channels = audio_channels_var.get()
    ffmpeg_path = ffmpeg_path_entry.get()

    if use_same_directory_var.get():
        output_dir = os.path.dirname(first_file)
    else:
        output_dir = output_dir_entry.get()

    output_dir = os.path.join(output_dir, language["converted_files_folder"])
    base_name = os.path.splitext(os.path.basename(first_file))[0]
    output_file = os.path.join(output_dir, base_name + '.' + output_format)

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
    messagebox.showinfo(language["about_program"], f"Mauricio Menon (+AI) \ngithub.com/mauriciomenon\nPython 3.10 + tk \n{language['version']} 9.0.0 \n22/08/2024")

# Função para exibir informações do arquivo de vídeo
def show_video_info():
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning(language["warning"], language["no_video_selected"])
        return

    ffmpeg_path = ffmpeg_path_entry.get()
    ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe' if platform.system() == 'Darwin' else 'ffprobe.exe')

    if not os.path.exists(ffprobe_path):
        if platform.system() == 'Darwin':
            messagebox.showinfo("MacOS", language["macos_download_ffmpeg"])
        else:
            messagebox.showerror(language["error"], language["ffprobe_path_not_found"])
        return

    info_window = tk.Toplevel()
    info_window.title(language["detailed_video_info"])

    # Ajustar a largura da janela secundária para ser igual à do programa principal
    window_width = root.winfo_width()
    info_window.geometry(f"{window_width}x500")  # 500 é um exemplo de altura

    notebook = ttk.Notebook(info_window)
    notebook.pack(fill='both', expand=True)

    for input_file in files:
        try:
            command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', input_file]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if process.returncode != 0:
                raise Exception(f"{language['ffprobe_error']}: {err}")

            info_data = json.loads(out)
            info_text = f"{language['file_info']}: {os.path.basename(input_file)}\n\n"
            audio_count = 0
            for stream in info_data.get('streams', []):
                if stream['codec_type'] == 'video':
                    info_text += f"{language['video_stream']}\n"
                    info_keys = ['codec_long_name', 'width', 'height', 'r_frame_rate']
                elif stream['codec_type'] == 'audio':
                    audio_count += 1
                    info_text += f"{language['audio_stream']} {audio_count}\n"
                    info_keys = ['codec_long_name', 'channels', 'sample_rate', 'bit_rate']

                for key in info_keys:
                    if key in stream:
                        value = stream[key]
                        if key == 'codec_long_name':
                            description = language["codec"]
                        elif key == 'width':
                            description = language["width"]
                            value = f"{value} {language['pixels']}"
                        elif key == 'height':
                            description = language["height"]
                            value = f"{value} {language['pixels']}"
                        elif key == 'channels':
                            description = language["channels"]
                            value = f"{value} ({language['mono'] if value == '1' else language['stereo'] if value == '2' else language['multi_channel']})"
                        elif key == 'sample_rate':
                            description = language["sample_rate"]
                            value += " Hz"
                        elif key == 'r_frame_rate':
                            description = "FPS"
                        elif key == 'bit_rate':
                            description = language["bitrate"]
                            value = f"{int(value)/1000:.2f} kbps"
                        info_text += f"{description}: {value}\n"
                info_text += "\n"

            if 'format' in info_data:
                info_text += f"{language['format_info']}\n"
                for key in ['format_name', 'duration', 'size', 'bit_rate']:
                    if key in info_data['format']:
                        value = info_data['format'][key]
                        if key == 'format_name':
                            description = language["format"]
                        elif key == 'duration':
                            description = language["duration"]
                            value = f"{float(value):.2f} {language['seconds']}"
                        elif key == 'size':
                            description = language["size"]
                            value = f"{int(value)/1024/1024:.2f} MB"
                        elif key == 'bit_rate':
                            description = language["bitrate"]
                            value = f"{int(value)/1000:.2f} kbps"
                        info_text += f"{description}: {value}\n"

            # Frame para conter o texto e a scrollbar
            frame = tk.Frame(notebook)
            frame.pack(fill='both', expand=True)

            # Adicionar um widget de texto com rolagem automática
            text_widget = tk.Text(frame, wrap='word', height=20, width=60)  # Wrap habilitado para quebrar linhas
            text_widget.insert('end', info_text)
            text_widget.config(state='normal')  # Permite edição para facilitar a cópia
            text_widget.pack(side='left', fill='both', expand=True)

            # Adicionar scrollbar
            scrollbar = tk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

            notebook.add(frame, text=os.path.basename(input_file))

        except Exception as e:
            messagebox.showerror(language["error"], f"{language['video_info_error']} {input_file}.\n{language['error']}: {str(e)}")

# Função para alternar idioma
def change_language(lang_code):
    global language
    language = load_language(lang_code)
    update_ui_language()

# Função para atualizar a interface com o novo idioma
def update_ui_language():
    root.title(language["main_window_title"])
    about_button.config(text=language["about_program"])
    info_button.config(text=language["video_info_button"])
    version_button.config(text=language["ffmpeg_version_button"])
    download_button.config(text=language["install_ffmpeg"])
    add_button.config(text=language["add_files_button"])
    remove_button.config(text=language["remove_files_button"])
    clear_button.config(text=language["clear_list_button"])
    use_same_directory_check.config(text=language["use_same_directory"])
    overwrite_check.config(text=language["overwrite_existing"])
    default_button.config(text=language["default_options"])
    load_button.config(text=language["load_config_button"])
    save_button.config(text=language["save_config_button"])
    convert_button.config(text=language["convert_button"])
    output_dir_label.config(text=language["output_directory"])
    format_label.config(text=language["output_format"])
    video_bitrate_label.config(text=language["video_bitrate"])
    audio_bitrate_label.config(text=language["audio_bitrate"])
    resolution_label.config(text=language["resolution"])
    video_codec_label.config(text=language["video_codec"])
    audio_codec_label.config(text=language["audio_codec"])
    frame_rate_label.config(text=language["frame_rate"])
    audio_sample_rate_label.config(text=language["audio_sample_rate"])
    audio_channels_label.config(text=language["audio_channels"])
    ffmpeg_path_label.config(text=language["ffmpeg_path"])
    command_label.config(text=language["ffmpeg_command"])
    language_label.config(text=language["language"])
    toggle_output_directory()

# Criar janela principal
root = tk.Tk()
root.title(language["main_window_title"])

# Ajustar o tamanho da janela com base no sistema operacional
if platform.system() == "Darwin":  # macOS
    root.geometry("1200x850")
else:  # Windows
    root.geometry("830x700")

# Frame para botões superiores
top_button_frame = tk.Frame(root)
top_button_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")

# Botões "Sobre o Programa" e "Codecs do vídeo"
about_button = tk.Button(top_button_frame, text=language["about_program"], command=show_about, font=("TkDefaultFont", 9))
about_button.pack(side="left", padx=5)
info_button = tk.Button(top_button_frame, text=language["video_info_button"], command=show_video_info, font=("TkDefaultFont", 9))
info_button.pack(side="left", padx=5)
version_button = tk.Button(top_button_frame, text=language["ffmpeg_version_button"], command=show_ffmpeg_info, font=("TkDefaultFont", 9))
version_button.pack(side="left", padx=5)
download_button = tk.Button(top_button_frame, text=language["install_ffmpeg"], command=start_download_ffmpeg, font=("TkDefaultFont", 9))
download_button.pack(side="left", padx=5)

# Adicionando o botão para troca de idioma
language_frame = tk.Frame(top_button_frame)
language_frame.pack(side="right", padx=5)

language_label = tk.Label(language_frame, text=language["language"])
language_label.pack(side="left", padx=5)

language_var = tk.StringVar(value="pt_br")
language_option_menu = tk.OptionMenu(language_frame, language_var, "pt_br", "en_us", "es_es", "it_it", "de_de", "gn_py", command=change_language)
language_option_menu.pack(side="left", padx=5)

# Label para arquivos selecionados
tk.Label(root, text=language["selected_files"]).grid(row=1, column=0, padx=5, pady=5, sticky="w")

# caixa com lista
# Frame para conter a listbox e a scrollbar
listbox_frame = tk.Frame(root)
listbox_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nswe")

# Criar uma scrollbar
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")

# Listbox com scrollbar
file_list = tk.Listbox(listbox_frame, width=80, height=8, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
file_list.pack(side="left", fill="both", expand=True)

# Configurar a scrollbar
scrollbar.config(command=file_list.yview)
scrollbar.pack(side="right", fill="y")
#final caixa com lista

# caixa botões add/remove
# Frame para botões de adicionar e remover
file_button_frame = tk.Frame(root)
file_button_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="we")

# Botões para adicionar e remover arquivos
add_button = tk.Button(file_button_frame, text=language["add_files_button"], command=select_files)
add_button.pack(side="left", padx=5)
remove_button = tk.Button(file_button_frame, text=language["remove_files_button"], command=lambda: [file_list.delete(i) for i in reversed(file_list.curselection())])
remove_button.pack(side="left", padx=5)
clear_button = tk.Button(file_button_frame, text=language["clear_list_button"], command=lambda: file_list.delete(0, tk.END))
clear_button.pack(side="left", padx=5)
# fim caixa botões add/remove

# Frame para diretório de saída
output_frame = tk.Frame(root)
output_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="we")

# Diretório de saída
output_dir_label = tk.Label(output_frame, text=language["output_directory"])
output_dir_label.pack(side="left", padx=5)
output_dir_entry = tk.Entry(output_frame, width=70)
output_dir_entry.pack(side="left", expand=True, fill="x", padx=5)
output_dir_button = tk.Button(output_frame, text=language["browse"], command=select_output_directory)
output_dir_button.pack(side="left", padx=5)

# Caixa de seleção para usar o mesmo diretório do arquivo de vídeo
use_same_directory_var = tk.BooleanVar()
use_same_directory_check = tk.Checkbutton(root, text=language["use_same_directory"], variable=use_same_directory_var, command=toggle_output_directory)
use_same_directory_check.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Checkbox para sobrescrever arquivos
overwrite_var = tk.BooleanVar()
overwrite_check = tk.Checkbutton(root, text=language["overwrite_existing"], variable=overwrite_var)
overwrite_check.grid(row=5, column=2, columnspan=2, padx=5, pady=5, sticky="w")

# Formato de saída
format_label = tk.Label(root, text=language["output_format"])
format_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
format_var = tk.StringVar()
format_menu = tk.OptionMenu(root, format_var, "mp4", "avi", "mkv", "flv", "mov", "mp3", "wmv", "asf")
format_menu.grid(row=6, column=1, padx=5, pady=5, sticky="w")

# Bitrate de vídeo
video_bitrate_label = tk.Label(root, text=language["video_bitrate"])
video_bitrate_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

# Bitrate de áudio
audio_bitrate_label = tk.Label(root, text=language["audio_bitrate"])
audio_bitrate_label.grid(row=7, column=2, padx=5, pady=5, sticky="w")
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=7, column=3, padx=5, pady=5, sticky="w")

# Resolução
resolution_label = tk.Label(root, text=language["resolution"])
resolution_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
resolution_var = tk.StringVar()
resolution_menu = tk.OptionMenu(root, resolution_var, "original", "1920x1080", "1280x720", "640x480", "320x240")
resolution_menu.grid(row=8, column=1, padx=5, pady=5, sticky="w")

# Codec de vídeo
video_codec_label = tk.Label(root, text=language["video_codec"])
video_codec_label.grid(row=8, column=2, padx=5, pady=5, sticky="w")
video_codec_var = tk.StringVar()
video_codec_menu = tk.OptionMenu(root, video_codec_var, "auto", "libx264", "libx265", "mpeg4", "wmv2")
video_codec_menu.grid(row=8, column=3, padx=5, pady=5, sticky="w")

# Codec de áudio
audio_codec_label = tk.Label(root, text=language["audio_codec"])
audio_codec_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
audio_codec_var = tk.StringVar()
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, "auto", "aac", "mp3", "ac3", "wmav2")
audio_codec_menu.grid(row=9, column=1, padx=5, pady=5, sticky="w")

# Taxa de quadros
frame_rate_label = tk.Label(root, text=language["frame_rate"])
frame_rate_label.grid(row=9, column=2, padx=5, pady=5, sticky="w")
frame_rate_entry = tk.Entry(root, width=20)
frame_rate_entry.grid(row=9, column=3, padx=5, pady=5, sticky="w")

# Taxa de amostragem de áudio
audio_sample_rate_label = tk.Label(root, text=language["audio_sample_rate"])
audio_sample_rate_label.grid(row=10, column=0, padx=5, pady=5, sticky="w")
audio_sample_rate_entry = tk.Entry(root, width=20)
audio_sample_rate_entry.grid(row=10, column=1, padx=5, pady=5, sticky="w")

# Canais de áudio
audio_channels_label = tk.Label(root, text=language["audio_channels"])
audio_channels_label.grid(row=10, column=2, padx=5, pady=5, sticky="w")
audio_channels_var = tk.StringVar()
audio_channels_menu = tk.OptionMenu(root, audio_channels_var, "1", "2")
audio_channels_menu.grid(row=10, column=3, padx=5, pady=5, sticky="w")

# Caminho do FFmpeg
ffmpeg_path_label = tk.Label(root, text=language["ffmpeg_path"])
ffmpeg_path_label.grid(row=11, column=0, padx=5, pady=5, sticky="w")
ffmpeg_path_entry = tk.Entry(root, width=70)
ffmpeg_path_entry.grid(row=11, column=1, columnspan=2, padx=5, pady=5, sticky="we")
ffmpeg_path_button = tk.Button(root, text=language["browse"], command=select_ffmpeg_executable)
ffmpeg_path_button.grid(row=11, column=3, padx=5, pady=5)

# Caixa do comando do FFmpeg
command_label = tk.Label(root, text=language["ffmpeg_command"])
command_label.grid(row=12, column=0, padx=5, pady=5, sticky="nw")
command_display = tk.Text(root, height=4, width=70, font=("TkDefaultFont", 9))
command_display.grid(row=12, column=1, columnspan=3, padx=5, pady=5, sticky="we")

# Barra de progresso total
total_progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
total_progress.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="we")

# Substituindo a barra de progresso individual pelo Label que mostra o nome do arquivo em conversão
individual_progress_label = tk.Label(root, text="", font=("TkDefaultFont", 9))
individual_progress_label.grid(row=13, column=2, columnspan=2, padx=5, pady=5, sticky="we")

# Botão para aplicar opções padrão
default_button = tk.Button(root, text=language["default_options"], command=set_default_options)
default_button.grid(row=14, column=0, padx=5, pady=5, sticky="we")

# Botão para carregar opções salvas
load_button = tk.Button(root, text=language["load_config_button"], command=load_config_from_file)
load_button.grid(row=14, column=1, padx=5, pady=5, sticky="we")

# Botão para salvar configurações
save_button = tk.Button(root, text=language["save_config_button"], command=save_config)
save_button.grid(row=14, column=2, padx=5, pady=5, sticky="we")

# Botão para converter vídeos
convert_button = tk.Button(root, text=language["convert_button"], command=convert_videos, font=("TkDefaultFont", 11, "bold"))
convert_button.grid(row=14, column=3, padx=5, pady=5, sticky="we")

# Aplicar configurações padrão no início, sem exibir mensagem
set_default_options()

# Executar o loop principal da interface
root.mainloop()
