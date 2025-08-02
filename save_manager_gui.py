import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Define file sizes
CHUNK_SIZE_KB = 32
CHUNK_SIZE_BYTES = CHUNK_SIZE_KB * 1024

class SaveFileManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Save File Manager")
        self.file_paths = []
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack()

        # Split File Section
        tk.Label(frame, text="Split a 128kb Save File", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        
        split_frame = tk.Frame(frame)
        split_frame.pack()

        self.name_entries = []
        default_names = [f"save{i+1}.sav" for i in range(4)]
        for i in range(4):
            entry_frame = tk.Frame(split_frame)
            entry_frame.pack(fill=tk.X, pady=2)
            tk.Label(entry_frame, text=f"File {i+1} Name:", width=15, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(entry_frame)
            entry.insert(0, default_names[i])
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.name_entries.append(entry)

        split_button = tk.Button(frame, text="Select File to Split", command=self.split_file, width=30)
        split_button.pack(pady=10)

        tk.Label(frame, text="-"*40).pack(pady=10)

        # Combine Files Section
        tk.Label(frame, text="Combine four 32kb Save Files", font=("Helvetica", 12, "bold")).pack(pady=(0, 5))
        select_combine_button = tk.Button(frame, text="Select 4 Files to Combine", command=self.select_files_to_combine, width=30)
        select_combine_button.pack(pady=5)

        # Listbox for re-ordering
        self.listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=4)
        self.listbox.pack(pady=5)

        # Re-ordering buttons frame
        order_frame = tk.Frame(frame)
        order_frame.pack(pady=5)
        move_up_button = tk.Button(order_frame, text="Move Up", command=self.move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)
        move_down_button = tk.Button(order_frame, text="Move Down", command=self.move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)

        combine_button = tk.Button(frame, text="Combine Files", command=self.combine_files, width=30)
        combine_button.pack(pady=10)

    def split_file(self):
        """Splits a 128kb file into four 32kb files using user-defined names."""
        filepath = filedialog.askopenfilename(
            title="Select 128kb file to split",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            output_dir = os.path.dirname(filepath)
            output_names = [entry.get() for entry in self.name_entries]
            
            with open(filepath, "rb") as f_in:
                for i in range(4):
                    data = f_in.read(CHUNK_SIZE_BYTES)
                    if not data:
                        break
                    
                    filename = output_names[i]
                    if not filename:
                        filename = f"save{i+1}.sav"
                    
                    part_filepath = os.path.join(output_dir, filename)
                    with open(part_filepath, "wb") as f_out:
                        f_out.write(data)

            messagebox.showinfo("Success", "File split successfully using the names provided.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_files_to_combine(self):
        """Opens a file dialog to select four 32kb files and updates the listbox."""
        file_paths = filedialog.askopenfilenames(
            title="Select the four 32kb save files",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        if len(file_paths) != 4:
            messagebox.showerror("Error", "You must select exactly four files to combine.")
            return

        self.file_paths = list(file_paths)
        self.listbox.delete(0, tk.END)
        for i, path in enumerate(self.file_paths):
            self.listbox.insert(tk.END, f"{i+1}: {os.path.basename(path)}")

    def move_up(self):
        """Moves the selected file up in the list."""
        try:
            selected_index = self.listbox.curselection()[0]
            if selected_index > 0:
                self.file_paths[selected_index], self.file_paths[selected_index - 1] = self.file_paths[selected_index - 1], self.file_paths[selected_index]
                self.update_listbox()
        except IndexError:
            pass

    def move_down(self):
        """Moves the selected file down in the list."""
        try:
            selected_index = self.listbox.curselection()[0]
            if selected_index < len(self.file_paths) - 1:
                self.file_paths[selected_index], self.file_paths[selected_index + 1] = self.file_paths[selected_index + 1], self.file_paths[selected_index]
                self.update_listbox()
        except IndexError:
            pass

    def update_listbox(self):
        """Refreshes the listbox with the current file order."""
        self.listbox.delete(0, tk.END)
        for i, path in enumerate(self.file_paths):
            self.listbox.insert(tk.END, f"{i+1}: {os.path.basename(path)}")
        self.listbox.select_set(0)

    def combine_files(self):
        """Combines the four files, padding smaller files to 32kb."""
        if len(self.file_paths) != 4:
            messagebox.showerror("Error", "Please select exactly four files before combining.")
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
                for filepath in self.file_paths:
                    file_size = os.path.getsize(filepath)
                    with open(filepath, "rb") as f_in:
                        data = f_in.read()

                    if file_size < CHUNK_SIZE_BYTES:
                        padding_needed = CHUNK_SIZE_BYTES - file_size
                        data += b'\x00' * padding_needed
                        padded_files_count += 1
                        print(f"Padded {os.path.basename(filepath)} with {padding_needed} bytes.")
                        
                    f_out.write(data)
            
            success_message = f"Files combined successfully into {os.path.basename(output_filepath)}"
            if padded_files_count > 0:
                success_message += f"\n{padded_files_count} file(s) were padded to 32kb."
            
            messagebox.showinfo("Success", success_message)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = SaveFileManager()
    app.mainloop()