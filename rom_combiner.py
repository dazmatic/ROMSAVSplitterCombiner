import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys

# --- Game ROM Combiner Constants ---
ROM_SIZE_32KB = 32 * 1024
ROM_SIZE_1MB = 1 * 1024 * 1024
ROM_SIZE_2MB = 2 * 1024 * 1024
ROM_SIZE_4MB = 4 * 1024 * 1024
ROM_SIZE_6MB = 6 * 1024 * 1024
TOTAL_ROM_SIZE_8MB = 8 * 1024 * 1024

GAME_SLOTS_4 = [
    {"start": ROM_SIZE_1MB, "max_size": ROM_SIZE_1MB, "name": "Game Slot 1 (1MB)"},
    {"start": ROM_SIZE_2MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 2 (2MB)"},
    {"start": ROM_SIZE_4MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 3 (2MB)"},
    {"start": ROM_SIZE_6MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 4 (2MB)"}
]

GAME_SLOTS_3 = [
    {"start": ROM_SIZE_2MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 1 (2MB)"},
    {"start": ROM_SIZE_4MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 2 (2MB)"},
    {"start": ROM_SIZE_6MB, "max_size": ROM_SIZE_2MB, "name": "Game Slot 3 (2MB)"}
]

MENU_FILES = {
    ("Gameboy", 3): "Daz 3in1.gb",
    ("Gameboy", 4): "Daz 4in1.gb",
    ("Gameboy Colour", 3): "Daz 3in1.gbc",
    ("Gameboy Colour", 4): "Daz 4in1.gbc",
}

# --- Save Splitter/Combiner Constants ---
CHUNK_SIZE_KB = 32
CHUNK_SIZE_BYTES = CHUNK_SIZE_KB * 1024

class MultiFunctionTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Boy Multi-Function Tool")
        
        # --- Rom Combiner Variables ---
        self.rom_combiner_menu_file_path = None
        self.rom_combiner_game_file_paths = []
        self.rom_combiner_rom_mode = tk.StringVar(value="4")
        self.rom_combiner_device_mode = tk.StringVar(value="Gameboy Colour")
        self.rom_combiner_menu_mode = tk.StringVar(value="Automatic")
        
        # --- Save Splitter/Combiner Variables ---
        self.savesplit_file_paths = []
        self.savesplit_name_entries = []
        self.savesplit_mode = tk.StringVar(value="4") # "4" or "3"

        self.setup_ui()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Create frames for each tab
        rom_combiner_frame = tk.Frame(self.notebook)
        save_splitter_frame = tk.Frame(self.notebook)

        self.notebook.add(rom_combiner_frame, text="ROM Combiner")
        self.notebook.add(save_splitter_frame, text="Save Splitter/Combiner")

        self.setup_rom_combiner_ui(rom_combiner_frame)
        self.setup_save_splitter_ui(save_splitter_frame)
        
    # -------------------------------------------------------------------------
    #                            ROM COMBINER GUI
    # -------------------------------------------------------------------------

    def setup_rom_combiner_ui(self, parent_frame):
        frame = tk.Frame(parent_frame, padx=20, pady=20)
        frame.pack()

        # Rom Type Section
        tk.Label(frame, text="1. Select ROM Type", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        rom_mode_frame = tk.Frame(frame)
        rom_mode_frame.pack()
        tk.Radiobutton(rom_mode_frame, text="4-Game ROM", variable=self.rom_combiner_rom_mode, value="4", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(rom_mode_frame, text="3-Game ROM", variable=self.rom_combiner_rom_mode, value="3", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)
        
        # Device Type Section
        tk.Label(frame, text="-"*60).pack(pady=10)
        tk.Label(frame, text="2. Select Device Type", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        device_mode_frame = tk.Frame(frame)
        device_mode_frame.pack()
        tk.Radiobutton(device_mode_frame, text="Gameboy", variable=self.rom_combiner_device_mode, value="Gameboy", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(device_mode_frame, text="Gameboy Colour", variable=self.rom_combiner_device_mode, value="Gameboy Colour", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)

        # Menu File Section
        tk.Label(frame, text="-"*60).pack(pady=10)
        tk.Label(frame, text="3. Select Menu File", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        menu_mode_frame = tk.Frame(frame)
        menu_mode_frame.pack()
        tk.Radiobutton(menu_mode_frame, text="Automatic", variable=self.rom_combiner_menu_mode, value="Automatic", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(menu_mode_frame, text="Custom", variable=self.rom_combiner_menu_mode, value="Custom", command=self.rom_combiner_update_ui).pack(side=tk.LEFT, padx=10)

        self.rom_combiner_menu_path_label = tk.Label(frame, text="No menu file selected.", bg="white", width=50, anchor="w")
        self.rom_combiner_menu_path_label.pack(pady=5)
        self.rom_combiner_select_menu_button = tk.Button(frame, text="Select Custom Menu File", command=self.select_custom_menu_file, width=40, state="disabled")
        self.rom_combiner_select_menu_button.pack(pady=5)
        
        # Game Files Section
        tk.Label(frame, text="-"*60).pack(pady=10)
        tk.Label(frame, text="4. Manage Game ROMs", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=5)
        add_game_button = tk.Button(button_frame, text="Add Game", command=self.add_game_file)
        add_game_button.pack(side=tk.LEFT, padx=5)
        remove_game_button = tk.Button(button_frame, text="Remove Selected", command=self.remove_game_file)
        remove_game_button.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame, text="Selected Games (in order of combination):").pack(pady=(5, 0))
        self.rom_combiner_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=4)
        self.rom_combiner_listbox.pack(pady=5)

        order_frame = tk.Frame(frame)
        order_frame.pack(pady=5)
        move_up_button = tk.Button(order_frame, text="Move Up", command=self.move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)
        move_down_button = tk.Button(order_frame, text="Move Down", command=self.move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)

        # Create ROM Button
        tk.Label(frame, text="-"*60).pack(pady=10)
        create_rom_button = tk.Button(frame, text="Create Multi-Game ROM", command=self.create_rom, width=40, height=2)
        create_rom_button.pack(pady=10)
        self.rom_combiner_update_ui()

    def rom_combiner_update_ui(self):
        """Updates the ROM Combiner UI based on radio button selections."""
        self.rom_combiner_update_listbox()
        if self.rom_combiner_menu_mode.get() == "Custom":
            self.rom_combiner_select_menu_button.config(state="normal")
            self.rom_combiner_menu_path_label.config(text=os.path.basename(self.rom_combiner_menu_file_path) if self.rom_combiner_menu_file_path else "No custom menu file selected.")
        else:
            self.rom_combiner_select_menu_button.config(state="disabled")
            rom_count = int(self.rom_combiner_rom_mode.get())
            device = self.rom_combiner_device_mode.get()
            menu_filename = MENU_FILES.get((device, rom_count))
            self.rom_combiner_menu_path_label.config(text=f"Automatic: {menu_filename}")

    def select_custom_menu_file(self):
        """Selects a custom menu ROM file."""
        filepath = filedialog.askopenfilename(
            title="Select Custom Menu ROM File (max 32KB)",
            filetypes=[("ROM Files", "*.gb *.gbc *.gba"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        file_size = os.path.getsize(filepath)
        if file_size > ROM_SIZE_32KB:
            messagebox.showerror("Error", f"The menu file is {file_size/1024:.2f}KB, which is larger than the 32KB limit.")
            self.rom_combiner_menu_file_path = None
            self.rom_combiner_menu_path_label.config(text="No custom menu file selected.")
            return
        
        self.rom_combiner_menu_file_path = filepath
        self.rom_combiner_menu_path_label.config(text=os.path.basename(filepath))

    def add_game_file(self):
        """Adds a single game file to the list."""
        max_games = 4 if self.rom_combiner_rom_mode.get() == "4" else 3
        if len(self.rom_combiner_game_file_paths) >= max_games:
            messagebox.showwarning("Warning", f"You can only add a maximum of {max_games} game files for the selected ROM type.")
            return

        filepath = filedialog.askopenfilename(
            title="Select a Game File",
            filetypes=[("ROM Files", "*.gb *.gbc *.gba"), ("All Files", "*.*")]
        )
        if filepath:
            self.rom_combiner_game_file_paths.append(filepath)
            self.rom_combiner_update_listbox()
            
    def remove_game_file(self):
        """Removes the selected game file from the list."""
        try:
            selected_index = self.rom_combiner_listbox.curselection()[0]
            del self.rom_combiner_game_file_paths[selected_index]
            self.rom_combiner_update_listbox()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a game to remove.")

    def move_up(self):
        """Moves the selected file up in the listbox."""
        try:
            selected_index = self.rom_combiner_listbox.curselection()[0]
            if selected_index > 0:
                self.rom_combiner_game_file_paths[selected_index], self.rom_combiner_game_file_paths[selected_index - 1] = self.rom_combiner_game_file_paths[selected_index - 1], self.rom_combiner_game_file_paths[selected_index]
                self.rom_combiner_update_listbox()
        except IndexError:
            pass

    def move_down(self):
        """Moves the selected file down in the listbox."""
        try:
            selected_index = self.rom_combiner_listbox.curselection()[0]
            if selected_index < len(self.rom_combiner_game_file_paths) - 1:
                self.rom_combiner_game_file_paths[selected_index], self.rom_combiner_game_file_paths[selected_index + 1] = self.rom_combiner_game_file_paths[selected_index + 1], self.rom_combiner_game_file_paths[selected_index]
                self.rom_combiner_update_listbox()
        except IndexError:
            pass
    
    def rom_combiner_update_listbox(self):
        """Refreshes the listbox with the current file order, highlighting files that are too large."""
        self.rom_combiner_listbox.delete(0, tk.END)
        current_slots = GAME_SLOTS_4 if self.rom_combiner_rom_mode.get() == "4" else GAME_SLOTS_3
        
        for i, path in enumerate(self.rom_combiner_game_file_paths):
            if i >= len(current_slots):
                continue
                
            slot = current_slots[i]
            
            try:
                file_size_bytes = os.path.getsize(path)
                file_size_mb = file_size_bytes / (1024 * 1024)
                display_text = f"Slot {i+1} ({slot['max_size']/1024/1024:.0f}MB): {os.path.basename(path)} ({file_size_mb:.2f}MB)"
                
                self.rom_combiner_listbox.insert(tk.END, display_text)
                
                if file_size_bytes > slot["max_size"]:
                    self.rom_combiner_listbox.itemconfig(tk.END, {'fg': 'red'})
            except OSError:
                display_text = f"Slot {i+1}: ERROR - File not found or inaccessible."
                self.rom_combiner_listbox.insert(tk.END, display_text)
                self.rom_combiner_listbox.itemconfig(tk.END, {'fg': 'red'})
        
    def create_rom(self):
        """Creates the final ROM file based on the memory map."""
        menu_filepath = None
        rom_count = int(self.rom_combiner_rom_mode.get())
        
        # Determine menu file path based on user selections
        if self.rom_combiner_menu_mode.get() == "Automatic":
            device = self.rom_combiner_device_mode.get()
            menu_filename = MENU_FILES.get((device, rom_count))
            
            # Use the directory where the script is running
            script_dir = os.path.dirname(os.path.abspath(__file__))
            menu_filepath = os.path.join(script_dir, 'menus', menu_filename)

            if not os.path.exists(menu_filepath):
                messagebox.showerror(
                    "Error", 
                    f"Could not find the automatic menu file: {menu_filename}.\n\n"
                    "Please create a folder named 'menus' in the same directory as this script "
                    "and place the file inside. Alternatively, select a custom menu file."
                )
                return
        else: # Custom menu mode
            if not self.rom_combiner_menu_file_path:
                messagebox.showerror("Error", "Please select a custom menu file.")
                return
            menu_filepath = self.rom_combiner_menu_file_path

        current_slots = GAME_SLOTS_4 if self.rom_combiner_rom_mode.get() == "4" else GAME_SLOTS_3
        
        if len(self.rom_combiner_game_file_paths) > len(current_slots):
             messagebox.showerror("Error", f"You have too many games selected for the {len(current_slots)}-game ROM configuration.")
             return
        
        # Check if any game file is too large for its slot
        for i, game_filepath in enumerate(self.rom_combiner_game_file_paths):
            slot = current_slots[i]
            try:
                file_size = os.path.getsize(game_filepath)
                if file_size > slot["max_size"]:
                    messagebox.showerror("Error", f"{os.path.basename(game_filepath)} ({file_size/1024/1024:.2f}MB) is larger than the {slot['max_size']/1024/1024}MB limit for {slot['name']}. No file will be created.")
                    return
            except OSError:
                messagebox.showerror("Error", f"Could not access game file: {os.path.basename(game_filepath)}. Please ensure the file exists and is accessible.")
                return


        output_filepath = filedialog.asksaveasfilename(
            defaultextension=".gbc",
            title="Save the combined ROM file",
            filetypes=[("ROM Files", "*.gbc"), ("All Files", "*.*")]
        )
        if not output_filepath:
            return

        try:
            # Create a byte array for the final ROM to simplify file writing
            final_rom_data = bytearray(TOTAL_ROM_SIZE_8MB)

            # Place the Menu File (first 32KB)
            with open(menu_filepath, "rb") as menu_in:
                menu_data = menu_in.read()
                final_rom_data[:len(menu_data)] = menu_data
            
            # Place the game files into their respective slots
            for i, game_filepath in enumerate(self.rom_combiner_game_file_paths):
                slot = current_slots[i]
                with open(game_filepath, "rb") as game_in:
                    game_data = game_in.read()
                    final_rom_data[slot["start"]:slot["start"] + len(game_data)] = game_data
            
            # Write the byte array to the output file
            with open(output_filepath, "wb") as f_out:
                f_out.write(final_rom_data)

            messagebox.showinfo("Success", f"Multi-game ROM created successfully at:\n{output_filepath}")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            
    # -------------------------------------------------------------------------
    #                         SAVE SPLITTER/COMBINER GUI
    # -------------------------------------------------------------------------

    def setup_save_splitter_ui(self, parent_frame):
        frame = tk.Frame(parent_frame, padx=20, pady=20)
        frame.pack()

        # Split File Section
        tk.Label(frame, text="Split a Save File", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        
        split_mode_frame = tk.Frame(frame)
        split_mode_frame.pack()
        self.savesplit_split_mode = tk.StringVar(value="4")
        tk.Radiobutton(split_mode_frame, text="4-Game Split", variable=self.savesplit_split_mode, value="4", command=self.update_split_ui).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(split_mode_frame, text="3-Game Split", variable=self.savesplit_split_mode, value="3", command=self.update_split_ui).pack(side=tk.LEFT, padx=10)

        split_frame = tk.Frame(frame)
        split_frame.pack()

        self.savesplit_name_entries = []
        default_names = [f"save{i+1}.sav" for i in range(4)]
        for i in range(4):
            entry_frame = tk.Frame(split_frame)
            entry_frame.pack(fill=tk.X, pady=2)
            tk.Label(entry_frame, text=f"File {i+1} Name:", width=15, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(entry_frame)
            entry.insert(0, default_names[i])
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.savesplit_name_entries.append(entry)

        split_button = tk.Button(frame, text="Select File to Split", command=self.split_file, width=30)
        split_button.pack(pady=10)

        tk.Label(frame, text="-"*40).pack(pady=10)
        
        # Combine Files Section
        tk.Label(frame, text="Combine Save Files", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))

        combine_mode_frame = tk.Frame(frame)
        combine_mode_frame.pack()
        self.savesplit_mode = tk.StringVar(value="4")
        tk.Radiobutton(combine_mode_frame, text="4-Save Combine", variable=self.savesplit_mode, value="4", command=self.savesplit_update_ui).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(combine_mode_frame, text="3-Save Combine", variable=self.savesplit_mode, value="3", command=self.savesplit_update_ui).pack(side=tk.LEFT, padx=10)
        
        self.select_combine_button = tk.Button(frame, text="Select 4 Files to Combine", command=self.select_files_to_combine, width=30)
        self.select_combine_button.pack(pady=5)

        self.savesplit_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=4)
        self.savesplit_listbox.pack(pady=5)

        # Re-ordering buttons frame
        order_frame = tk.Frame(frame)
        order_frame.pack(pady=5)
        move_up_button = tk.Button(order_frame, text="Move Up", command=self.savesplit_move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)
        move_down_button = tk.Button(order_frame, text="Move Down", command=self.savesplit_move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)

        combine_button = tk.Button(frame, text="Combine Files", command=self.combine_files, width=30)
        combine_button.pack(pady=10)
        
        self.savesplit_update_ui()
        self.update_split_ui()

    def update_split_ui(self):
        # Disable/enable entry fields for 3-game split
        for i in range(4):
            state = "normal"
            if self.savesplit_split_mode.get() == "3" and i == 0:
                state = "disabled"
            self.savesplit_name_entries[i].config(state=state)
            
    def savesplit_update_ui(self):
        """Updates the Save Splitter/Combiner UI based on radio button selections."""
        max_files = 4 if self.savesplit_mode.get() == "4" else 3
        self.select_combine_button.config(text=f"Select {max_files} Files to Combine")
        
        # Clear the listbox if the mode changes and file count doesn't match
        if len(self.savesplit_file_paths) != max_files:
            self.savesplit_file_paths = []
            self.savesplit_update_listbox()
        
    def split_file(self):
        """Splits a save file into individual save files based on selected mode."""
        filepath = filedialog.askopenfilename(
            title="Select 128kb file to split",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        file_size = os.path.getsize(filepath)
        if file_size != 4 * CHUNK_SIZE_BYTES:
            messagebox.showerror("Error", "The selected file is not a 128kb file. Cannot split.")
            return

        try:
            output_dir = os.path.dirname(filepath)
            output_names = [entry.get() for entry in self.savesplit_name_entries]
            
            start_index = 0
            file_count = 4
            if self.savesplit_split_mode.get() == "3":
                start_index = 1
                file_count = 3
            
            with open(filepath, "rb") as f_in:
                save_data = f_in.read()
            
            for i in range(file_count):
                data_index = i + start_index
                start_byte = data_index * CHUNK_SIZE_BYTES
                end_byte = start_byte + CHUNK_SIZE_BYTES
                data = save_data[start_byte:end_byte]
                
                filename = output_names[data_index]
                if not filename:
                    filename = f"save{data_index+1}.sav"
                
                part_filepath = os.path.join(output_dir, filename)
                with open(part_filepath, "wb") as f_out:
                    f_out.write(data)

            messagebox.showinfo("Success", f"File split successfully into {file_count} files using the names provided.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_files_to_combine(self):
        """Opens a file dialog to select files for combining and updates the listbox."""
        max_files = 4 if self.savesplit_mode.get() == "4" else 3
        file_paths = filedialog.askopenfilenames(
            title=f"Select the {max_files} save files to combine",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        if len(file_paths) != max_files:
            messagebox.showerror("Error", f"You must select exactly {max_files} files to combine.")
            return

        self.savesplit_file_paths = list(file_paths)
        self.savesplit_update_listbox()

    def savesplit_move_up(self):
        """Moves the selected file up in the list."""
        try:
            selected_index = self.savesplit_listbox.curselection()[0]
            if selected_index > 0:
                self.savesplit_file_paths[selected_index], self.savesplit_file_paths[selected_index - 1] = self.savesplit_file_paths[selected_index - 1], self.savesplit_file_paths[selected_index]
                self.savesplit_update_listbox()
        except IndexError:
            pass

    def savesplit_move_down(self):
        """Moves the selected file down in the list."""
        try:
            selected_index = self.savesplit_listbox.curselection()[0]
            if selected_index < len(self.savesplit_file_paths) - 1:
                self.savesplit_file_paths[selected_index], self.savesplit_file_paths[selected_index + 1] = self.savesplit_file_paths[selected_index + 1], self.savesplit_file_paths[selected_index]
                self.savesplit_update_listbox()
        except IndexError:
            pass

    def savesplit_update_listbox(self):
        """Refreshes the listbox with the current file order."""
        self.savesplit_listbox.delete(0, tk.END)
        for i, path in enumerate(self.savesplit_file_paths):
            self.savesplit_listbox.insert(tk.END, f"{i+1}: {os.path.basename(path)}")
        if self.savesplit_file_paths:
            self.savesplit_listbox.select_set(0)

    def combine_files(self):
        """Combines the files based on the selected mode, padding smaller files to 32kb."""
        max_files = 4 if self.savesplit_mode.get() == "4" else 3
        if len(self.savesplit_file_paths) != max_files:
            messagebox.showerror("Error", f"Please select exactly {max_files} files before combining.")
            return

        output_filepath = filedialog.asksaveasfilename(
            defaultextension=".sav",
            title="Save the combined 128kb file",
            filetypes=[("Save Files", "*.sav")]
        )
        if not output_filepath:
            return

        try:
            padded_files_count = 0
            with open(output_filepath, "wb") as f_out:
                # Add padding for 3-file mode
                if self.savesplit_mode.get() == "3":
                    f_out.write(b'\x00' * CHUNK_SIZE_BYTES)

                for filepath in self.savesplit_file_paths:
                    file_size = os.path.getsize(filepath)
                    with open(filepath, "rb") as f_in:
                        data = f_in.read()

                    if file_size < CHUNK_SIZE_BYTES:
                        padding_needed = CHUNK_SIZE_BYTES - file_size
                        data += b'\x00' * padding_needed
                        padded_files_count += 1
                        
                    f_out.write(data)
            
            success_message = f"Files combined successfully into {os.path.basename(output_filepath)}"
            if padded_files_count > 0:
                success_message += f"\n{padded_files_count} file(s) were padded to 32kb."
            
            messagebox.showinfo("Success", success_message)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = MultiFunctionTool()
    app.mainloop()
