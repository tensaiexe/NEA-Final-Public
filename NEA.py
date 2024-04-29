import tkinter as tk # graphic library
from tkinter import *
from tkinter import ttk, font, messagebox, Frame, Entry, Button, Label, END
from PIL import Image, ImageTk #allows for images on Tk UI
import sqlite3 #allow me to enter SQL Queries via python
import random #allows me to request random values
import hashlib #allows me to create and hash values, ie(passowrd)
import os
from tkcalendar import DateEntry
import datetime # to open date dropdown
import re #for defensive design Reg ex
import webbrowser #allows for hyperlinks
import time # allows to create timers
import uuid  # to generate UUID's

class LoginMenu:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Login")
        self.parent.geometry("300x200")
        self.createUI()

    def createUI(self):  # initalises the UI and creates its buttons and labels
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.usertxtLbl = ttk.Label(self.frame, text="Username:")
        self.usertxtLbl.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.userImpBox = ttk.Entry(self.frame)
        self.userImpBox.grid(row=0, column=1, padx=5, pady=5)
        self.passtxtLbl = ttk.Label(self.frame, text="Password:")
        self.passtxtLbl.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.passImpBox = ttk.Entry(self.frame, show="*")
        self.passImpBox.grid(row=1, column=1, padx=5, pady=5)
        self.LoginBtn = ttk.Button(self.frame, text="Login", command=self.login)
        self.LoginBtn.grid(row=2, column=0, columnspan=2, pady=10, sticky="we")
        self.RegisterBtn = ttk.Button(self.frame, text="Register", command=self.register)
        self.RegisterBtn.grid(row=3, column=0, columnspan=2, pady=5, sticky="we")

    def login(self): #defines the login system
        username = self.userImpBox.get()
        password = self.passImpBox.get()

        if not self.checkImp(username, password):
            return

        try:
            connection = sqlite3.connect("physics_data.db") #connecting to the main database for the program
            cursor = connection.cursor()

            cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,)) #retriving the information required from the users table 
            user_data = cursor.fetchone()

            if user_data:
                UID, hashPassStore = user_data
                if self.checkPass(password, hashPassStore): #compares the hashed password vs the password entered
                    messagebox.showinfo("Login Successful", "Welcome!")
                    self.parent.destroy()
                    app = PhysicsRevisionHelper(tk.Tk(), UID)  #closes the login window opens the main revision helper window also while passing on the UID
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password.")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while accessing the database: {str(e)}") #error handling via excepts
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}") #error handling via excepts
        finally:
            if connection:
                connection.close()

    def register(self): #defines the register function
        username = self.userImpBox.get()
        password = self.passImpBox.get()

        if not self.checkImp(username, password):
            return

        try:
            connection = sqlite3.connect("physics_data.db") #connects to the main database for the program
            cursor = connection.cursor()

            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id TEXT PRIMARY KEY,
                                username TEXT UNIQUE,
                                password_hash TEXT
                              )''')  #creating the first table in the database with the ID as a primary key

            cursor.execute("SELECT * FROM users WHERE username=?", (username,)) #Checking if inputed username already exists in the users table
            if cursor.fetchone():
                messagebox.showerror("Registration Failed", "Username already exists.")
            else:
                UID = str(uuid.uuid4())  
                passHash = self.hashPass(password)
                cursor.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)", (UID, username, passHash)) #Adds the user[ and users data] to the users table
                connection.commit()
                messagebox.showinfo("Registration Successful", "Registration complete.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while accessing the database: {str(e)}") #error handling via excepts
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}") #error handling via excepts
        finally:
            if connection:
                connection.close()

    @staticmethod
    def checkImp(username, password): #defensise design by checking users inputs with re checks
        if not username or not password:
            messagebox.showerror("Validation Error", "Please enter both username and password.")
            return False
        elif len(username) < 3 or len(password) < 3:
            messagebox.showerror("Validation Error", "Username must be at least 4 characters long, and password must be at least 6 characters long.")
            return False
        elif not re.match("^[a-zA-Z0-9]+$", username):
            messagebox.showerror("Validation Error", "Username can only contain letters and numbers.")
            return False
        elif not re.match("^[a-zA-Z0-9]+$", password):
            messagebox.showerror("Validation Error", "Password can only contain letters and numbers.")
            return False
        return True

    @staticmethod 
    def hashPass(password): #hash algorithm to hash the password inputed
        x = os.urandom(32)
        hashKey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), x, 998123)
        passHashed = salt + hashKey
        return passHashed

    @staticmethod
    def checkPass(passImpt, hashPassStore): #function to compare the hashed password with inputed password
        x = hashPassStore[:32]
        stored_key = hashPassStore[32:]
        hashKey = hashlib.pbkdf2_hmac('sha256', passImpt.encode('utf-8'), x, 998123)
        return hashKey == stored_key

class GlossaryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Glossary")
        self.window.geometry("940x320")  

        self.menu_font = font.Font(family="Helvetica", size=14, weight="bold")

        self.createUI()

    def createUI(self):
        self.create_frame()
        self.create_search_entry()
        self.create_search_button()
        self.create_show_all_button()
        self.create_back_button()
        self.create_output_text()

    def create_frame(self):
        self.glossary_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.glossary_frame.pack(pady=20, padx=20)

    def create_search_entry(self):
        self.entry_search_label = tk.Label(self.glossary_frame, text="search term:", font=self.menu_font, bg="#f0f0f0")
        self.entry_search_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_search = tk.Entry(self.glossary_frame, font=self.menu_font)
        self.entry_search.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.entry_search.bind("<Return>", self.search_entry)

    def create_search_button(self):
        self.search_button = tk.Button(self.glossary_frame, text="search", font=self.menu_font, command=self.search_entry, bg="#90ee90", activebackground="#6aa84f", bd=0)
        self.search_button.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="w")  

    def create_show_all_button(self):
        self.show_all_button = tk.Button(self.glossary_frame, text="show all terms", font=self.menu_font, command=self.show_all_terms, bg="#90ee90", activebackground="#6aa84f", bd=0)
        self.show_all_button.grid(row=0, column=3, padx=(5, 0), pady=5, sticky="w")  

    def create_back_button(self):
        self.back_button = tk.Button(self.glossary_frame, text="back", font=self.menu_font, command=self.window.destroy, bg="#ff6b6b", activebackground="#ff4d4d", bd=0)
        self.back_button.grid(row=0, column=4, padx=(5, 0), pady=5, sticky="w")  

    def create_output_text(self):
        self.text_output = tk.Text(self.glossary_frame, height=10, width=80, font=self.menu_font, state="disabled", bg="white")
        self.text_output.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="w")

    def search_entry(self, event=None):  #main function to search for terms similar to the one input in the table "glossary"
        term = self.entry_search.get().strip()

        if term:
            try:
                connection = sqlite3.connect("physics_data.db") #connects the the programs main database
                cursor = connection.cursor()

                # checks for similar terms
                cursor.execute("SELECT term, definition FROM glossary WHERE term LIKE ?", ('%' + term + '%',))
                results = cursor.fetchall()

                if results:
                    if len(results) == 1:  # check if only one similar term
                        word, definition = results[0]
                        self.text_output.config(state="normal")
                        self.text_output.delete("1.0", "end")
                        self.text_output.insert("end", f"{word}:\n{definition}")
                        self.text_output.config(state="disabled")
                    else:
                        suggested_terms = "\n".join(result[0] for result in results)
                        self.text_output.config(state="normal")
                        self.text_output.delete("1.0", "end")
                        self.text_output.insert("end", f"Suggestions:\n{suggested_terms}")
                        self.text_output.config(state="disabled")
                else:
                    messagebox.showinfo("bad", f"Term '{term}' not found in the glossary.")

            except Exception as e: #error handling via excepts
                messagebox.showerror("bad", f"An error occurred: {str(e)}") 
            finally:
                connection.close()

        else:
            messagebox.showerror("bad", "error add valid search")

    def show_all_terms(self):
        try:
            connection = sqlite3.connect("physics_data.db") #connects to the main database
            cursor = connection.cursor()

            cursor.execute("SELECT term FROM glossary")
            terms = [row[0] for row in cursor.fetchall()] #retrives all terms in the table "glossary"

            # show the terms in the box
            self.text_output.config(state="normal")
            self.text_output.delete("1.0", "end")
            self.text_output.insert("end", "\n".join(terms))
            self.text_output.config(state="disabled")

        except Exception as e: #error handling via excepts
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            connection.close()



class FlashcardsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Flashcards")
        self.window.geometry("600x300")

        self.style = ttk.Style()

        if not self.style.theme_names().__contains__("FlashcardsStyle"):
            self.style.theme_create("FlashcardsStyle", parent="alt", settings={
                "TLabel": {"configure": {"foreground": "#333333", "background": "#E0F2F1"}},
                "TButton": {
                    "configure": {
                        "font": ('Helvetica', 12),
                        "foreground": "#FFFFFF",
                        "background": "#007BFF",
                        "padding": 5,
                        "borderwidth": 1,
                        "relief": "solid",
                        "bordercolor": "#007BFF",
                        "focuscolor": "none",
                        "highlightcolor": "none"
                    }
                },
                "TEntry": {"configure": {"font": ('Helvetica', 12)}},
                "TFrame": {"configure": {"background": "#E0F2F1"}}
            })
        
        self.style.theme_use("FlashcardsStyle") #style made for flashcard window, similar to the one in login menu, the colour is suppose to help with cognitive function


        self.term = None  
        self.createUI()
        self.display_random_flashcard()
        self.correct_count = 0
        self.timer_start = time.time()
        self.update_timer()

        self.check_button_enabled = True  # a flag to track if Check button is enabled

        self.summary_data = []

    def createUI(self):
        self.create_frame()
        self.create_input_entry()
        self.create_check_button()
        self.create_next_button()
        self.create_result_label()
        self.create_back_button()
        self.create_counter_label()
        self.create_timer_label()

        self.window.bind("<Return>", self.check_similarity)

    def create_frame(self):
        self.flashcards_frame = ttk.Frame(self.window, style="TFrame")
        self.flashcards_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.window.configure(background=self.style.lookup("TFrame", "background"))

    def create_input_entry(self):
        self.input_label = ttk.Label(self.flashcards_frame, text="Enter Value:", font=self.menu_font)
        self.input_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.input_entry = ttk.Entry(self.flashcards_frame, font=self.menu_font)
        self.input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def create_check_button(self):
        self.check_button = ttk.Button(self.flashcards_frame, text="Check", command=self.check_similarity)
        self.check_button.grid(row=1, column=2, padx=(5, 0), pady=5, sticky="w")

    def create_next_button(self):
        self.next_button = ttk.Button(self.flashcards_frame, text="Next", command=self.process_next_flashcard)
        self.next_button.grid(row=1, column=3, padx=(5, 0), pady=5, sticky="w")
        self.next_button.grid_remove()  # Hide the next button initially

    def create_result_label(self):
        self.result_label = ttk.Label(self.flashcards_frame, text="", font=self.menu_font, wraplength=550)
        self.result_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="w")

    def create_back_button(self):
        self.back_button = ttk.Button(self.flashcards_frame, text="Back", command=self.window.destroy)
        self.back_button.grid(row=3, column=0, columnspan=4, padx=(5, 0), pady=5, sticky="w")

    def create_counter_label(self):
        self.counter_label = ttk.Label(self.flashcards_frame, text="Correct Answers: 0", font=self.menu_font)
        self.counter_label.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="w")

    def create_timer_label(self):
        self.timer_label = ttk.Label(self.flashcards_frame, text="Timer: 00:00", font=self.menu_font)
        self.timer_label.grid(row=0, column=3, padx=10, pady=5, sticky="e")

    def update_timer(self): #function to make the timer tick and display that live on the screen
        elapsed_time = time.time() - self.timer_start
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.timer_label.config(text=f"Timer: {minutes:02d}:{seconds:02d}")
        self.window.after(1000, self.update_timer)

    def check_similarity(self, event=None): #function to check for similar terms
        if self.check_button_enabled:
            input_value = self.input_entry.get().strip()

            if input_value:
                try:
                    connection = sqlite3.connect("physics_data.db") #connects to the main database of the program
                    cursor = connection.cursor()

                    
                    cursor.execute("SELECT term, definition FROM glossary WHERE term LIKE ?", ('%' + input_value + '%',)) #searching for all similar terms to the term input
                    similar_terms = cursor.fetchall()

                    if len(similar_terms) == 1: 
                        term, definition = similar_terms[0]
                        if term == self.term:
                            self.result_label.config(text="Correct") #in the case where there is only one similar term and that term is the correct term the correct counter increments [+1]
                            self.correct_count += 1
                        else: #if there are multiple similar terms that means the awnser was too vauge causing the program to return incorrect
                            self.result_label.config(text=f"Incorrect. The answer was '{self.term}'")
                        self.counter_label.config(text=f"Correct Answers: {self.correct_count}")
                        self.summary_data.append((term, self.term, self.definition))

                    elif len(similar_terms) == 0:  #if no terms were similar the awnser was incorrect
                        self.result_label.config(text=f"Incorrect. The answer was '{self.term}'")
                        self.summary_data.append((input_value, self.term, self.definition))
                    else: # an expression for error handing for the case we get an un predicted result
                        self.result_label.config(text="Your awnser was too vauge therfore wrong")
                        self.result_label.config(text=f"Incorrect. The answer was '{self.term}'")
                        self.summary_data.append((input_value, self.term, self.definition))

                except Exception as e: #error handling via excepts
                    self.result_label.config(text=f"An error occurred: {str(e)}")
                finally:
                    connection.close()

                self.check_button_enabled = False  # disable Check button
                self.next_button.grid()  # whow Next button
        else:
            messagebox.showinfo("Information", "Please click 'Next' to proceed to the next flashcard.")

    def process_next_flashcard(self):
        self.input_entry.delete(0, tk.END)  # clear the text entry
        self.result_label.config(text="")  # clear the result label
        self.next_button.grid_remove()  # hide the next button
        self.display_random_flashcard()  # display a new flashcard
        self.check_button_enabled = True  # enable Check button

    def display_random_flashcard(self):
        try:
            connection = sqlite3.connect("physics_data.db") #connect to the main database
            cursor = connection.cursor()

            cursor.execute("SELECT term, definition FROM glossary ORDER BY RANDOM() LIMIT 1") #selects a random term in the table "glossary"
            term, definition = cursor.fetchone()

            self.term = term  
            self.definition = definition
            # split the definition into multiple lines so it doesn't overflow the screen
            lines = [definition[i:i+50] for i in range(0, len(definition), 50)]  
            formatted_definition = "\n".join(lines)
            self.result_label.config(text=formatted_definition)

        except Exception as e: #error handling via excepts
            self.result_label.config(text=f"An error occurred: {str(e)}")
        finally:
            connection.close()

    def close_window(self):
        self.window.destroy()  # close the Flashcards window
        elapsed_time = time.time() - self.timer_start
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        self.timer_text = f"Timer: {minutes:02d}:{seconds:02d}" #stores timer data to pass onto the summary window
        SummaryWindow(self.parent, self.summary_data, self.correct_count, self.timer_text)  # open the Summary window


class SummaryWindow:
    def __init__(self, parent, data, correct_count, timer_text):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Summary")
        self.window.geometry("600x300")

        self.menu_font = font.Font(family="Helvetica", size=14, weight="bold")

        self.createUI(data, correct_count, timer_text)

    def createUI(self, data, correct_count, timer):
        ttk.Label(self.window, text="Summary", font=self.menu_font).pack()

        ttk.Label(self.window, text=f"Correct Answers: {correct_count}", font=self.menu_font).pack()

        ttk.Label(self.window, text=timer, font=self.menu_font).pack()

        tree = ttk.Treeview(self.window, columns=("Entered Value", "Correct Value", "Definition"), show="headings") 
        #displaying the data presented as a tree
        for col in ("Entered Value", "Correct Value", "Definition"):
            tree.heading(col, text=col)

        for item in data:
            tree.insert("", "end", values=item)

        tree.pack(fill="both", expand=True)



class Task: #function to create and "object" of "task" with the provided data
    def __init__(self, description, category, priority, due_date):
        self.description = description
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.completed = False

class RevisionPlannerWindow:
    def __init__(self, parent, UID):
        self.parent = parent
        self.UID = UID
        self.window = tk.Toplevel(parent)
        self.window.title("Revision Planner")
        self.window.geometry("1200x670")

        self.menu_font = font.Font(family="Helvetica", size=14, weight="bold") #set the font for the window

        self.tasks = []  

        self.createUI()
        self.load_planner() 

    def createUI(self):
        self.create_frame()
        self.create_task_entry()
        self.create_category_dropdown()
        self.create_priority_dropdown()
        self.create_due_date_picker()
        self.create_add_task_button()
        self.create_task_list()
        self.create_back_button()
        self.create_status_label()  

    def create_frame(self):
        self.planner_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.planner_frame.pack(expand=True, fill="both", padx=20, pady=20)

    def create_task_entry(self):
        self.task_entry_label = tk.Label(self.planner_frame, text="Task:", font=self.menu_font, bg="#f0f0f0")
        self.task_entry_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.task_entry = tk.Entry(self.planner_frame, font=self.menu_font, width=30)
        self.task_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    def create_category_dropdown(self):
        self.category_label = tk.Label(self.planner_frame, text="Category:", font=self.menu_font, bg="#f0f0f0")
        self.category_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.category_var = tk.StringVar(self.planner_frame)
        self.category_var.set("Select Category")
        self.category_dropdown = tk.OptionMenu(self.planner_frame, self.category_var, "Study", "Practice", "Review") #creates the dropdown [optionmenu] with the options "study","practice","review"
        self.category_dropdown.config(font=self.menu_font)
        self.category_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    def create_priority_dropdown(self):
        self.priority_label = tk.Label(self.planner_frame, text="Priority:", font=self.menu_font, bg="#f0f0f0")
        self.priority_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.priority_var = tk.StringVar(self.planner_frame)
        self.priority_var.set("Select Priority")
        self.priority_dropdown = tk.OptionMenu(self.planner_frame, self.priority_var, "High", "Medium", "Low") #creates the dropdown [optionmenu] with the options "high","medium","low"
        self.priority_dropdown.config(font=self.menu_font)
        self.priority_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def create_due_date_picker(self):
        self.due_date_label = tk.Label(self.planner_frame, text="Due Date:", font=self.menu_font, bg="#f0f0f0")
        self.due_date_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.due_date_picker = DateEntry(self.planner_frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=2024) #creates the calendar pop out
        self.due_date_picker.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    def create_add_task_button(self):
        self.add_task_button = tk.Button(self.planner_frame, text="Add Task", font=self.menu_font, command=self.add_task, bg="#90ee90", activebackground="#6aa84f", bd=0)
        self.add_task_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def create_task_list(self):
        self.task_list_label = tk.Label(self.planner_frame, text="Tasks:", font=self.menu_font, bg="#f0f0f0")
        self.task_list_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.task_treeview = ttk.Treeview(self.planner_frame, columns=("Description", "Category", "Priority", "Due Date", "Completed"), show="headings", height=10)
        self.task_treeview.heading("Description", text="Description")
        self.task_treeview.heading("Category", text="Category")
        self.task_treeview.heading("Priority", text="Priority")
        self.task_treeview.heading("Due Date", text="Due Date")
        self.task_treeview.heading("Completed", text="Completed")
        self.task_treeview.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.task_treeview.bind("<ButtonRelease-1>", self.on_select)

        self.mark_complete_button = tk.Button(self.planner_frame, text="Mark as Complete", font=self.menu_font, command=self.mark_as_complete, bg="#90ee90", activebackground="#6aa84f", bd=0)
        self.mark_complete_button.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        self.delete_task_button = tk.Button(self.planner_frame, text="Delete Task", font=self.menu_font, command=self.delete_task, bg="#ff6b6b", activebackground="#ff4d4d", bd=0)
        self.delete_task_button.grid(row=7, column=1, padx=10, pady=5, sticky="w")

    def create_back_button(self):
        self.back_button = tk.Button(self.planner_frame, text="Back", font=self.menu_font, command=self.window.destroy, bg="#ff6b6b", activebackground="#ff4d4d", bd=0)
        self.back_button.grid(row=8, column=1, padx=10, pady=5, sticky="e")

    def create_status_label(self):
        self.status_label = tk.Label(self.planner_frame, text="", font=self.menu_font, fg="green", bg="#f0f0f0")
        self.status_label.grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    def add_task(self):
        description = self.task_entry.get()
        category = self.category_var.get()
        priority = self.priority_var.get()
        due_date = self.due_date_picker.get_date()

        if description:
            new_task = Task(description, category, priority, due_date)
            self.tasks.append(new_task)
            self.update_task_list()
            self.clear_task_entry()
            self.save_planner()  # autosave when a task is added
            self.show_status("Task added successfully.")
        else:
            self.show_status("Please enter a task description.")

    def update_task_list(self):
        self.task_treeview.delete(*self.task_treeview.get_children()) #another demonstration of tree traversal
        for task in self.tasks:
            completed_status = "Yes" if task.completed else "No"
            self.task_treeview.insert("", "end", values=(task.description, task.category, task.priority, task.due_date.strftime("%Y-%m-%d"), completed_status))

    def on_select(self, event):
        selected_items = self.task_treeview.selection()
        if selected_items:  # check if any item is selected
            item = selected_items[0]
            index = self.task_treeview.index(item)
            task = self.tasks[index]
            self.selected_task = task 

    def mark_as_complete(self):
        if self.selected_task:
            self.selected_task.completed = not self.selected_task.completed
            self.update_task_list()
            self.save_planner()  # autosave when a task is marked as complete
            self.show_status("Task marked as complete.")

    def delete_task(self):
        if self.selected_task:
            self.tasks.remove(self.selected_task)
            self.update_task_list()
            self.save_planner()  # autosave when a task is deleted
            self.show_status("Task deleted successfully.")

    def clear_task_entry(self):
        self.task_entry.delete(0, tk.END)

    def save_planner(self):
        try:
            connection = sqlite3.connect("physics_data.db") # connects to the main database
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS tasks (UID INTEGER, description TEXT, category TEXT, priority TEXT, due_date TEXT, completed INTEGER)") #creates the second table of the database "tasks"

            # clear existing data for the current user
            cursor.execute("DELETE FROM tasks WHERE UID = ?", (self.UID,))

            # insert new data for the current user
            for task in self.tasks:
                completed_value = 1 if task.completed else 0
                cursor.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)", (self.UID, task.description, task.category, task.priority, task.due_date.strftime("%Y-%m-%d"), completed_value))

            connection.commit()
            self.show_status("Revision planner saved successfully.")
        except Exception as e: #error handling via exceptions
            self.show_status(f"An error occurred while saving the planner: {str(e)}")
        finally:
            connection.close()

    def load_planner(self):
        try:
            connection = sqlite3.connect("physics_data.db") #connect to the main database
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS tasks (UID INTEGER, description TEXT, category TEXT, priority TEXT, due_date TEXT, completed INTEGER)")

            cursor.execute("SELECT * FROM tasks WHERE UID = ?", (self.UID,)) #retrives all the task data paired with the current UID of the user logged in
            planner_data = cursor.fetchall()

            for task_data in planner_data: #breaking down the retrived data into its own segments , using the data to make a task object and then displaying that data accordingly
                _, description, category, priority, due_date_str, completed_value = task_data
                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                completed = bool(completed_value)
                task = Task(description, category, priority, due_date)
                task.completed = completed
                self.tasks.append(task)

            self.update_task_list()
            self.show_status("Planner loaded successfully.")
        except Exception as e: #error handling via exceptions
            self.show_status(f"An error occurred while loading the planner: {str(e)}")
        finally:
            connection.close()

    def show_status(self, message):
        self.status_label.config(text=message)




class GlossaryEditorWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = Toplevel(parent)
        self.window.title("Physics Glossary Editor")
        self.window.geometry("1000x645")  
        self.window.resizable(False, False)

        # connect to the main database
        self.connection = sqlite3.connect("physics_data.db")
        self.cursor = self.connection.cursor()
        self.create_glossary_table()
        self.glossary_frame = Frame(self.window)

        # create Treeview to display database content, another demonstration of tree traversal
        self.tree = ttk.Treeview(self.glossary_frame, columns=("Term", "Definition"), show="headings", height=20)
        self.tree.heading("Term", text="Term")
        self.tree.heading("Definition", text="Definition")
        self.tree.column("Term", width=300)
        self.tree.column("Definition", width=600)  
        self.tree.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.glossary_frame, orient="vertical", command=self.tree.yview) # scrollbar creation
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set) 
        self.load_data() # Get data from the database and insert into the Treeview
        self.entry_term = Entry(self.glossary_frame, width=30)   # entry fields for adding terms
        self.entry_term.pack(pady=5)
        self.entry_definition = Entry(self.glossary_frame, width=30)
        self.entry_definition.pack(pady=5)
        self.add_button = Button(self.glossary_frame, text="Add Term", command=self.add_term)# buttons to add and remove terms
        self.add_button.pack(pady=5)
        self.remove_button = Button(self.glossary_frame, text="Remove Selected Term", command=self.remove_selected_term)
        self.remove_button.pack(pady=5)
        self.back_button = Button(self.glossary_frame, text="Back", command=self.close_window) # button to close the window
        self.back_button.pack(pady=5)
        self.status_label = Label(self.glossary_frame, text="", fg="black")
        self.status_label.pack()
        self.glossary_frame.pack(padx=20, pady=20)

    def create_glossary_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS glossary (
                    id INTEGER PRIMARY KEY,
                    term TEXT,
                    definition TEXT
                )
            """)# creates the third and final table in the database "glossary"
            self.connection.commit()
        except sqlite3.Error as e: #error handling via exceptions
            print("Error creating glossary table:", e)

    def load_data(self): #uses the data from the database and loads it into a treeview
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT term, definition FROM glossary")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1]))

    def add_term(self): #allows for adding terms into the database
        term = self.entry_term.get()
        definition = self.entry_definition.get()
        if term and definition:
            self.cursor.execute("INSERT INTO glossary (term, definition) VALUES (?, ?)", (term, definition)) #the sql query to add the term and definition into the table
            self.connection.commit()
            self.status_label.config(text="Term added successfully", fg="green")
            self.entry_term.delete(0, "end")
            self.entry_definition.delete(0, "end")
            self.load_data()  # refresh the displayed data after adding
        else:
            self.status_label.config(text="Please enter both term and definition", fg="red")

    def remove_selected_term(self): # function to remove the selected term from the database
        selected_item = self.tree.selection()
        if selected_item:
            term_to_remove = self.tree.item(selected_item, "values")[0]
            self.cursor.execute("DELETE FROM glossary WHERE term=?", (term_to_remove,))
            self.connection.commit()
            self.status_label.config(text="Term removed successfully", fg="green")
            self.load_data()  # refresh the displayed data after removing
        else:
            self.status_label.config(text="Please select a term to remove", fg="red")

    def close_window(self):
        self.window.destroy()


class PhysicsRevisionHelper: #main window which acts as the bug
    def __init__(self, root, UID):
        self.root = root
        self.UID = UID
        self.root.title("Physics Revision Helper")
        self.menu_font = font.Font(family="Helvetica", size=14, weight="bold")

        self.create_menu_frame()

    def create_menu_frame(self):
        self.menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.menu_frame.pack(expand=True, fill="both", padx=20, pady=(20, 0))

        self.button_images = {
            "Glossary": ImageTk.PhotoImage(Image.open("glossary.png").resize((40, 40))),
            "Flashcards": ImageTk.PhotoImage(Image.open("flashcards.png").resize((40, 40))),
            "Revision Planner": ImageTk.PhotoImage(Image.open("planner.png").resize((40, 40))),
            "Formula Reference": ImageTk.PhotoImage(Image.open("formula.png").resize((40, 40))),
            "Glossary Editor": ImageTk.PhotoImage(Image.open("graph.png").resize((40, 40))),
        } #adds all the images ontop of the buttons in the menu

        self.create_menu_buttons()

    def create_menu_buttons(self):
        glossaryBtn = tk.Button(self.menu_frame, image=self.button_images["Glossary"], text="Glossary", font=self.menu_font, compound="top", command=self.opnGlossary, bg="#f0f0f0", bd=0)
        glossaryBtn.grid(row=0, column=0, padx=10, pady=5)
        flashcardsBtn = tk.Button(self.menu_frame, image=self.button_images["Flashcards"], text="Flashcards", font=self.menu_font, compound="top", command=self.opnFlashcards, bg="#f0f0f0", bd=0)
        flashcardsBtn.grid(row=0, column=1, padx=10, pady=5)
        revisionPlannerBtn = tk.Button(self.menu_frame, image=self.button_images["Revision Planner"], text="Revision Planner", font=self.menu_font, compound="top", command=lambda: self.opnRevPlanner(self.UID), bg="#f0f0f0", bd=0)
        revisionPlannerBtn.grid(row=0, column=2, padx=10, pady=5)
        glossaryEditorBtn = tk.Button(self.menu_frame, image=self.button_images["Glossary Editor"], text="Glossary Editor", font=self.menu_font, compound="top", command=self.opnGlossEditor, bg="#f0f0f0", bd=0)
        glossaryEditorBtn.grid(row=0, column=3, padx=10, pady=5)    
        formulaReferenceBtn = tk.Button(self.menu_frame, image=self.button_images["Formula Reference"], text="Formula Reference", font=self.menu_font, compound="top", command=self.opnFormulaReference, bg="#f0f0f0", bd=0)
        formulaReferenceBtn.grid(row=0, column=4, padx=10, pady=5)

    def opnGlossary(self):
        GlossaryWindow(self.root)

    def opnFlashcards(self):
        flashcards_window = FlashcardsWindow(self.root)
        flashcards_window.window.protocol("WM_DELETE_WINDOW", flashcards_window.close_window)

    def opnRevPlanner(self, UID):
        RevisionPlannerWindow(self.root, UID)

    def opnGlossEditor(self):
        GlossaryEditorWindow(self.root)

    def opnFormulaReference(self):
        url = "https://www.ocr.org.uk/Images/363796-units-h156-and-h556-data-formulae-and-relationships-booklet.pdf"
        webbrowser.open_new(url)


if __name__ == "__main__": #mainloop for the program to run
    root = tk.Tk()
    login_menu = LoginMenu(root)
    root.mainloop()
