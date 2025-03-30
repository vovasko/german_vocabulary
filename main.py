import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import pandas as pd
from vocabulary import Vocabulary, Netzverb, tableManagement
import threading
import json
from pathlib import Path
from DB_manager import DBManager

ctk.set_default_color_theme(Path(__file__).parent / "theme.json")  # Themes: "blue" (standard), "green", "dark-blue"
ctk.set_appearance_mode("dark")
# cool colours: https://coolors.co/palette/cdb4db-ffc8dd-ffafcc-bde0fe-a2d2ff
colors = {
    "orange":        "#F67B1F",
    "shaded_orange": "#E07200",
    "green":         "#4E8F31",
    "shaded_green":  "#2E6A10",
    "blue":          "#3B7D9F",
    "shaded_blue":   "#165B75",
    "red":           "#CF2025",
    "shaded_red":    "#B40A10",
    # here are colors for the flash cards
    "yellow":        "#FCDA7F",
    "cyan":          "#A8A1FF",
}
nouns = Netzverb.nouns
verbs = Netzverb.verbs
adjectives = Netzverb.adjectives

class SettingWindow(ctk.CTkToplevel): # MARK: SettingWindow
    def __init__(self, master):
        # Create Window
        super().__init__(master)
        self.master = master
        self.title("Settings")
        width = 400
        height = 500
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        location = f"{width}x{height}+{x}+{y}"
        self.geometry(location)
        self.minsize(width, height)
        self.protocol("WM_DELETE_WINDOW", func=self.on_close)

        # Create Layout

        self.translation_settings()
        self.table_settings()
        self.flashcards_settings()

    def translation_settings(self):
        translation_area = ctk.CTkFrame(self)
        translation_area.grid_columnconfigure((0,1), weight=1, uniform="a")
        translation_area.grid_rowconfigure((0,1,2,3,4), weight=1, uniform="a")
        # translation_area.pack(expand = True, fill = "both", padx = 5, pady = 5)
        translation_area.pack(expand=True, fill="both", padx = 5, pady = 5)

        self.languages = list(Netzverb.languages.values())

        def second_lang_list(x):
            filtered_values = ["None"] + [lang for lang in self.languages if lang != self.master.main_lang_var.get()]
            second_lang_box.configure(values=filtered_values)
            self.master.sec_lang_var.set("")

        ctk.CTkLabel(translation_area, text="Translation Settings", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2)
        ctk.CTkLabel(translation_area, text="Main translation language").grid(row=1, column=0, sticky="w", padx=5)
        ctk.CTkLabel(translation_area, text="Second translation language").grid(row=2, column=0, sticky="w", padx=5)
        ctk.CTkLabel(translation_area, text="Examples to include").grid(row=3, column=0, sticky="w", padx=5)
        ctk.CTkLabel(translation_area, text="Meanings to include").grid(row=4, column=0, sticky="w", padx=5)

        main_lang_box = ctk.CTkComboBox(translation_area, values=self.languages, 
            variable=self.master.main_lang_var, command=second_lang_list)
        main_lang_box.grid(row=1, column=1, sticky="e", padx=5)
        
        second_lang_box = ctk.CTkComboBox(translation_area, variable=self.master.sec_lang_var,
            values = ["None"] + [lang for lang in self.languages if lang != self.master.main_lang_var.get()])
        second_lang_box.grid(row=2, column=1, sticky="e", padx=5)

        example_button = ctk.CTkSegmentedButton(translation_area, values=[0,1,2,3], variable=self.master.example_var)
        example_button.grid(row=3, column=1, sticky="e", padx=5)

        meaning_button = ctk.CTkSegmentedButton(translation_area, values=[0,1,2,3], variable=self.master.meaning_var)
        meaning_button.grid(row=4, column=1, sticky="e", padx=5)

    def table_settings(self):
        table_area = ctk.CTkFrame(self)
        table_area.grid_columnconfigure((0,1), weight=1)
        table_area.pack(expand=True, fill="both", padx = 5, pady = 5)

        ctk.CTkLabel(table_area, text="Table display options", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2)

        self.col_variables = {}
        grid = [1, 0]
        for key, val in self.master.settings.get("columns").items():
            self.col_variables[key] = ctk.BooleanVar(value=val)
            if key == "german": continue
            ctk.CTkSwitch(table_area, text=key, variable=self.col_variables[key], border_color=ctk.CTkSwitch(self).cget("progress_color"), border_width=1).grid(row=grid[0], column=grid[1], sticky="w")
            grid[0] += 1
            if grid[0] == 4: grid = [1, 1]

    def flashcards_settings(self):
        flashcards_area = ctk.CTkFrame(self)
        flashcards_area.grid_columnconfigure((0,1), weight=1)
        flashcards_area.pack(expand=True, fill="both", padx = 5, pady = 5)

        ctk.CTkLabel(flashcards_area, text="Flash cards viewer", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2)
        ctk.CTkLabel(flashcards_area, text="Cards in deck:").grid(row=1, column=0, sticky="w", padx = 5)
        ctk.CTkComboBox(flashcards_area, values=["10","15","20","25","30"], variable=self.master.cards_in_deck).grid(row=1, column=1, sticky="e", padx = 5)
        ctk.CTkLabel(flashcards_area, text="Flash cards content").grid(row=2, column=0, columnspan=2)

        self.cards_variables = {}
        grid = [3, 0]
        for key, val in self.master.settings.get("flashcards").items():
            self.cards_variables[key] = ctk.BooleanVar(value=val)
            if key == "german": continue
            ctk.CTkSwitch(flashcards_area, text=key, variable=self.cards_variables[key], border_color=ctk.CTkSwitch(self).cget("progress_color"), border_width=1).grid(row=grid[0], column=grid[1], sticky="w")
            grid[0] += 1
            if grid[0] == 6: grid = [3, 1]
    
    @classmethod
    def load_settings(self):
        file_path = Path(__file__).parent / "settings.json"
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}   

    def save_settings(self):
        file_path = Path(__file__).parent / "settings.json"
        with open(file_path, 'w') as file:
            json.dump(self.master.settings, file, indent=4)

    def on_close(self):
        update_table = False
        # Save some variables for table and flash cards
        for key in self.master.settings.get("columns").keys(): 
            if self.master.display_cols[key] != self.col_variables[key].get():
                update_table = True
                self.master.display_cols[key] = self.col_variables[key].get()
            self.master.flash_info[key] = self.cards_variables[key].get()
        
        if update_table: self.master.create_table()
        self.destroy()
        self.master.update_settings()
        self.save_settings()

