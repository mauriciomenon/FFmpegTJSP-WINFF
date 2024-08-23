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
        base_path = os.path.join(sys._MEIPASS, 'bin')
    else:
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
    config_file_path = filedialog.asksaveasfilename(initialdir=os.getcwd(), title=language.get("save_config", "Save Configuration"), defaultextension=".ini", filetypes=[("INI files", "*.ini")])
    if not config_file_path:
        messagebox.showwarning(language.get("warning", "Warning"), language.get("no_file_selected", "No file selected. Configuration not saved."))
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
    messagebox.showinfo(language.get("config", "Configuration"), f"{language.get('config_saved', 'Configuration successfully saved to')} {config_file_path}.")

# Função para carregar uma configuração
def load_config_from_file():
    config_file = filedialog.askopenfilename(title=language.get("load_config", "Load Configuration"), filetypes=[(language.get("configurations", "Configurations"), "*.ini")])
    if config_file:
        load_config(config_file)
        messagebox.showinfo(language.get("load_config", "Load Configuration"), language.get("config_loaded", "Configuration successfully loaded!"))

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
    files = filedialog.askopenfilenames(title=language.get("select_files", "Select Files"))
    if files:
        current_files = file_list.get(0, tk.END)
        for file in files:
            if file not in current_files:
                file_list.insert(tk.END, file)
    update_command_display()

# Função para selecionar diretório de saída
def select_output_directory():
    directory = filedialog.askdirectory(title=language.get("output_directory", "Output Directory"))
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)
    update_command_display()

# Função para selecionar o executável do FFmpeg
def select_ffmpeg_executable():
    ffmpeg_path = filedialog.askopenfilename(title=language.get("ffmpeg_path", "FFmpeg Path"), filetypes=[(language.get("executables", "Executables"), "*.*")])
    ffmpeg_path_entry.delete(0, tk.END)
    ffmpeg_path_entry.insert(0, ffmpeg_path)
    config['DEFAULT']['ffmpeg_path'] = ffmpeg_path
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_command_display()

