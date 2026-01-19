from mixed import main as mixed_main
from binary_hashing import main as binary_main
from tfidf import main as tfdif_main
import tkinter as tk
from tkinter import filedialog, messagebox

class FileProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Double file checker")

        # Listbox to show file paths
        self.listbox = tk.Listbox(root, width=80, height=12)
        self.listbox.pack(padx=10, pady=10)
        # Checkbox frame
        chkbx_frame = tk.Frame(root)
        chkbx_frame.pack(pady=5)
        self.selected = tk.StringVar(value="B")
        rbutton1 = tk.Radiobutton(chkbx_frame, text="Pure Hashing", variable=self.selected, value="A")
        rbutton2 = tk.Radiobutton(chkbx_frame, text="Text analysis (NLP) + Binary Hashing", variable=self.selected, value="B")
        rbutton3 = tk.Radiobutton(chkbx_frame, text="Text analysis (NLP text only, ignore other formats)", variable=self.selected, value="C")
        rbutton1.pack(anchor="w")
        rbutton2.pack(anchor="w")
        rbutton3.pack(anchor="w")
        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add Directories", command=self.add_files).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Process Directories", command=self.process_files).grid(row=0, column=2, padx=5)



    def add_files(self):
        # askdirectory returns a single string, or an empty string if cancelled
        folder_path = filedialog.askdirectory(title="Select Folder")
        # Check if the user actually selected a folder (didn't press Cancel)
        if folder_path:
            self.listbox.insert(tk.END, folder_path)

    def remove_selected(self):
        selected = list(self.listbox.curselection())
        selected.reverse()  # remove from bottom to avoid index shift
        for index in selected:
            self.listbox.delete(index)

    def process_files(self):
        directory_list = list(self.listbox.get(0, tk.END))
        mode = str(self.selected.get())
        if not directory_list:
            messagebox.showwarning("No directories selected", "Please add directories first.")
            return
        print(directory_list)
        match mode:
            case "A":
                binary_main(directory_list)
            case "B":
                mixed_main(directory_list)
            case "C":
                tfdif_main(directory_list)
        messagebox.showinfo("Done", "Processing complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorGUI(root)
    root.mainloop()