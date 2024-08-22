    global selected_files_label
    print("Atualizando texto para:", language.get("selected_files", "Selected Files:"))

    # Destrua o label existente, se houver
    if selected_files_label is not None:
        selected_files_label.destroy()

    # Recrie o label com o novo texto
    selected_files_label = tk.Label(root, text=language.get("selected_files", "Selected Files:"), anchor="w")
    selected_files_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    # Atualize a interface para garantir que o label seja redesenhado
    root.update_idletasks()