def show_installing_window(install_path):
    installing_window = tk.Toplevel(root)
    installing_window.title(language.get("installing", "Installation in Progress"))
    installing_window.geometry("400x150")
    installing_window.resizable(False, False)
    
    tk.Label(installing_window, text=language.get("installing_message", "Installing FFmpeg, please wait...")).pack(pady=10)
    tk.Label(installing_window, text=f"{language.get('installing_in', 'Installing in')}: {install_path}").pack(pady=5)
    
    progress_bar = ttk.Progressbar(installing_window, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(pady=10)
    
    return installing_window, progress_bar

def download_ffmpeg():
    download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    dest_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')

    # Verificar se a pasta bin já existe
    if os.path.exists(dest_folder):
        result = messagebox.askyesno(language.get("confirmation", "Confirmation"), language.get("bin_exists", "The 'bin' folder already exists. Do you want to continue with the download and overwrite the files?"))
        if not result:
            return

    try:
        installing_window, progress_bar = show_installing_window(dest_folder)

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")

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

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        internal_bin_path = os.path.join(temp_dir, "ffmpeg-master-latest-win64-gpl", "bin")

        os.makedirs(dest_folder, exist_ok=True)

        for item in os.listdir(internal_bin_path):
            s = os.path.join(internal_bin_path, item)
            d = os.path.join(dest_folder, item)
            shutil.move(s, d)

        messagebox.showinfo(language.get("success", "Success"), f"{language.get('ffmpeg_installed', 'FFmpeg and ffprobe have been successfully downloaded and installed to')} {dest_folder}.")
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror(language.get("download_error", "Download Error"), f"{language.get('download_error_message', 'Error downloading FFmpeg. Please check your internet connection.')}\n\n{str(e)}")
    
    except zipfile.BadZipFile:
        messagebox.showerror(language.get("extraction_error", "Extraction Error"), language.get("extraction_error_message", "Error extracting the ZIP file. The file may be corrupted."))

    except Exception as e:
        messagebox.showerror(language.get("error", "Error"), f"{language.get('ffmpeg_installation_error', 'Error downloading or installing FFmpeg:')}\n\n{str(e)}")
    
    finally:
        shutil.rmtree(temp_dir)
        installing_window.destroy()

def start_download_ffmpeg():
    download_thread = threading.Thread(target=download_ffmpeg)
    download_thread.start()

import threading

def show_ffmpeg_info():
    def get_error_message(item):
        return f"{language.get('error_getting', 'Error getting')} {item} {language.get('from_ffmpeg', 'from FFmpeg')}: "

    ffmpeg_path = ffmpeg_path_entry.get()
    ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe' if platform.system() == 'Darwin' else 'ffprobe.exe')

    results = {}
    
    def run_command(command, key, error_message):
        try:
            result = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW).strip()
        except Exception as e:
            result = error_message + str(e)
        results[key] = result

    threads = [
        threading.Thread(target=run_command, args=([ffmpeg_path, "-version"], "ffmpeg_version_output", get_error_message("version"))),
        threading.Thread(target=run_command, args=([ffprobe_path, "-version"], "ffprobe_output", get_error_message("ffprobe"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-buildconf"], "ffmpeg_buildconf", get_error_message("build configuration"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-codecs"], "ffmpeg_codecs", get_error_message("codecs"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-formats"], "ffmpeg_formats", get_error_message("formats"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-protocols"], "ffmpeg_protocols", get_error_message("protocols"))),
        threading.Thread(target=run_command, args=([ffmpeg_path, "-filters"], "ffmpeg_filters", get_error_message("filters"))),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    ffmpeg_version = results.get("ffmpeg_version_output", "").split()[2] if "ffmpeg_version_output" in results else language.get("unknown", "Unknown")

    version_info = (
        f"FFmpeg:\n{results.get('ffmpeg_version_output', '')}\n\n"
        f"{language.get('build_configuration', 'FFmpeg Build Configuration')}:\n{results.get('ffmpeg_buildconf', '')}\n\n"
    )
    
    info_window = tk.Toplevel(root)
    info_window.title(f"{language.get('ffmpeg_info', 'FFmpeg Info')} - {ffmpeg_version}")
    
    notebook = ttk.Notebook(info_window)
    notebook.pack(fill='both', expand=True)
    
    def add_tab(title, content):
        frame = tk.Frame(notebook)
        text_widget = tk.Text(frame, wrap='word', height=40, width=100)
        text_widget.insert('end', content)
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        notebook.add(frame, text=title)

    add_tab(language.get("version_and_config", "Version and Configuration"), version_info)
    add_tab(language.get("codecs", "Codecs"), results.get('ffmpeg_codecs', ''))
    add_tab(language.get("formats", "Formats"), results.get('ffmpeg_formats', ''))
    add_tab(language.get("protocols", "Protocols"), results.get('ffmpeg_protocols', ''))
    add_tab(language.get("filters", "Filters"), results.get('ffmpeg_filters', ''))
    add_tab("ffprobe", results.get('ffprobe_output', ''))

def convert_videos():
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning(language.get("warning", "Warning"), language.get("no_video_selected", "No video file selected."))
        return

    ffmpeg_path = ffmpeg_path_entry.get()
    if not os.path.exists(ffmpeg_path):
        messagebox.showerror(language.get("error", "Error"), language.get("ffmpeg_path_not_found", "FFmpeg path not found. Please check if the path is correct."))
        return

    if not use_same_directory_var.get() and not output_dir_entry.get():
        messagebox.showerror(language.get("error", "Error"), language.get("output_directory_error", "Please select an output directory or check the 'Use same directory as input file' option."))
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

        if use_same_directory_var.get():
            output_dir = os.path.dirname(files[0])
        else:
            output_dir = output_dir_entry.get()

        output_dir = os.path.join(output_dir, language.get("converted_files_folder", "Converted Files"))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for index, input_file in enumerate(files):
            
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, base_name + '.' + output_format)

            if not overwrite_var.get() and os.path.exists(output_file):
                messagebox.showerror(language.get("error", "Error"), f"{language.get('file_exists_error', 'The file already exists and cannot be overwritten.')}'{output_file}'.")
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

            individual_progress_label.config(text=f"{language.get('converting', 'Converting')}: {os.path.basename(input_file)}")

            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                while True:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break
                    root.update_idletasks()

                process.wait()

            except Exception as e:
                messagebox.showerror(language.get("error", "Error"), f"{language.get('conversion_error', 'Failed to convert video.')}\n{str(e)}")
                return

            total_progress['value'] += 1
            root.update_idletasks()

        success_message = f"{language.get('conversion_complete', 'Video conversion completed.')}\n{language.get('files_saved_in', 'Files saved in:')} {output_dir}"
        result = messagebox.askyesno(language.get("success", "Success"), success_message + f"\n\n{language.get('open_folder', 'Do you want to open the folder with the converted files?')}")

        if result:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", output_dir])
            else:
                subprocess.Popen(["xdg-open", output_dir])

    conversion_thread = threading.Thread(target=run_conversion)
    conversion_thread.start()

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

    output_dir = os.path.join(output_dir, language.get("converted_files_folder", "Converted Files"))
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