class CardsWindow(ctk.CTkToplevel): # MARK: CardsWindow
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Flash cards viewer")
        width = 400
        height = 250
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        location = f"{width}x{height}+{x}+{y}"
        self.geometry(location)
        self.minsize(width, height)
        self.protocol("WM_DELETE_WINDOW", func=self.on_close)

        self.create_variables()
        self.create_flashcards_layout()
        self.set_deck()
        self.next_card()

    def create_variables(self):
        self.deck = pd.DataFrame()

        self.card_data = pd.Series()
        self.current_card = ctk.IntVar(value=0)
        self.card_number_var = ctk.Variable(value="card 1 / 20")
        self.german_word_var = ctk.Variable(value="das Auto")
        self.meaning_var = ctk.Variable(value="meaning of the word")
        self.main_translation_var = ctk.Variable(value="Main translation")
        self.second_translation_var = ctk.Variable(value="Second translation")
        self.example_var = ctk.Variable(value="Example sentance")
        self.score_var = ctk.IntVar(value=-11)
        
    def set_deck(self):
        flash_option = self.master.flash_mode.get()
        sample_amount = lambda shape: min(int(self.master.cards_in_deck.get()), shape)
        self.deck = self.master.db.to_dataframe(mode = flash_option) # get df with needed rows from db
            
        self.deck = self.deck.sample(sample_amount(self.deck.shape[0]), weights=self.deck.score.apply(lambda x: 4-x))
    
    def flip(self):
        if self.front_side.winfo_ismapped():
            self.front_side.place_forget()
            self.back_side.place(relheight=0.69, relwidth=0.98, relx=0.01, rely=0.01)
        else: 
            self.back_side.place_forget()
            self.front_side.place(relheight=0.69, relwidth=0.98, relx=0.01, rely=0.01)

    def create_flashcards_layout(self):
        self.cards_area = ctk.CTkFrame(self)
        self.cards_area.pack(fill = "both", expand = True)

        self.front_side = ctk.CTkFrame(self.cards_area, fg_color=colors["cyan"], corner_radius=10)
        self.front_side.place(relheight=0.69, relwidth=0.98, relx=0.01, rely=0.01)

        card_number_txt = ctk.CTkLabel(self.front_side, text_color="black", textvariable=self.card_number_var)
        german_word_txt = ctk.CTkLabel(self.front_side, text_color="black", textvariable=self.german_word_var, font=ctk.CTkFont(size=30, weight="bold"))
        meaning_txt = ctk.CTkLabel(self.front_side, text_color="black", textvariable=self.meaning_var)
        
        card_number_txt.place(relx=0.5, rely=0.1, anchor="center")
        if self.master.flash_info["german"]: german_word_txt.place(relx=0.5, rely=0.5, anchor="center")
        if self.master.flash_info["meaning"]: meaning_txt.place(relx=0.5, rely=0.95, anchor="s")

        self.back_side = ctk.CTkFrame(self.cards_area, fg_color=colors["yellow"], corner_radius=10)
        
        card_number_txt_2 = ctk.CTkLabel(self.back_side, text_color="black", textvariable=self.card_number_var)
        main_translation_txt = ctk.CTkLabel(self.back_side, text_color="black", textvariable=self.main_translation_var)
        second_translation_txt = ctk.CTkLabel(self.back_side, text_color="black", textvariable=self.second_translation_var)
        example_txt = ctk.CTkLabel(self.back_side, text_color="black", textvariable=self.example_var)
        score_txt = ctk.CTkLabel(self.back_side, text_color="black", textvariable=self.score_var)

        card_number_txt_2.place(relx=0.5, rely=0.1, anchor="center")
        if self.master.flash_info["translation"]: main_translation_txt.place(relx=0.5, rely=0.4, anchor="center")
        if self.master.flash_info["second_translation"]: second_translation_txt.place(relx=0.5, rely=0.6, anchor="center")
        if self.master.flash_info["example"]: example_txt.place(relx=0.5, rely=0.9, anchor="center")
        if self.master.flash_info["score"]: score_txt.place(relx=0.98, rely=0.0, anchor="ne")

        buttons = ctk.CTkFrame(self.cards_area, fg_color="transparent") 
        buttons.place(relheight=0.3, relwidth=1.0, relx=0.0, rely=0.7)

        ctk.CTkButton(buttons, text="Again", fg_color=colors["red"], hover_color=colors["shaded_red"], 
                      command=lambda: self.next_card(-1)
                      ).place(relx=0.01, rely=0.3, relheight=0.4, relwidth=0.18)
        ctk.CTkButton(buttons, text="Hard", fg_color=colors["orange"], hover_color=colors["shaded_orange"],
                      command=lambda: self.next_card(1)
                      ).place(relx=0.2, rely=0.3, relheight=0.4, relwidth=0.18)
        ctk.CTkButton(buttons, text="Flip", 
                      command=self.flip
                      ).place(relx=0.39, rely=0.3, relheight=0.4, relwidth=0.22)
        ctk.CTkButton(buttons, text="Good", fg_color=colors["blue"], hover_color=colors["shaded_blue"],
                      command=lambda: self.next_card(2)
                      ).place(relx=0.62, rely=0.3, relheight=0.4, relwidth=0.18)
        ctk.CTkButton(buttons, text="Easy", fg_color=colors["green"], hover_color=colors["shaded_green"],
                      command=lambda: self.next_card(3)
                      ).place(relx=0.81, rely=0.3, relheight=0.4, relwidth=0.18)

    def next_card(self, points=0):
        if self.score_var.get() != -11: # set points for previous card
            self.deck.loc[self.deck.query(f"german == '{self.card_data["german"]}'").index, "score"] = points
        if self.current_card.get() == self.deck.shape[0]: 
            self.finish_layout()
            return
        if self.back_side.winfo_ismapped(): self.flip()

        self.card_data = self.deck.iloc[self.current_card.get(), :]
        self.current_card.set(self.current_card.get() + 1)
        
        self.card_number_var.set(f"card {self.current_card.get()} / {self.deck.shape[0]}")
        if self.card_data["type"] in ["der", "die", "das", "NOUN"]:
            self.german_word_var.set(f"{self.card_data["type"]} {self.card_data["german"]}") 
        else:  self.german_word_var.set(f"{self.card_data["german"]}")  
        self.meaning_var.set(tableManagement.split_to_rows(f"{self.card_data["meaning"]}"))
        self.main_translation_var.set(f"{self.card_data["translation"]}") 
        self.second_translation_var.set(f"{self.card_data["second_translation"]}")
        self.example_var.set(f"{self.card_data["example"]}")
        self.score_var.set(f"{self.card_data["score"]}")
    
    def finish_layout(self): 
        self.cards_area.pack_forget()
        finish_frame = ctk.CTkFrame(self)
        finish_frame.pack(fill = "both", expand = True)

        finish_card = ctk.CTkFrame(finish_frame, fg_color="#bbd0ff", corner_radius=10)
        finish_card.place(relheight=0.69, relwidth=0.98, relx=0.01, rely=0.01)
        ctk.CTkLabel(finish_card, text="You did well!", text_color="black").place(relx=0.5, rely=0.5, anchor="center")

        exit_button = ctk.CTkButton(self, text="Exit", command=self.on_close)
        exit_button.place(relx=0.5, rely=0.85, anchor="center")
    
    def on_close(self):
        # closes window and saves progress to db properly
        self.deck.reset_index(inplace=True)
        self.deck = self.deck[["rowid", "score"]]
        self.master.db.update_from_df(self.deck)
        self.master.update_stats()
        self.destroy()

