import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import requests
import pandas as pd
from PIL import Image, ImageTk
import time
from IPython.display import display, Image
from utils import start_driver, pt_search_scrape, process_and_match_data
from paths import get_mrn_paths

class MIPApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MIP Patient Data Acquisition')
        self.root.geometry("700x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.template_path = None
        self.mrn_path = None
        self.output_path = None
        self.excel_path = None
        self.new_window = None

        self.edData = []

        self.create_login_window()

    def create_login_window(self):
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
                self.create_selection_page(username, password)
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')

    def create_selection_page(self, username, password):
        if self.new_window is not None:
            self.new_window.destroy()
        
        self.new_window = ctk.CTkToplevel()
        self.new_window.title("Select Entry Method")
        self.new_window.geometry("400x300")
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        manual_button = ctk.CTkButton(self.new_window, text="Manually Enter Patient IDs and Sides", font=("Helvetica", 14),
                                      command=lambda: self.create_manual_entry_page(username, password))
        manual_button.pack(pady=20)

        upload_button = ctk.CTkButton(self.new_window, text="Upload Excel File", font=("Helvetica", 14),
                                      command=lambda: self.create_upload_entry_page(username, password))
        upload_button.pack(pady=20)

    def create_manual_entry_page(self, username, password):
        self.new_window.withdraw()
        self.new_window = ctk.CTkToplevel()
        self.new_window.title("Enter Patient IDs and Sides")
        self.new_window.geometry("700x600")
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

        choose_mrn_button = ctk.CTkButton(self.new_window, text="Choose MRN File", font=("Helvetica", 14), command=self.choose_mrn_file)
        choose_mrn_button.pack(pady=10)

        choose_output_button = ctk.CTkButton(self.new_window, text="Choose Output File Location", font=("Helvetica", 14), command=self.choose_output_location)
        choose_output_button.pack(pady=10)

        collect_button = ctk.CTkButton(self.new_window, text="Collect Data", font=("Helvetica", 14), command=lambda: self.collect_data(username, password))
        collect_button.pack(pady=20)

        back_button = ctk.CTkButton(self.new_window, text="Back", font=("Helvetica", 14), command=lambda: self.go_back_to_selection_page(username, password))
        back_button.pack(pady=10)

    def create_upload_entry_page(self, username, password):
        self.new_window.withdraw()
        self.new_window = ctk.CTkToplevel()
        self.new_window.title("Upload Patient Data")
        self.new_window.geometry("700x600")
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        choose_excel_button = ctk.CTkButton(self.new_window, text="Choose Excel File", font=("Helvetica", 14), command=self.choose_excel_file)
        choose_excel_button.pack(pady=20)

        choose_template_button = ctk.CTkButton(self.new_window, text="Choose Template File", font=("Helvetica", 14), command=self.choose_template_file)
        choose_template_button.pack(pady=20)

        choose_mrn_button = ctk.CTkButton(self.new_window, text="Choose MRN File", font=("Helvetica", 14), command=self.choose_mrn_file)
        choose_mrn_button.pack(pady=10)

        choose_output_button = ctk.CTkButton(self.new_window, text="Choose Output File Location", font=("Helvetica", 14), command=self.choose_output_location)
        choose_output_button.pack(pady=20)

        disclaimer_label = ctk.CTkLabel(self.new_window, text="Note: No more than 20 entries at a time.", font=("Helvetica", 16))
        disclaimer_label.pack(pady=10)

        collect_button = ctk.CTkButton(self.new_window, text="Collect Data", font=("Helvetica", 14), command=lambda: self.collect_data_from_excel(username, password))
        collect_button.pack(pady=20)

        back_button = ctk.CTkButton(self.new_window, text="Back", font=("Helvetica", 14), command=lambda: self.go_back_to_selection_page(username, password))
        back_button.pack(pady=10)

    def go_back_to_selection_page(self, username, password):
        self.new_window.destroy()
        self.create_selection_page(username, password)

    def choose_template_file(self):
        self.template_path = filedialog.askopenfilename(title="Select RedCAP CSV Import Template")

    def choose_mrn_file(self):
        self.mrn_path = filedialog.askopenfilename(title="Choose MRN Matching Path")

    def choose_output_location(self):
        self.output_path = filedialog.asksaveasfilename(title="Choose Output File Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    def choose_excel_file(self):
        self.excel_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx;*.xls")])

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

        self.start_collection(data, username, password)

    def collect_data_from_excel(self, username, password):
        if not self.excel_path:
            messagebox.showerror("Error", "Please choose an Excel file.")
            return

        df = pd.read_excel(self.excel_path)
        if len(df) > 20:
            messagebox.showerror("Error", "Please ensure there are no more than 20 entries in the Excel file.")
            return

        data = list(zip(df['Patient ID'], df['Side']))
        self.start_collection_from_excel(data, username, password)

    def start_collection(self, data, username, password):
        messagebox.showinfo("Please Wait", f"Collecting data for {len(data)} entries. This may take around {45 * len(data)} seconds.")

        auth_url = f'http://{username}:{password}@mipresearch.org/otopilot/MUSC2/index.php?p=Tool.getPatientTable'
        driver = start_driver(auth_url)

        for patient_id, side in data:
            try:
                pt_search_scrape(patient_id, side, driver, self.edData)
                time.sleep(3)
            except Exception as e:
                time.sleep(3)
                driver = start_driver(auth_url)
                try:
                    pt_search_scrape(patient_id, side, driver, self.edData)
                    time.sleep(3)
                except Exception as e:
                    messagebox.showerror('Error', f'Instance failed for Patient ID: {patient_id} due to {e}')
                    continue

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

        process_and_match_data(dfED, self.template_path, self.output_path, self.mrn_path)
        messagebox.showinfo("Success", "Data collection completed successfully!")

    def start_collection_from_excel(self, data, username, password):
        messagebox.showinfo("Please Wait", f"Collecting data for {len(data)} entries. This may take around {45 * len(data)} seconds.")
        
        try:
            auth_url = f'http://{username}:{password}@mipresearch.org/otopilot/MUSC2/index.php?p=Tool.getPatientTable'
            driver = start_driver(auth_url)

            for patient_id, side in data:
                try:
                    pt_search_scrape(patient_id, side, driver, self.edData)
                    time.sleep(3)
                except Exception as e:
                    time.sleep(3)
                    driver = start_driver(auth_url)
                    try:
                        pt_search_scrape(patient_id, side, driver, self.edData)
                        time.sleep(3)
                    except Exception as e:
                        messagebox.showerror('Error', f'Instance failed for Patient ID: {patient_id} due to {e}')
                        continue

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

            process_and_match_data(dfED, self.template_path, self.output_path, self.mrn_path)
            messagebox.showinfo("Success", "Data collection completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing the Excel file: {e}")

    def on_closing(self):
        if self.new_window is not None:
            self.new_window.destroy()
        self.root.destroy()

if __name__ == "__main__":
    #computer_choice = input("Which computer are you using? (Enter 'mac' or 'pc'): ").strip().lower()
    #mrn_path = MIPApp.mrn_path

    root = ctk.CTk()
    app = MIPApp(root)
    root.mainloop()