def toggle_output_directory():
    if use_same_directory_var.get():
        output_dir_entry.config(state=tk.DISABLED)
        output_dir_button.config(state=tk.DISABLED)
    else:
        output_dir_entry.config(state=tk.NORMAL)
        output_dir_button.config(state=tk.NORMAL)
    update_command_display()

def show_about():
    messagebox.showinfo(language.get("about_program", "About the Program"), f"Mauricio Menon (+AI) \ngithub.com/mauriciomenon\nPython 3.10 + tk \n{language.get('version', 'Version')} 9.0.0 \n22/08/2024")

def show_video_info():
    files = file_list.get(0, tk.END)
    if not files:
        messagebox.showwarning(language.get("warning", "Warning"), language.get("no_video_selected", "No video file selected."))
        return

    ffmpeg_path = ffmpeg_path_entry.get()
    ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe' if platform.system() == 'Darwin' else 'ffprobe.exe')

    if not os.path.exists(ffprobe_path):
        if platform.system() == 'Darwin':
            messagebox.showinfo("MacOS", language.get("macos_download_ffmpeg", "Please download FFmpeg and ffprobe manually from https://evermeet.cx/ffmpeg/"))
        else:
            messagebox.showerror(language.get("error", "Error"), language.get("ffprobe_path_not_found", "ffprobe path not found. Please check if the path is correct."))
        return

    info_window = tk.Toplevel()
    info_window.title(language.get("detailed_video_info", "Detailed Video Info"))

    window_width = root.winfo_width()
    info_window.geometry(f"{window_width}x500")

    notebook = ttk.Notebook(info_window)
    notebook.pack(fill='both', expand=True)

    for input_file in files:
        try:
            command = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-show_format', input_file]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            if process.returncode != 0:
                raise Exception(f"{language.get('ffprobe_error', 'Error executing ffprobe')}: {err}")

            info_data = json.loads(out)
            info_text = f"{language.get('file_info', 'File Info')}: {os.path.basename(input_file)}\n\n"
            audio_count = 0
            for stream in info_data.get('streams', []):
                if stream['codec_type'] == 'video':
                    info_text += f"{language.get('video_stream', 'Video Stream')}\n"
                    info_keys = ['codec_long_name', 'width', 'height', 'r_frame_rate']
                elif stream['codec_type'] == 'audio':
                    audio_count += 1
                    info_text += f"{language.get('audio_stream', 'Audio Stream')} {audio_count}\n"
                    info_keys = ['codec_long_name', 'channels', 'sample_rate', 'bit_rate']

                for key in info_keys:
                    if key in stream:
                        value = stream[key]
                        if key == 'codec_long_name':
                            description = language.get("codec", "Codec")
                        elif key == 'width':
                            description = language.get("width", "Width")
                            value = f"{value} {language.get('pixels', 'pixels')}"
                        elif key == 'height':
                            description = language.get("height", "Height")
                            value = f"{value} {language.get('pixels', 'pixels')}"
                        elif key == 'channels':
                            description = language.get("channels", "Channels")
                            value = f"{value} ({language.get('mono', 'mono') if value == '1' else language.get('stereo', 'stereo') if value == '2' else language.get('multi_channel', 'multi-channel')})"
                        elif key == 'sample_rate':
                            description = language.get("sample_rate", "Sample Rate")
                            value += " Hz"
                        elif key == 'r_frame_rate':
                            description = "FPS"
                        elif key == 'bit_rate':
                            description = language.get("bitrate", "Bitrate")
                            value = f"{int(value)/1000:.2f} kbps"
                        info_text += f"{description}: {value}\n"
                info_text += "\n"

            if 'format' in info_data:
                info_text += f"{language.get('format_info', 'Format Info')}\n"
                for key in ['format_name', 'duration', 'size', 'bit_rate']:
                    if key in info_data['format']:
                        value = info_data['format'][key]
                        if key == 'format_name':
                            description = language.get("format", "Format")
                        elif key == 'duration':
                            description = language.get("duration", "Duration")
                            value = f"{float(value):.2f} {language.get('seconds', 'seconds')}"
                        elif key == 'size':
                            description = language.get("size", "Size")
                            value = f"{int(value)/1024/1024:.2f} MB"
                        elif key == 'bit_rate':
                            description = language.get("bitrate", "Bitrate")
                            value = f"{int(value)/1000:.2f} kbps"
                        info_text += f"{description}: {value}\n"

            frame = tk.Frame(notebook)
            frame.pack(fill='both', expand=True)

            text_widget = tk.Text(frame, wrap='word', height=20, width=60)
            text_widget.insert('end', info_text)
            text_widget.config(state='normal')
            text_widget.pack(side='left', fill='both', expand=True)

            scrollbar = tk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

            notebook.add(frame, text=os.path.basename(input_file))

        except Exception as e:
            messagebox.showerror(language.get("error", "Error"), f"{language.get('video_info_error', 'Could not retrieve video information')} {input_file}.\n{language.get('error', 'Error')}: {str(e)}")