class EditableWindow(ctk.CTkToplevel): # MARK: EditableWindow
    def __init__(self, master, mode):
         # Create Window
        super().__init__(master)
        self.master = master
        self.mode = mode
        # Check if there are any records to display
        self.populate_records()
        width = 1200
        height = 500
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        location = f"{width}x{height}+{x}+{y}"
        self.geometry(location)
        self.minsize(width, height)
        self.protocol("WM_DELETE_WINDOW", func=self.on_close)

        self.edit_entry = None
        self.updated_records = pd.DataFrame(columns=list(self.records.columns))
            
        self.create_table()
        self.create_buttons()

    def populate_records(self):
        self.records = pd.DataFrame()

        if self.mode == "duplicates":
            self.title("Duplicate viewer")
            self.records = self.master.db.to_dataframe(mode="duplicates")
            empty_string = "No duplicates found"
        elif self.mode == "edit":
            self.title("Edit mode")
            self.records = self.master.db.to_dataframe(mode="all")
            empty_string = "No records found"
        
        if self.records.empty:
            messagebox.showinfo("Info", empty_string)
            self.destroy()
            return

    def create_table(self):
        self.cols = {
            "rowid" : 20, "type" : 50, "german" : 110, "translation": 200, 
            "second_translation": 200, "example" : 200, "meaning": 200, "score" : 25}

        self.table = ttk.Treeview(self, columns=list(self.cols.keys()), show='headings', selectmode="extended")
        
        for name in self.cols.keys():
            self.table.heading(name, text=name, command=lambda c = name: sort_column(c, False))
            self.table.column(name, width=self.cols[name])

        self.table.pack(expand=True, fill="both", padx=10)

        self.table.bind("<BackSpace>", lambda x: self.delete_selected_rows())
        self.table.bind("<Delete>", lambda x: self.delete_selected_rows())
        self.table.bind("<Double-1>", self.start_edit)

        for row in self.records.itertuples(): # populate the table
            self.table.insert("", "end", iid=row[0], values=list(row))

        def sort_column(col, reverse):
            """Sort the Treeview column data."""
            data = [(self.table.set(k, col), k) for k in self.table.get_children('')]
            # Case-insensitive sorting
            data.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
            
            for index, (val, k) in enumerate(data):
                self.table.move(k, '', index)

            # Reverse sorting on next click
            self.table.heading(col, command=lambda: sort_column(col, not reverse))

    def delete_selected_rows(self): 
        selected_items = self.table.selection()  # Get selected rows
        for item in selected_items:
            row_id = self.table.item(item)["values"][0]

            updated_row = self.records.loc[row_id].copy()  # Get the row using the index (rowid)
            updated_row["german"] = "#delete"
            self.updated_records.loc[row_id] = updated_row  # Add the row to the updated DataFrame
            
            self.records.drop(row_id, inplace=True)  # Remove the row from the original DataFrame
            self.table.delete(item)  # Delete each selected row

    def start_edit(self, event):
        # Identify the row and column being clicked
        row_id = self.table.identify_row(event.y) # row_id in treeview
        column_id = self.table.identify_column(event.x) # column_id in treeview

        if row_id and column_id:
            columns = list(self.cols.keys())
            column_name = columns[int(column_id[1:]) - 1]
            if column_name == "rowid": return
            current_value = self.records.at[int(row_id), column_name]

            # Get the bounding box of the cell
            bbox = self.table.bbox(row_id, column_id)
            if bbox:
                # Create an Entry widget over the cell
                self.edit_entry = ctk.CTkEntry(self, width=bbox[2], height=bbox[3], corner_radius=0)
                self.edit_entry.place(x=bbox[0], y=bbox[1])
                self.edit_entry.insert(0, current_value)  # Insert current value
                self.edit_entry.focus()

                # Bind events to save the value
                self.edit_entry.bind("<Return>", lambda e: self.save_edit(row_id, column_name))
                self.edit_entry.bind("<FocusOut>", lambda e: self.save_edit(row_id, column_name))

    # Function to save edited value to Treeview and DataFrame
    def save_edit(self, row_id, column_name):
        if self.edit_entry:
            new_value = self.edit_entry.get()
            # Update DataFrame
            self.records.at[int(row_id), column_name] = new_value
            updated_row = self.records.loc[int(row_id)].copy()
            self.updated_records.loc[int(row_id)] = updated_row
            # Update Treeview
            self.table.set(row_id, column_name, new_value)
            # Remove Entry widget
            self.edit_entry.destroy()
            self.edit_entry = None
    
    def create_buttons(self):
        buttons = ctk.CTkFrame(self)
        buttons.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(buttons, text="Cancel",
                      command=self.on_close # do not apply changes
                      ).pack(side="left", expand=True)
        ctk.CTkButton(buttons, text="Save changes",
                      command=self.save
                      ).pack(side="left", expand=True)
        if self.mode == "duplicates" : ctk.CTkButton(buttons, text="Keep last instance",
                      command=self.auto_delete
                      ).pack(side="left", expand=True)
    
    def auto_delete(self):
        # Identify duplicates (excluding the ones that are kept)
        duplicates = self.records[self.records.duplicated(subset=["type", "german"], keep="last")]
        # Remove duplicates from main dataframe
        self.records = self.records.drop_duplicates(subset=["type", "german"], keep="last")
        duplicates["german"] = "#delete"  # Mark duplicates for deletion
        # Store deleted duplicates while preserving their indices
        if hasattr(self, "updated_records"):  # If attribute exists, append to it
            self.updated_records = pd.concat([self.updated_records, duplicates])
        else: self.updated_records = duplicates.copy()

        # Clear and populate the table
        for item in self.table.get_children():
            self.table.delete(item)
        
        for row in self.records.itertuples(): # populate the table
            self.table.insert("", "end", iid=row[0], values=list(row))
    
    def save(self):
        self.updated_records.index.name = "rowid" # set index name to rowid
        self.updated_records.reset_index(inplace=True)
        self.master.db.update_from_df(self.updated_records)
        self.on_close()

    def on_close(self):
        self.master.update_stats()
        self.destroy()

