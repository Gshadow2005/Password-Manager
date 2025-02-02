import customtkinter as ctk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import os
import sys

# Function to get the application directory
def get_app_directory():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Function to prompt the user to choose a folder for storing data 0.1
def choose_data_folder():
    app_directory = get_app_directory()
    data_folder = os.path.join(app_directory, "data 0.1")
    config_file = os.path.join(data_folder, "config.txt")

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            data_folder = file.read().strip()
            if os.path.exists(data_folder):
                return data_folder

    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    chosen_folder = filedialog.askdirectory(title="Select Folder for Data Storage")
    if chosen_folder:
        data_folder = os.path.join(chosen_folder, "data 0.1")
        os.makedirs(data_folder, exist_ok=True)
        # Make the folder hidden
        os.system(f'attrib +h "{data_folder}"')
        with open(config_file, "w") as file:
            file.write(data_folder)
    root.destroy()
    return data_folder

# Call the function to set the data_folder variable
data_folder = choose_data_folder()

# Function to create a "do not delete.txt" file in the data folder
def create_do_not_delete_file():
    file_path = os.path.join(data_folder, "DO NOT DELETE.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("All files in the data folder are important. Do not delete any of them.")

# Call the function to create the "do not delete.txt" file
create_do_not_delete_file()

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
        password_path = os.path.join(data_folder, "32653efaf9200d926226709373545aaa63e758ed.bin")
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
        password_path = os.path.join(data_folder, "32653efaf9200d926226709373545aaa63e758ed.bin")
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

    password_path = os.path.join(data_folder, "32653efaf9200d926226709373545aaa63e758ed.bin")
    if not os.path.exists(password_path):
        messagebox.showerror("Error", "Password file not found")
        return

    with open(password_path, "rb") as file:
        data = file.readlines()

    # Check for duplicated entries
    duplicate_found = any(line.strip().decode().split(" | ")[0] == website for line in data)
    if duplicate_found:
        response = messagebox.askyesno("Warning", 
                                       "Deleting a website with a duplicated or identical name will result in the removal of all such entries. Continue?")
        if not response:
            return

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
                        
- DO NOT FORGET YOUR LOGIN PASSWORD, because if you forget it, your passwords will be lost.
                        
- If you delete a duplicated website or one with the same name, the other instance will also be deleted.

- To delete a password, you need to enter the exact website name of the chosen password to delete.

- Be cautious when clicking "View Password." Ensure your screen is private, as anyone nearby can instantly see the stored password.

- It’s recommended to store the data file in the same directory as the application (exe file) to keep things organized.

- To quickly access the app, create a shortcut for the executable file (exe).

- Backup Instructions: Enable hidden files on your system to locate the data file where the app is installed. Copy and Save the file to a secure location to prevent data loss.


Terms and Conditions:
                        
- Password Management: You can securely add, view, and delete your passwords.
                        
- Account Responsibility: You are responsible for the accuracy and security of the passwords you store.
                        
- Data Deletion: Deleting a website with a duplicated or identical name will result in the removal of all such entries.
                        
- Privacy and Security: We do not store or share your passwords. Your data is only saved locally on your device.
                        

All lefts reserved. (ver 0.1)                                           
    """)

# Function to save password during sign-up
def save_signup_password(password):
    encrypted_password = encrypt_text(password)
    password_path = os.path.join(data_folder, "0cd31aeb80595a1a5f3d27951f9ab4dcee88c5f5.bin")
    with open(password_path, "wb") as file:
        file.write(encrypted_password)

# Function to load sign-up password
def load_signup_password():
    password_path = os.path.join(data_folder, "0cd31aeb80595a1a5f3d27951f9ab4dcee88c5f5.bin")
    if os.path.exists(password_path):
        with open(password_path, "rb") as file:
            encrypted_password = file.read()
        return decrypt_text(encrypted_password)
    return None

# Sign-up window
def sign_up():
    def save_credentials():
        password = entry_password.get()
        generate_key()  # Generate key during sign-up
        save_signup_password(password)
        success_label.configure(text="Credentials saved! (Don't forget them!)", text_color="green")
        sign_up_window.after(2000, lambda: [sign_up_window.destroy(), login()])

    sign_up_window = ctk.CTk()
    sign_up_window.title("Sign Up")

    # Set the size of the sign-up window
    window_width = 300
    window_height = 200

    # Get the screen width and height
    screen_width = sign_up_window.winfo_screenwidth()
    screen_height = sign_up_window.winfo_screenheight()

    # Calculate the position to center the window
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the geometry of the window
    sign_up_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Make the window not resizable
    sign_up_window.resizable(False, False)

    label_password = ctk.CTkLabel(sign_up_window, text="Enter a one-time password:")
    label_password.pack(pady=10)

    entry_password = ctk.CTkEntry(sign_up_window, show="*")
    entry_password.pack(pady=10)

    button_save = ctk.CTkButton(sign_up_window, text="Save", command=save_credentials)
    button_save.pack(pady=10)

    # Label for success or error messages
    success_label = ctk.CTkLabel(sign_up_window, text="")
    success_label.pack(pady=10)

    sign_up_window.mainloop()

# Login window
def login():
    def check_credentials():
        password = entry_password.get()
        saved_password = load_signup_password()
        if password == saved_password:
            success_label.configure(text="Success", text_color="green")
            login_window.after(2000, lambda: [login_window.destroy(), main_screen()])
        else:
            success_label.configure(text="Error: Invalid credentials", text_color="red")
            login_window.after(3500, lambda: success_label.configure(text=""))

    login_window = ctk.CTk()
    login_window.title("Login")

    # Set the size of the login window
    window_width = 300
    window_height = 200

    # Get the screen width and height
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()

    # Calculate the position to center the window
    position_x = int((screen_width / 2) - (window_width / 2))
    position_y = int((screen_height / 2) - (window_height / 2))

    # Set the geometry of the window
    login_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Make the window not resizable
    login_window.resizable(False, False)

    label_password = ctk.CTkLabel(login_window, text="Enter Password:")
    label_password.pack(pady=10)

    entry_password = ctk.CTkEntry(login_window, show="*")
    entry_password.pack(pady=10)

    button_login = ctk.CTkButton(login_window, text="Login", command=check_credentials)
    button_login.pack(pady=10)

    # Label for success or error messages
    success_label = ctk.CTkLabel(login_window, text="")
    success_label.pack(pady=10)

    login_window.mainloop()

# Main screen
def main_screen():
    # Create the main window
    global root, website_entry, username_entry, password_entry, error_label, password_text
    root = ctk.CTk()
    root.title("Password Manager")
    root.geometry("500x500")
    root.resizable(False, False)

    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the position to center the window
    position_x = int((screen_width / 2) - (500 / 2))
    position_y = int((screen_height / 2) - (500 / 2))

    # Set the geometry of the window
    root.geometry(f"500x500+{position_x}+{position_y}")

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

# Check if password file exists
if not os.path.exists(os.path.join(data_folder, "0cd31aeb80595a1a5f3d27951f9ab4dcee88c5f5.bin")):
    sign_up()
else:
    login()