def change_language(lang_code):
    global language
    language = load_language(lang_code)
    update_ui_language()

def update_ui_language():
    global selected_files_label
    print("Atualizando texto para:", language.get("selected_files", "Selected Files:"))

    # Destrua o label existente, se houver
    if selected_files_label is not None:
        selected_files_label.destroy()

    # Forçar a interface a se atualizar e garantir que o label antigo foi removido
    root.update_idletasks()

    # Recrie o label com o novo texto
    selected_files_label = tk.Label(root, text=language.get("selected_files", "Selected Files:"), anchor="w")
    selected_files_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Atualize a interface para garantir que o label seja redesenhado
    root.update_idletasks()
    
    root.title(language.get("main_window_title", "Advanced Video Converter - FFmpeg GUI"))
    about_button.config(text=language.get("about_program", "About the Program"))
    info_button.config(text=language.get("video_info_button", "Video Information"))
    version_button.config(text=language.get("ffmpeg_version_button", "FFmpeg Version"))
    download_button.config(text=language.get("install_ffmpeg", "Install FFmpeg"))
    add_button.config(text=language.get("add_files_button", "Add File(s)"))
    remove_button.config(text=language.get("remove_files_button", "Remove File(s)"))
    clear_button.config(text=language.get("clear_list_button", "Clear List"))
    use_same_directory_check.config(text=language.get("use_same_directory", "Use the same directory as the input file"))
    overwrite_check.config(text=language.get("overwrite_existing", "Overwrite existing files"))
    default_button.config(text=language.get("default_options", "Default Options"))
    load_button.config(text=language.get("load_config_button", "Load Configuration"))
    save_button.config(text=language.get("save_config_button", "Save Configuration"))
    convert_button.config(text=language.get("convert_button", "Convert"))
    
# Labels e botões de texto que não foram atualizados
    selected_files_label.config(text=language.get("selected_files", "Selected Files:"))
    output_dir_button.config(text=language.get("browse", "Browse"))
    ffmpeg_path_button.config(text=language.get("browse", "Browse"))  # Certifique-se de que este botão também seja atualizado
    
    
    output_dir_label.config(text=language.get("output_directory", "Output Directory"))
    format_label.config(text=language.get("output_format", "Output Format"))
    video_bitrate_label.config(text=language.get("video_bitrate", "Video Bitrate"))
    audio_bitrate_label.config(text=language.get("audio_bitrate", "Audio Bitrate"))
    resolution_label.config(text=language.get("resolution", "Resolution"))
    video_codec_label.config(text=language.get("video_codec", "Video Codec"))
    audio_codec_label.config(text=language.get("audio_codec", "Audio Codec"))
    frame_rate_label.config(text=language.get("frame_rate", "Frame Rate"))
    audio_sample_rate_label.config(text=language.get("audio_sample_rate", "Audio Sample Rate"))
    audio_channels_label.config(text=language.get("audio_channels", "Audio Channels"))
    ffmpeg_path_label.config(text=language.get("ffmpeg_path", "FFmpeg Path"))
    command_label.config(text=language.get("ffmpeg_command", "FFmpeg Command"))
    language_label.config(text=language.get("language", "Language"))
    toggle_output_directory()

root = tk.Tk()
root.title(language.get("main_window_title", "Advanced Video Converter - FFmpeg GUI"))

