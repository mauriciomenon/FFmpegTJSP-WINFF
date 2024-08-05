import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def select_file():
    file_path = filedialog.askopenfilename()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def select_output_directory():
    directory = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, directory)

def convert_video():
    input_file = input_entry.get()
    output_format = format_var.get()
    video_bitrate = video_bitrate_entry.get()
    audio_bitrate = audio_bitrate_entry.get()
    resolution = resolution_var.get()
    video_codec = video_codec_var.get()
    audio_codec = audio_codec_var.get()
    output_dir = output_dir_entry.get()

    if not input_file or not output_dir:
        messagebox.showwarning("Input Error", "Please select a video file and output directory.")
        return

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + output_format)

    command = f"ffmpeg -i \"{input_file}\""

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
        messagebox.showinfo("Success", f"Video converted to {output_format} format successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to convert video.\nError: {e}")

# Criar janela principal
root = tk.Tk()
root.title("Advanced Video Converter")

# Entrada para o arquivo de vídeo
tk.Label(root, text="Select Video File:").grid(row=0, column=0, padx=10, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=10, pady=5)

# Diretório de saída
tk.Label(root, text="Select Output Directory:").grid(row=1, column=0, padx=10, pady=5)
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_output_directory).grid(row=1, column=2, padx=10, pady=5)

# Formato de saída
tk.Label(root, text="Select Output Format:").grid(row=2, column=0, padx=10, pady=5)
format_var = tk.StringVar(value="mp4")
format_options = ["mp4", "avi", "mkv", "flv", "mov", "mp3"]
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.grid(row=2, column=1, padx=10, pady=5)

# Bitrate de vídeo
tk.Label(root, text="Video Bitrate (e.g., 1000k):").grid(row=3, column=0, padx=10, pady=5)
video_bitrate_entry = tk.Entry(root, width=20)
video_bitrate_entry.grid(row=3, column=1, padx=10, pady=5)

# Bitrate de áudio
tk.Label(root, text="Audio Bitrate (e.g., 128k):").grid(row=4, column=0, padx=10, pady=5)
audio_bitrate_entry = tk.Entry(root, width=20)
audio_bitrate_entry.grid(row=4, column=1, padx=10, pady=5)

# Resolução
tk.Label(root, text="Select Resolution:").grid(row=5, column=0, padx=10, pady=5)
resolution_var = tk.StringVar(value="original")
resolution_options = ["original", "1920x1080", "1280x720", "640x480"]
resolution_menu = tk.OptionMenu(root, resolution_var, *resolution_options)
resolution_menu.grid(row=5, column=1, padx=10, pady=5)

# Codec de vídeo
tk.Label(root, text="Select Video Codec:").grid(row=6, column=0, padx=10, pady=5)
video_codec_var = tk.StringVar(value="auto")
video_codec_options = ["auto", "libx264", "libx265", "mpeg4"]
video_codec_menu = tk.OptionMenu(root, video_codec_var, *video_codec_options)
video_codec_menu.grid(row=6, column=1, padx=10, pady=5)

# Codec de áudio
tk.Label(root, text="Select Audio Codec:").grid(row=7, column=0, padx=10, pady=5)
audio_codec_var = tk.StringVar(value="auto")
audio_codec_options = ["auto", "aac", "mp3", "ac3"]
audio_codec_menu = tk.OptionMenu(root, audio_codec_var, *audio_codec_options)
audio_codec_menu.grid(row=7, column=1, padx=10, pady=5)

# Botão para converter vídeo
convert_button = tk.Button(root, text="Convert", command=convert_video)
convert_button.grid(row=8, column=0, columnspan=3, pady=20)

# Executar o loop principal da interface
root.mainloop()
