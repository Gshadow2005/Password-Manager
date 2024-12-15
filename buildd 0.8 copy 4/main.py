import customtkinter as ctk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import os

# Define the hidden data folder path
script_directory = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(script_directory, "data")

# Create the hidden data folder if it doesn't exist
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    # Make the folder hidden
    os.system(f'attrib +h "{data_folder}"')

# Function to generate a key and save it to a hidden file
def generate_key():
    key = Fernet.generate_key()
    key_path = os.path.join(data_folder, "key.key")
    with open(key_path, "wb") as key_file:
        key_file.write(key)

# Function to load the saved key
def load_key():
    key_path = os.path.join(data_folder, "key.key")
    if os.path.exists(key_path):
        return open(key_path, "rb").read()
    else:
        messagebox.showerror("Error", "Key file not found")
        return None

# Encrypt the text
def encrypt_text(text):
    key = load_key()
    if key:
        fernet = Fernet(key)
        encrypted_text = fernet.encrypt(text.encode())
        return encrypted_text
    return None

# Decrypt the text
def decrypt_text(encrypted_text):
    key = load_key()
    if key:
        fernet = Fernet(key)
        try:
            decrypted_text = fernet.decrypt(encrypted_text).decode()
        except cryptography.fernet.InvalidToken:
            messagebox.showerror("Error", "Failed to decrypt data. The data may be corrupted or the key may be incorrect.")
            return None
        return decrypted_text
    return None

# Function to save the password
def save_password():
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if website == "" or username == "" or password == "":
        error_label.configure(text="All fields are required!", text_color="red")
        # Remove error message after 7 seconds
        root.after(7000, lambda: error_label.configure(text=""))
        return
    else:
        error_label.configure(text="")

    encrypted_username = encrypt_text(username)
    encrypted_password = encrypt_text(password)

    if encrypted_username and encrypted_password:
        password_path = os.path.join(data_folder, "passwords.bin")
        with open(password_path, "ab") as file:
            file.write(f"{website} | {encrypted_username.decode()} | {encrypted_password.decode()}\n".encode())
        error_label.configure(text="Password saved successfully!", text_color="green")
        # Remove success message after 7 seconds
        root.after(7000, lambda: error_label.configure(text=""))

        # Clear the input fields
        website_entry.delete(0, ctk.END)
        username_entry.delete(0, ctk.END)
        password_entry.delete(0, ctk.END)

        # Display the newly saved password
        view_passwords()

# Function to view the stored passwords
def view_passwords():
    try:
        password_path = os.path.join(data_folder, "passwords.bin")
        if not os.path.exists(password_path):
            messagebox.showerror("Error", "Password file not found")
            return

        with open(password_path, "rb") as file:
            data = file.readlines()

        passwords = ""
        for line in data:
            website, encrypted_username, encrypted_password = line.strip().decode().split(" | ")
            decrypted_username = decrypt_text(encrypted_username.encode())
            decrypted_password = decrypt_text(encrypted_password.encode())
            if decrypted_username is None or decrypted_password is None:
                return
            passwords += f"Website: {website}\nUsername: {decrypted_username}\nPassword: {decrypted_password}\n\n"

        # Show the stored passwords
        password_text.delete(1.0, ctk.END)
        password_text.insert(ctk.END, passwords)

    except FileNotFoundError:
        messagebox.showerror("Error", "No password data found.")

# Function to delete a specific password
def delete_password():
    website = website_entry.get().strip()
    if website == "":
        error_label.configure(text="Website field is required to delete a password!", text_color="red")
        # Remove error message after 7 seconds
        root.after(7000, lambda: error_label.configure(text=""))
        return
    else:
        error_label.configure(text="")

    password_path = os.path.join(data_folder, "passwords.bin")
    if not os.path.exists(password_path):
        messagebox.showerror("Error", "Password file not found")
        return

    with open(password_path, "rb") as file:
        data = file.readlines()

    new_data = []
    found = False
    for line in data:
        if line.strip().decode().split(" | ")[0] != website:
            new_data.append(line)
        else:
            found = True

    if not found:
        error_label.configure(text="No password found for the specified website!", text_color="red")
        # Remove error message after 7 seconds
        root.after(7000, lambda: error_label.configure(text=""))
        return

    with open(password_path, "wb") as file:
        file.writelines(new_data)

    error_label.configure(text="Password deleted successfully!", text_color="green")
    # Remove success message after 7 seconds
    root.after(7000, lambda: error_label.configure(text=""))

    # Clear the input fields
    website_entry.delete(0, ctk.END)
    username_entry.delete(0, ctk.END)
    password_entry.delete(0, ctk.END)

    # Display the updated passwords
    view_passwords()