if platform.system() == "Darwin":
    root.geometry("1100x700")
else:
    root.geometry("830x700")

# Definir o label para "Arquivos Selecionados" (Selected Files)
selected_files_label = tk.Label(root, text=language.get("selected_files", "Selected Files:"))
selected_files_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

top_button_frame = tk.Frame(root)
top_button_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")

about_button = tk.Button(top_button_frame, text=language.get("about_program", "About the Program"), command=show_about, font=("TkDefaultFont", 9))
about_button.pack(side="left", padx=5)
info_button = tk.Button(top_button_frame, text=language.get("video_info_button", "Video Information"), command=show_video_info, font=("TkDefaultFont", 9))
info_button.pack(side="left", padx=5)
version_button = tk.Button(top_button_frame, text=language.get("ffmpeg_version_button", "FFmpeg Version"), command=show_ffmpeg_info, font=("TkDefaultFont", 9))
version_button.pack(side="left", padx=5)
download_button = tk.Button(top_button_frame, text=language.get("install_ffmpeg", "Install FFmpeg"), command=start_download_ffmpeg, font=("TkDefaultFont", 9))
download_button.pack(side="left", padx=5)

language_frame = tk.Frame(top_button_frame)
language_frame.pack(side="right", padx=5)

language_label = tk.Label(language_frame, text=language.get("language", "Language"))
language_label.pack(side="left", padx=5)

language_var = tk.StringVar(value="pt_br")
language_option_menu = tk.OptionMenu(language_frame, language_var, "pt_br", "en_us", "es_es", "it_it", "de_de", "gn_py", command=change_language)
language_option_menu.pack(side="left", padx=5)

tk.Label(root, text=language.get("selected_files", "Selected Files")).grid(row=1, column=0, padx=5, pady=5, sticky="w")

listbox_frame = tk.Frame(root)
listbox_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nswe")

scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")

file_list = tk.Listbox(listbox_frame, width=80, height=8, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
file_list.pack(side="left", fill="both", expand=True)

scrollbar.config(command=file_list.yview)
scrollbar.pack(side="right", fill="y")

file_button_frame = tk.Frame(root)
file_button_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="we")

add_button = tk.Button(file_button_frame, text=language.get("add_files_button", "Add File(s)"), command=select_files)
add_button.pack(side="left", padx=5)
remove_button = tk.Button(file_button_frame, text=language.get("remove_files_button", "Remove File(s)"), command=lambda: [file_list.delete(i) for i in reversed(file_list.curselection())])
remove_button.pack(side="left", padx=5)
clear_button = tk.Button(file_button_frame, text=language.get("clear_list_button", "Clear List"), command=lambda: file_list.delete(0, tk.END))
clear_button.pack(side="left", padx=5)

output_frame = tk.Frame(root)
output_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="we")

output_dir_label = tk.Label(output_frame, text=language.get("output_directory", "Output Directory"))
output_dir_label.pack(side="left", padx=5)
output_dir_entry = tk.Entry(output_frame, width=70)
output_dir_entry.pack(side="left", expand=True, fill="x", padx=5)
output_dir_button = tk.Button(output_frame, text=language.get("browse", "Browse"), command=select_output_directory)
output_dir_button.pack(side="left", padx=5)

use_same_directory_var = tk.BooleanVar()
use_same_directory_check = tk.Checkbutton(root, text=language.get("use_same_directory", "Use the same directory as the input file"), variable=use_same_directory_var, command=toggle_output_directory)
use_same_directory_check.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

overwrite_var = tk.BooleanVar()
overwrite_check = tk.Checkbutton(root, text=language.get("overwrite_existing", "Overwrite existing files"), variable=overwrite_var)
overwrite_check.grid(row=5, column=2, columnspan=2, padx=5, pady=5, sticky="w")

format_label = tk.Label(root, text=language.get("output_format", "Output Format"))
format_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
format_var = tk.StringVar()
format_menu = tk.OptionMenu(root, format_var, "mp4", "avi", "mkv", "flv", "mov", "mp3", "wmv", "asf")
format_menu.grid(row=6, column=1, padx=5, pady=5, sticky="w")

video_bitrate_label = tk.Label(root, text=language.get("video_bitrate", "Video Bitrate"))
video_bitrate_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

audio_bitrate_label = tk.Label(root, text=language.get("audio_bitrate", "Audio Bitrate"))
audio_bitrate_label.grid(row=7, column=2, padx=5, pady=5, sticky="w")
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=7, column=3, padx=5, pady=5, sticky="w")

