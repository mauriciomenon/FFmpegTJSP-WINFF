# Caixa de texto para exibir o comando do FFmpeg
tk.Label(root, text="Comando FFmpeg:").grid(row=13, column=0, padx=10, pady=5, sticky="w")
command_display = tk.Text(root, height=3, width=80, font=("TkDefaultFont", 9))
command_display.grid(row=14, column=0, columnspan=3, padx=10, pady=5)