class MainApp(ctk.CTk): # MARK: MainApp
    def __init__(self):
        super().__init__()
        self.title("Vocabulary booster")
        width = 900
        height = 500
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        location = f"{width}x{height}+{x}+{y}"
        self.geometry(location)

        self.create_variables()
        self.update_settings()

        self.create_menu()

        self.create_layout()
        self.update_stats()

        self.mainloop()

    def open_window(self, w_name):
        if self.windows[w_name] is None or not self.windows[w_name].winfo_exists():
            match w_name:
                case "settings"   : self.windows[w_name] = SettingWindow(self)
                case "duplicates" : self.windows[w_name] = EditableWindow(self, mode="duplicates")
                case "edit_mode"  : self.windows[w_name] = EditableWindow(self, mode="edit")
                case "flashcards" : self.windows[w_name] = CardsWindow(self)
        else: 
            self.windows[w_name].deiconify()  # Restore the Toplevel if it was minimized
            self.windows[w_name].lift()       # Bring it to the front
            self.windows[w_name].focus_force()  # Set focus
    
    def create_variables(self):
        # General variables
        self.db = DBManager() # db manager
        self.input_data = Vocabulary() # df to store raw german words
        self.storage = tableManagement.load_storage() # df with loaded words from .csv
        self.new_words = pd.DataFrame(columns= self.storage.columns) # freshly translated words
        # self.dup_values = tableManagement.show_duplicates(self.storage) # df with duplicates
        self.in_file_var = ctk.Variable(value="")
        self.german_word = ctk.Variable(value="")
        self.flash_mode = ctk.Variable(value="all")

        # Windows and settings
        self.windows = {
            "settings" : None,
            "duplicates" : None,
            "edit_mode" : None,
            "flashcards" : None
        }
        self.settings = SettingWindow.load_settings()

        # Variables from settings
        self.main_lang_var = ctk.Variable(value=self.settings.get("main_lang"))
        self.sec_lang_var = ctk.Variable(value=self.settings.get("second_lang"))
        self.meaning_var = ctk.Variable(value=self.settings.get("examples"))
        self.example_var = ctk.Variable(value=self.settings.get("meanings"))

        self.display_cols = self.settings.get("columns")
        self.flash_info = self.settings.get("flashcards")
        self.cards_in_deck = ctk.Variable(value=self.settings.get("cards_in_deck"))

        # Stats variables
        self.dup_number = ctk.Variable(value="")
        self.new_number = ctk.Variable(value="")

    # MARK: Update functions
    def update_settings(self):
        self.settings["main_lang"] = self.main_lang_var.get()
        self.settings["second_lang"] = self.sec_lang_var.get()
        self.settings["examples"] = self.example_var.get()
        self.settings["meanings"] = self.meaning_var.get()
        self.settings["columns"] = self.display_cols
        self.settings["flashcards"] = self.flash_info
        self.settings["cards_in_deck"] = self.cards_in_deck.get()
    
    def update_stats(self):
        dn = self.db.count_rows(mode = "duplicates") # number of duplicates
        if dn:
            self.dup_number.set(f"Duplicate values: {dn}")
            self.dup_values_stat.pack(side="left", padx=10)
        elif dn == 0:

            self.dup_number.set("")
            if self.dup_values_stat.winfo_ismapped(): self.dup_values_stat.pack_forget()

        nn = self.db.count_rows(mode = "new") # number of new words
        if nn:
            self.new_number.set(f"New words: {nn}")
            self.new_words_stat.pack(side="left", padx=10)
        elif nn == 0:
            self.new_number.set("")
            if self.new_words_stat.winfo_ismapped(): self.new_words_stat.pack_forget()

    def update_progress(self, completed, total):
        progress = completed / total
        self.progress_var.set(progress)

    # def sync_storage(self, mode="default"):
    #     match mode:
    #         case "duplicates":
    #             self.storage = pd.concat([self.storage, self.dup_values]).sort_index()
    #             self.storage.reset_index(inplace=True, drop=True)
    #         # case "edit":
    #         #     pass
    #         case _:
    #             pass
        
    #     tableManagement.update_storage(self.storage)

    # MARK: Menu area
    def create_menu(self):
        # Create the menu bar
        menu_bar = tk.Menu(self)

        # Add "File" menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Add "Settings" menu
        sett_menu = tk.Menu(menu_bar, tearoff=0)
        sett_menu.add_command(label="Configure Settings", command=lambda: self.open_window("settings"))
        sett_menu.add_command(label="Extract words to csv", command=self.extract_df)
        sett_menu.add_command(label="Load new storage", command=self.load_new_storage)
        menu_bar.add_cascade(label="Settings", menu=sett_menu)

        # Add "Help" menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About")
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Attach the menu bar to the main window
        self.config(menu=menu_bar)

    def extract_df(self):
        file_path = filedialog.asksaveasfile()
        if file_path:
            try:
                data = self.db.to_dataframe(mode="all")
                data.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data saved to {file_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        
    def load_new_storage(self): # deprecated and impossible to use
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.storage = pd.read_csv(file_path)
                self.update_table(self.storage)
                self.update_stats()
                messagebox.showinfo("Success", f"Data loaded successfully with {self.storage.shape[0]} rows and {self.storage.shape[1]} columns.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def load_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")])
        if file_path:
            try:
                self.input_data.read_data(file_path)
                self.input_data.clean_data()
                self.in_file_var.set(file_path.split("/")[-1])
                self.translate_button.configure(state="normal")
                messagebox.showinfo("Success", f"Data loaded successfully with {self.input_data.data.shape[0]} rows and {self.input_data.data.shape[1]} columns.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    # MARK: - Layout area
    def create_layout(self):
        self.control_panel = ctk.CTkFrame(self, fg_color="transparent", width = 200)
        self.table_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.control_panel.grid(row=0, column=0, sticky="ns")
        self.table_frame.grid(row=0, column=1, sticky="nsew")

        self.create_translation_area()
        self.create_practice_area()
        self.create_table_buttons()
        self.create_stats_bar()
        self.create_table()

    def create_translation_area(self):
        trl = ctk.CTkFrame(self.control_panel) # trl => TRanslation Layout
        trl.pack(fill="x", pady=10, padx=10)

        tr_option = ctk.Variable(value="Translate from file")
        ctk.CTkSegmentedButton(trl, variable=tr_option, command=lambda x: change_layout(),
                               values=["Translate from file", "Translate one word"],
                               ).pack(pady=10)
        
        def change_layout():
            if tr_option.get() == "Translate one word":
                input_button.grid_forget()
                file_entry.grid_forget()
                word_label.grid(row=0, column=0, sticky="e", padx=10)
                word_entry.grid(row=0, column=1, sticky="e", padx=10)
            else: 
                word_label.grid_forget()
                word_entry.grid_forget()
                input_button.grid(row=0, column=0, sticky="w", padx=10)
                file_entry.grid(row=0, column=1, sticky="e", padx=10)

        # Translate from file setup
        translation_frame = ctk.CTkFrame(trl, fg_color="transparent")
        translation_frame.grid_columnconfigure((0,1), weight=1)
        translation_frame.grid_rowconfigure((0,1), weight=1)
        translation_frame.pack(expand = True, fill = "x", padx=3, pady=5)

        input_button = ctk.CTkButton(translation_frame, text="Input new words", command=self.load_csv_file)
        input_button.grid(row=0, column=0, sticky="w", padx=10)
        file_entry = ctk.CTkEntry(translation_frame, state="disabled", textvariable=self.in_file_var)
        file_entry.grid(row=0, column=1, sticky="e", padx=10)

        self.translate_button = ctk.CTkButton(trl, text="Translate", command=lambda: self.translate(mode=tr_option.get()), state="disabled")
        self.translate_button.pack(pady=10)# grid(row=1, column=0, columnspan=2, padx=10)

        self.progress_var = ctk.Variable(value=0)
        self.progress_bar = ctk.CTkProgressBar(trl, height=25, mode="determinate", variable=self.progress_var)
        self.progress_bar["maximum"] = 1.0
        # self.progress_bar.pack(pady=10)

        word_label = ctk.CTkLabel(translation_frame, text="Input word:")
        word_entry = ctk.CTkEntry(translation_frame, textvariable=self.german_word)

        word_entry.bind(sequence="<Key>", 
                        command=lambda x: 
                        self.translate_button.configure(state = "normal") 
                        if len(self.german_word.get()) > 1 else 
                        self.translate_button.configure(state = "disabled"))

    def create_practice_area(self):
        pr_frame = ctk.CTkFrame(self.control_panel) 
        pr_frame.grid_columnconfigure((0,1), weight=1)
        pr_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(pr_frame, text="Practice area").grid(row=0, column=0, padx=10, pady=2, columnspan=2)

        ctk.CTkComboBox(pr_frame, values=["all","new","nouns","verbs","adjectives","other"],
                        variable=self.flash_mode
                        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkButton(pr_frame, text="Flash cards viewer", command=lambda: self.open_window("flashcards")
                      ).grid(row=1, column=1, padx=10,pady=10,sticky="e")
   
    def create_stats_bar(self):
        stats_frame = ctk.CTkFrame(self.control_panel) 
        stats_frame.pack(fill="both", padx=10)
        ctk.CTkFrame(self.control_panel, height=10, fg_color="transparent").pack()  # Padding below the status bar
        
        self.dup_values_stat = ctk.CTkLabel(stats_frame, textvariable=self.dup_number)
        self.new_words_stat = ctk.CTkLabel(stats_frame, textvariable=self.new_number)

    # MARK: - Table functions
    def create_table_buttons(self):
        tbs_frame = ctk.CTkFrame(self.control_panel) 
        tbs_frame.grid_columnconfigure((0,1), weight=1)
        tbs_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        ctk.CTkLabel(tbs_frame, text="Table settings").grid(row=0, column=0, padx=10, pady=2, columnspan=2)
        # Row 1
        ctk.CTkButton(tbs_frame, text="Display vocabulary", 
                      command=self.display_vocabulary
                      ).grid(row=1, column=0, padx=10,pady=5,sticky="w")
        ctk.CTkButton(tbs_frame, text="Show duplicates",
                      command=lambda: self.open_window("duplicates")
                      ).grid(row=1, column=1, padx=10,pady=5,sticky="e")
        # Row 2
        ctk.CTkLabel(tbs_frame, text="Filter: ").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        filter = ctk.Variable(value="all")
        ctk.CTkComboBox(tbs_frame, values=["all", "new", "nouns", "verbs", "adjectives", "other"],
                        variable=filter, command=lambda var: self.display_vocabulary(filter=var)
                        ).grid(row=2, column=1, padx=10, pady=5, sticky="e")
        # Row 3
        ctk.CTkButton(tbs_frame, text="Edit mode",
                      command=lambda: self.open_window("edit_mode")
                      ).grid(row=3, column=1, padx=10,pady=5,sticky="e")      

    def create_table(self):
        col_names = []
        for col, value in self.display_cols.items():
            if value: col_names.append(col)
        
        # Set style
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview general styling
        style.configure("Treeview",
            background="gray29",       # Matches CTkEntry fg_color (light mode)
            foreground="#DCE4EE",        # Matches CTkLabel text_color (light mode)
            fieldbackground="gray29",  # Matches CTkEntry fg_color
            font=("Roboto", 13),        # Matches CTkFont settings
            rowheight=25,               # Adjust row height for readability
            # borderwidth=0               # Flat, modern look
            bordercolor = "transparent"
        )

        # Treeview heading styling
        style.configure("Treeview.Heading",
            background="#9370DB",       # Matches CTkButton fg_color
            foreground="#DCE4EE",       # Matches CTkButton text_color
            font=("Roboto", 13, "bold"), # Matches CTkFont settings
            borderwidth=1,              # Slight border for definition
            relief="flat"
        )

        # Hover effect for heading
        style.map("Treeview.Heading",
            background=[("active", "#7A5DC7")],  # Matches CTkButton hover_color
            relief=[("pressed", "groove"), ("!pressed", "flat")]
        )

        # Selected row styling
        style.map("Treeview",
            background=[("selected", "#7A5DC7")], # Matches CTkSwitch progress_color
            foreground=[("selected", "#DCE4EE")]  # Matches CTkButton text_color
        )
        
        # Create Treeview
        if hasattr(self, "table"): del self.table
        self.table = ttk.Treeview(self.table_frame, columns=col_names, show='headings', selectmode="extended")
        widths = {
            "type" : 50, "german" : 110, "translation": 200, "second_translation": 200, 
            "example" : 200, "meaning": 200, "score" : 30
        }
        for name in col_names:
            self.table.heading(name, text=name, command=lambda c = name: sort_column(c, False))
            self.table.column(name, width=widths[name])

        # Vertical Scrollbar
        self.v_scrollbar = ctk.CTkScrollbar(self.table_frame, width=15, orientation="vertical", command=self.table.yview)
        self.v_scrollbar.place(relx=0.97, rely=0.02, relheight=0.94)

        # Horizontal Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(self.table_frame, height=15, orientation="horizontal", command=self.table.xview)
        self.h_scrollbar.place(relx=0.02, rely=0.96, relwidth=0.95)

        # Link Treeview and Scrollbars
        self.table.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.table.place(relx=0.02, rely=0.02, relwidth=0.95, relheight=0.94)
        
        def sort_column(col, reverse):
            """Sort the Treeview column data."""
            data = [(self.table.set(k, col), k) for k in self.table.get_children('')]
            # Case-insensitive sorting
            data.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
            
            for index, (val, k) in enumerate(data):
                self.table.move(k, '', index)

            # Reverse sorting on next click
            self.table.heading(col, command=lambda: sort_column(col, not reverse))
    
    def translate(self, mode = None):
        if mode == "Translate one word":
            self.input_data.data = pd.DataFrame({"Input":[self.german_word.get()]})
            self.input_data.clean_data()

        if  self.input_data.data.empty:
            return
        
        def gui_callback():
            self.after(0, lambda: self.translation_complete())
        
        self.translate_button.pack_forget()
        self.progress_bar.pack(pady=5)

        threading.Thread(
            target=self.input_data.get_netz_info,       # Function to execute in the thread
            args=(self.main_lang_var.get(), 
                  self.sec_lang_var.get(),
                  self.example_var.get(),
                  self.meaning_var.get(), 
                  self.update_progress,
                  gui_callback),                 # Arguments for the function
            daemon=True                          # Make the thread a daemon thread
        ).start() 
        
    def translation_complete(self):
        self.progress_bar.pack_forget()
        self.translate_button.pack(pady=10)
        
        messagebox.showinfo("Success", 
            f"Translation completed!\n\
            {self.input_data.data["translation"].notna().sum()} out of {self.input_data.data.shape[0]}")
        
        self.update_table(self.input_data.data)
        # self.storage = pd.concat([self.storage, self.input_data.data], ignore_index=True)
        # tableManagement.save_to_storage(self.input_data.data)
        self.db.insert_data(self.input_data.data)
        self.input_data.data.drop(self.input_data.data.index, inplace=True)
        self.update_stats()
        
    def update_table(self, df: pd.DataFrame):
        if df.shape[0] > 0:
            self.new_words = pd.concat([self.new_words, df], ignore_index=True)

        for i in df[list(self.table["columns"])].itertuples(index=False):
            self.table.insert(parent='', index=tk.END, values=i)

    def display_vocabulary(self, filter="all"):
        for item in self.table.get_children(): # clear the table
            self.table.delete(item)

        data = self.db.to_dataframe(mode = filter)

        for i in data[list(self.table["columns"])].itertuples(index=False):
            self.table.insert(parent='', index=tk.END, values=i)


if __name__ == "__main__":
    MainApp()