resolution_label = tk.Label(root, text=language.get("resolution", "Resolution"))
resolution_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
resolution_var = tk.StringVar()
resolution_menu = tk.OptionMenu(root, resolution_var, "original", "1920x1080", "1280x720", "640x480", "320x240")
resolution_menu.grid(row=8, column=1, padx=5, pady=5, sticky="w")

video_codec_label = tk.Label(root, text=language.get("video_codec", "Video Codec"))
video_codec_label.grid(row=8, column=2, padx=5, pady=5, sticky="w")
video_codec_var = tk.StringVar()
video_codec_menu = tk.OptionMenu(root, video_codec_var, "auto", "libx264", "libx265", "mpeg4", "wmv2")
video_codec_menu.grid(row=8, column=3, padx=5, pady=5, sticky="w")

audio_codec_label = tk.Label(root, text=language.get("audio_codec", "Audio Codec"))
audio_codec_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
audio_codec_var = tk.StringVar()
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, "auto", "aac", "mp3", "ac3", "wmav2")
audio_codec_menu.grid(row=9, column=1, padx=5, pady=5, sticky="w")

frame_rate_label = tk.Label(root, text=language.get("frame_rate", "Frame Rate"))
frame_rate_label.grid(row=9, column=2, padx=5, pady=5, sticky="w")
frame_rate_entry = tk.Entry(root, width=20)
frame_rate_entry.grid(row=9, column=3, padx=5, pady=5, sticky="w")

audio_sample_rate_label = tk.Label(root, text=language.get("audio_sample_rate", "Audio Sample Rate"))
audio_sample_rate_label.grid(row=10, column=0, padx=5, pady=5, sticky="w")
audio_sample_rate_entry = tk.Entry(root, width=20)
audio_sample_rate_entry.grid(row=10, column=1, padx=5, pady=5, sticky="w")

audio_channels_label = tk.Label(root, text=language.get("audio_channels", "Audio Channels"))
audio_channels_label.grid(row=10, column=2, padx=5, pady=5, sticky="w")
audio_channels_var = tk.StringVar()
audio_channels_menu = tk.OptionMenu(root, audio_channels_var, "1", "2")
audio_channels_menu.grid(row=10, column=3, padx=5, pady=5, sticky="w")

ffmpeg_path_label = tk.Label(root, text=language.get("ffmpeg_path", "FFmpeg Path"))
ffmpeg_path_label.grid(row=11, column=0, padx=5, pady=5, sticky="w")
ffmpeg_path_entry = tk.Entry(root, width=70)
ffmpeg_path_entry.grid(row=11, column=1, columnspan=2, padx=5, pady=5, sticky="we")
ffmpeg_path_button = tk.Button(root, text=language.get("browse", "Browse"), command=select_ffmpeg_executable)
ffmpeg_path_button.grid(row=11, column=3, padx=5, pady=5)

command_label = tk.Label(root, text=language.get("ffmpeg_command", "FFmpeg Command"))
command_label.grid(row=12, column=0, padx=5, pady=5, sticky="nw")
command_display = tk.Text(root, height=4, width=70, font=("TkDefaultFont", 9))
command_display.grid(row=12, column=1, columnspan=3, padx=5, pady=5, sticky="we")

total_progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
total_progress.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="we")

individual_progress_label = tk.Label(root, text="", font=("TkDefaultFont", 9))
individual_progress_label.grid(row=13, column=2, columnspan=2, padx=5, pady=5, sticky="we")

default_button = tk.Button(root, text=language.get("default_options", "Default Options"), command=set_default_options)
default_button.grid(row=14, column=0, padx=5, pady=5, sticky="we")

load_button = tk.Button(root, text=language.get("load_config_button", "Load Configuration"), command=load_config_from_file)
load_button.grid(row=14, column=1, padx=5, pady=5, sticky="we")

save_button = tk.Button(root, text=language.get("save_config_button", "Save Configuration"), command=save_config)
save_button.grid(row=14, column=2, padx=5, pady=5, sticky="we")

convert_button = tk.Button(root, text=language.get("convert_button", "Convert"), command=convert_videos, font=("TkDefaultFont", 11, "bold"))
convert_button.grid(row=14, column=3, padx=5, pady=5, sticky="we")

set_default_options()
root.mainloop()

