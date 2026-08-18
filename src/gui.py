import tkinter as tk
from tkinter import filedialog, messagebox

from organizer import (
    get_category,
    get_files,
    organize_folder,
    undo_organization,
)


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root

        self.root.title("File Organizer")
        self.root.geometry("700x500")
        self.root.minsize(600, 450)

        self.selected_folder = None
        self.last_operation = None

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="File Organizer",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(25, 5))

        subtitle = tk.Label(
            self.root,
            text="Organize your files into categories automatically",
            font=("Segoe UI", 11)
        )
        subtitle.pack(pady=(0, 20))

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(fill="x", padx=40)

        tk.Label(
            folder_frame,
            text="Selected Folder:",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        path_frame = tk.Frame(folder_frame)
        path_frame.pack(fill="x", pady=8)

        self.folder_entry = tk.Entry(
            path_frame,
            font=("Segoe UI", 10)
        )
        self.folder_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        browse_button = tk.Button(
            path_frame,
            text="Browse",
            command=self.select_folder,
            width=10
        )
        browse_button.pack(
            side="left",
            padx=(10, 0)
        )

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        self.preview_button = tk.Button(
            button_frame,
            text="Preview",
            command=self.preview_files,
            width=12,
            height=2
        )
        self.preview_button.pack(
            side="left",
            padx=4
        )

        self.organize_button = tk.Button(
            button_frame,
            text="Organize Files",
            command=self.organize_files,
            width=12,
            height=2
        )
        self.organize_button.pack(
            side="left",
            padx=4
        )

        self.undo_button = tk.Button(
            button_frame,
            text="Undo",
            command=self.undo_last_operation,
            width=12,
            height=2,
            state=tk.DISABLED
        )
        self.undo_button.pack(
            side="left",
            padx=4
        )

        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear,
            width=12,
            height=2
        )
        self.clear_button.pack(
            side="left",
            padx=4
        )

        result_label = tk.Label(
            self.root,
            text="Preview / Results",
            font=("Segoe UI", 11, "bold")
        )
        result_label.pack(
            anchor="w",
            padx=40,
            pady=(10, 5)
        )

        result_frame = tk.Frame(self.root)
        result_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=(0, 25)
        )

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.result_text = tk.Text(
            result_frame,
            height=12,
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.result_text.yview
        )

    def select_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder to organize"
        )

        if not folder:
            return

        self.selected_folder = folder
        self.last_operation = None

        self.folder_entry.delete(
            0,
            tk.END
        )

        self.folder_entry.insert(
            0,
            folder
        )

        self.undo_button.config(
            state=tk.DISABLED
        )

        self.result_text.delete(
            "1.0",
            tk.END
        )

        self.result_text.insert(
            tk.END,
            "Folder selected successfully.\n\n"
            "Click Preview to see how the files "
            "will be organized."
        )

    def preview_files(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No Folder",
                "Please select a folder first."
            )
            return

        try:
            files = get_files(
                self.selected_folder
            )

            self.result_text.delete(
                "1.0",
                tk.END
            )

            if not files:
                self.result_text.insert(
                    tk.END,
                    "No files found in the selected folder."
                )
                return

            self.result_text.insert(
                tk.END,
                f"Found {len(files)} file(s):\n\n"
            )

            for file_path in files:
                category = get_category(file_path)

                self.result_text.insert(
                    tk.END,
                    f"{file_path.name}\n"
                    f"    → {category}\n\n"
                )

        except (
            FileNotFoundError,
            NotADirectoryError
        ) as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

        except OSError as error:
            messagebox.showerror(
                "File System Error",
                f"Could not read the folder.\n\n{error}"
            )

    def organize_files(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No Folder",
                "Please select a folder first."
            )
            return

        confirmation = messagebox.askyesno(
            "Confirm Organization",
            "Are you sure you want to organize "
            "the files in this folder?"
        )

        if not confirmation:
            return

        try:
            moved_files = organize_folder(
                self.selected_folder
            )

            self.result_text.delete(
                "1.0",
                tk.END
            )

            if not moved_files:
                self.last_operation = None

                self.undo_button.config(
                    state=tk.DISABLED
                )

                self.result_text.insert(
                    tk.END,
                    "No files were found to organize."
                )
                return

            self.last_operation = moved_files

            self.undo_button.config(
                state=tk.NORMAL
            )

            self.result_text.insert(
                tk.END,
                f"Successfully organized "
                f"{len(moved_files)} file(s).\n\n"
            )

            for item in moved_files:
                self.result_text.insert(
                    tk.END,
                    f"{item['source'].name}"
                    f" → {item['category']}\n"
                )

            messagebox.showinfo(
                "Completed",
                f"Successfully organized "
                f"{len(moved_files)} file(s).\n\n"
                "You can use Undo to restore them."
            )

        except (
            FileNotFoundError,
            NotADirectoryError
        ) as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

        except OSError as error:
            messagebox.showerror(
                "File System Error",
                f"Could not organize the files.\n\n{error}"
            )

    def undo_last_operation(self):
        if not self.last_operation:
            messagebox.showinfo(
                "Nothing to Undo",
                "There is no organization operation to undo."
            )
            return

        confirmation = messagebox.askyesno(
            "Confirm Undo",
            "Restore the files to their original locations?"
        )

        if not confirmation:
            return

        try:
            restored_files = undo_organization(
                self.last_operation
            )

            self.last_operation = None

            self.undo_button.config(
                state=tk.DISABLED
            )

            self.result_text.delete(
                "1.0",
                tk.END
            )

            if not restored_files:
                self.result_text.insert(
                    tk.END,
                    "No files could be restored."
                )
                return

            self.result_text.insert(
                tk.END,
                f"Successfully restored "
                f"{len(restored_files)} file(s).\n\n"
            )

            for item in restored_files:
                self.result_text.insert(
                    tk.END,
                    f"{item['source'].name}"
                    f" → original location\n"
                )

            messagebox.showinfo(
                "Undo Completed",
                f"Successfully restored "
                f"{len(restored_files)} file(s)."
            )

        except OSError as error:
            messagebox.showerror(
                "Undo Error",
                f"Could not restore the files.\n\n{error}"
            )

    def clear(self):
        self.selected_folder = None
        self.last_operation = None

        self.folder_entry.delete(
            0,
            tk.END
        )

        self.result_text.delete(
            "1.0",
            tk.END
        )

        self.undo_button.config(
            state=tk.DISABLED
        )


def start_app():
    root = tk.Tk()

    FileOrganizerApp(root)

    root.mainloop()