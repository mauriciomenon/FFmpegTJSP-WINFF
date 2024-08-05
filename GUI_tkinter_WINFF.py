import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def select_file():
    file_path = filedialog.askopenfilename()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def convert_video():
    input_file = input_entry.get()
    output_format = format_var.get()

    if not input_file:
        messagebox.showwarning("Input Error", "Please select a video file.")
        return

    output_file = os.path.splitext(input_file)[0] + '.' + output_format

    command = f"ffmpeg -i \"{input_file}\" \"{output_file}\""
    
    try:
        subprocess.run(command, check=True, shell=True)
        messagebox.showinfo("Success", f"Video converted to {output_format} format successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to convert video.\nError: {e}")

# Criar janela principal
root = tk.Tk()
root.title("Simple Video Converter")

# Criar entrada para o arquivo de vídeo
tk.Label(root, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2, padx=10, pady=10)

# Criar opção de formato de saída
tk.Label(root, text="Select Output Format:").grid(row=1, column=0, padx=10, pady=10)
format_var = tk.StringVar(value="mp4")
format_options = ["mp4", "avi", "mkv", "flv", "mov"]
format_menu = tk.OptionMenu(root, format_var, *format_options)
format_menu.grid(row=1, column=1, padx=10, pady=10)

# Botão para converter vídeo
convert_button = tk.Button(root, text="Convert", command=convert_video)
convert_button.grid(row=2, column=0, columnspan=3, pady=20)

# Executar o loop principal da interface
root.mainloop()
