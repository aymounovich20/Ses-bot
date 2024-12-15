import os
import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import re
import json

# Function to read existing vault content into a set for duplication checks
def read_vault():
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding="utf-8") as vault_file:
            return set(line.strip() for line in vault_file if line.strip())
    return set()

# Function to append unique chunks to vault.txt
def append_to_vault(chunks):
    existing_content = read_vault()
    new_chunks = [chunk for chunk in chunks if chunk not in existing_content]
    with open("vault.txt", "a", encoding="utf-8") as vault_file:
        for chunk in new_chunks:
            vault_file.write(chunk.strip() + "\n")
    return len(new_chunks)

# Function to process text and split into chunks
def process_text(text, max_chunk_size=1000):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < max_chunk_size:
            current_chunk += (sentence + " ").strip()
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Function to handle file uploads
def upload_file(filetype):
    filetypes = {
        "pdf": [("PDF Files", "*.pdf")],
        "txt": [("Text Files", "*.txt")],
        "json": [("JSON Files", "*.json")]
    }
    file_path = filedialog.askopenfilename(filetypes=filetypes[filetype])
    if not file_path:
        return
    
    try:
        if filetype == "pdf":
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ''.join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif filetype == "txt":
            with open(file_path, 'r', encoding="utf-8") as txt_file:
                text = txt_file.read()
        elif filetype == "json":
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
                text = json.dumps(data, ensure_ascii=False)

        chunks = process_text(text)
        added_count = append_to_vault(chunks)
        messagebox.showinfo("Success", f"Added {added_count} unique chunks to vault.txt.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to clear the vault
def clear_vault():
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all content from vault.txt?"):
        with open("vault.txt", "w", encoding="utf-8") as vault_file:
            pass
        messagebox.showinfo("Success", "Vault cleared successfully!")

# Function to display vault content
def view_vault():
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding="utf-8") as vault_file:
            content = vault_file.read()
            if content:
                messagebox.showinfo("Vault Content", content)
            else:
                messagebox.showinfo("Vault Content", "Vault is empty.")
    else:
        messagebox.showinfo("Vault Content", "Vault file does not exist.")

# Create the main window
root = tk.Tk()
root.title("Vault Manager")

# Buttons for file uploads
tk.Button(root, text="Upload PDF", command=lambda: upload_file("pdf")).pack(pady=10)
tk.Button(root, text="Upload Text File", command=lambda: upload_file("txt")).pack(pady=10)
tk.Button(root, text="Upload JSON File", command=lambda: upload_file("json")).pack(pady=10)

# Buttons for vault management
tk.Button(root, text="Clear Vault", command=clear_vault).pack(pady=10)

# Run the main event loop
root.mainloop()
