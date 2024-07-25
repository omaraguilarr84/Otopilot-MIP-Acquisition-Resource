import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import requests
import pandas as pd
from utils import start_driver, pt_search_scrape, process_and_match_data
from paths import get_mrn_paths

class MIPApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MIP Patient Data Acquisition')
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.template_path = None
        self.output_path = None
        self.new_window = None

        self.edData = []

        self.create_main_window()

    def create_main_window(self):
        form_frame = ctk.CTkFrame(self.root)
        form_frame.pack(pady=20)

        username_label = ctk.CTkLabel(form_frame, text="Username:", font=("Helvetica", 14))
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14), width=200)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        password_label = ctk.CTkLabel(form_frame, text="Password:", font=("Helvetica", 14))
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14), show="*", width=200)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        si_button = ctk.CTkButton(self.root, text="Sign-In", font=("Helvetica", 14), command=self.sign_in)
        si_button.pack(pady=20)

    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.auth(username, password)

    def auth(self, username, password):
        try:
            url = f'http://{username}:{password}@mipresearch.org/otopilot/MUSC2/index.php?p=Tool.getPatientTable'
            response = requests.get(url)
            if response.status_code != 200:
                messagebox.showerror('Error', 'Invalid username or password. Please try again.')
            else:
                self.root.withdraw()
                self.open_new_window(username, password)
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')

    def open_new_window(self, username, password):
        self.new_window = ctk.CTkToplevel()
        self.new_window.title("Enter Patient IDs and Sides")
        self.new_window.geometry("600x400")
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        instructions_label = ctk.CTkLabel(self.new_window, text="Enter Patient IDs and Sides:", font=("Helvetica", 12))
        instructions_label.pack(pady=10)

        self.entries_frame = ctk.CTkFrame(self.new_window)
        self.entries_frame.pack(pady=10)

        self.add_entry_row()

        add_button = ctk.CTkButton(self.new_window, text="Add Entry", font=("Helvetica", 14), command=self.add_entry_row)
        add_button.pack(pady=10)

        choose_template_button = ctk.CTkButton(self.new_window, text="Choose Template File", font=("Helvetica", 14), command=self.choose_template_file)
        choose_template_button.pack(pady=10)

        choose_output_button = ctk.CTkButton(self.new_window, text="Choose Output File Location", font=("Helvetica", 14), command=self.choose_output_location)
        choose_output_button.pack(pady=10)

        collect_button = ctk.CTkButton(self.new_window, text="Collect Data", font=("Helvetica", 14), command=lambda: self.collect_data(username, password))
        collect_button.pack(pady=20)

    def choose_template_file(self):
        self.template_path = filedialog.askopenfilename(title="Select RedCAP CSV Import Template")

    def choose_output_location(self):
        self.output_path = filedialog.asksaveasfilename(title="Choose Output File Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    def add_entry_row(self):
        row = len(self.entries_frame.winfo_children()) // 4
        patient_id_label = ctk.CTkLabel(self.entries_frame, text=f"Patient ID {row + 1}:", font=("Helvetica", 12))
        patient_id_label.grid(row=row, column=0, padx=10, pady=5, sticky="e")

        patient_id_entry = ctk.CTkEntry(self.entries_frame, font=("Helvetica", 14), width=150)
        patient_id_entry.grid(row=row, column=1, padx=10, pady=5)

        side_label = ctk.CTkLabel(self.entries_frame, text=f"Side {row + 1}:", font=("Helvetica", 12))
        side_label.grid(row=row, column=2, padx=10, pady=5, sticky="e")

        side_entry = ctk.CTkEntry(self.entries_frame, font=("Helvetica", 14), width=150)
        side_entry.grid(row=row, column=3, padx=10, pady=5)

    def collect_data(self, username, password):
        entries = self.entries_frame.winfo_children()
        data = []

        for i in range(0, len(entries), 4):
            patient_id = entries[i + 1].get()
            side = entries[i + 3].get()
            data.append((patient_id, side))

        print('Starting driver')
        auth_url = f'http://{username}:{password}@mipresearch.org/otopilot/MUSC2/index.php?p=Tool.getPatientTable'
        driver = start_driver(auth_url)

        for patient_id, side in data:
            pt_search_scrape(patient_id, side, driver, self.edData)

        driver.quit()

        processedData = {}
        for data in self.edData:
            patient_id = data['Patient ID']
            if patient_id not in processedData:
                processedData[patient_id] = []
            processedData[patient_id].append(data)

        formattedData = []
        for patient_id, electrodes in processedData.items():
            formatted_row = {'Patient ID': patient_id}
            for i, electrode in enumerate(electrodes):
                formatted_row[f'Electrode Number {i+1}'] = electrode['Electrode Number']
                formatted_row[f'Distance {i+1}'] = electrode['Distance']
                formatted_row[f'Angle {i+1}'] = electrode['Angle']
                formatted_row[f'Place Frequency {i+1}'] = electrode['Place Frequency']
                formatted_row[f'Channel Frequency {i+1}'] = electrode['Channel Frequency']
                formatted_row[f'Scalar Location {i+1}'] = electrode['Scalar Location']
            formattedData.append(formatted_row)

        dfED = pd.DataFrame(formattedData)

        process_and_match_data(dfED, self.template_path, self.output_path, mrn_path, mrn_path2)

    def on_closing(self):
        if self.new_window is not None:
            self.new_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    computer_choice = input("Which computer are you using? (Enter 'mac' or 'pc'): ").strip().lower()
    mrn_path, mrn_path2 = get_mrn_paths(computer_choice)

    root = ctk.CTk()
    app = MIPApp(root)
    root.mainloop()