# Function to show the help message
def show_help():
    messagebox.showinfo("Help", """
Welcome to the Password Manager! Here, you can securely save and manage your passwords.
                        

Important Notes:
                        
- If you delete a duplicated website or one with the same name, the other instance will also be deleted.

- If you want to delete a password, you need to enter the website name of the chosen password to delete.                        

- Backup Instructions: To back up your files, locate the folder where the app’s executable file (exe) is stored. Enable hidden files to see it, and then copy the file to a safe location for backup.
                        

Terms and Conditions:
                        
- Password Management: You can securely add, view, and delete your passwords.
                        
- Account Responsibility: You are responsible for the accuracy and security of the passwords you store.
                        
- Data Deletion: Deleting a website with a duplicated or identical name will result in the removal of all such entries.
                        
- Privacy and Security: We do not store or share your passwords. Your data is only saved locally on your device.
                        

                        

All lefts reserved.                                              
    """)

# Create the main window
root = ctk.CTk()
root.title("Password Manager")
root.geometry("500x500")
root.resizable(False, False)  # Disable window resizing
root.attributes("-fullscreen", False)  # Disable fullscreen

# Add the help button
help_button = ctk.CTkButton(root, text="?", width=20, height=20, command=show_help)
help_button.place(x=10, y=10)

# Check if the key file exists, if not, prompt to generate it
if not os.path.exists(os.path.join(data_folder, "key.key")):
    generate_key()

# Title and Description
title_label = ctk.CTkLabel(root, text="Password Manager", font=ctk.CTkFont(size=16, weight="bold"))
title_label.pack(pady=10)

description_label = ctk.CTkLabel(root, text="Save and view your passwords securely.")
description_label.pack()

# Frame for input fields
input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10)

website_label = ctk.CTkLabel(input_frame, text="   Website:")
website_label.grid(row=0, column=0, sticky=ctk.W)
website_entry = ctk.CTkEntry(input_frame, width=320)
website_entry.grid(row=0, column=1, padx=10, pady=5)

username_label = ctk.CTkLabel(input_frame, text="   Username:")
username_label.grid(row=1, column=0, sticky=ctk.W)
username_entry = ctk.CTkEntry(input_frame, width=320)
username_entry.grid(row=1, column=1, padx=10, pady=5)

password_label = ctk.CTkLabel(input_frame, text="   Password:")
password_label.grid(row=2, column=0, sticky=ctk.W)
password_entry = ctk.CTkEntry(input_frame, width=320, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=5)

# Checkbox to show/hide password
show_password_var = ctk.BooleanVar()
show_password_check = ctk.CTkCheckBox(input_frame, text="Show Password", variable=show_password_var,
                                      command=lambda: password_entry.configure(show='' if show_password_var.get() else '*'))
show_password_check.grid(row=3, column=1, sticky=ctk.W)

# Label for error and success messages centered
error_label = ctk.CTkLabel(input_frame, text="", text_color="red")
error_label.grid(row=4, column=0, columnspan=2, sticky=ctk.W+ctk.E)

# Buttons for saving, viewing, and deleting passwords
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

save_button = ctk.CTkButton(button_frame, text="Save Password", command=save_password)
save_button.grid(row=0, column=0, padx=5)

view_button = ctk.CTkButton(button_frame, text="View Passwords", command=view_passwords)
view_button.grid(row=0, column=1, padx=5)

delete_button = ctk.CTkButton(button_frame, text="Delete Password", command=delete_password)
delete_button.grid(row=0, column=2, padx=5)

# Frame for displaying passwords
output_frame = ctk.CTkFrame(root)
output_frame.pack(pady=10)

password_text = ctk.CTkTextbox(output_frame, height=200, width=400)
password_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

# Start the main loop
root.mainloop()
