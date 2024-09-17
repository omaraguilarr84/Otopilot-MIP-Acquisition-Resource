# Otopilot-MIP-Acquisition-Resource
This is an application that uses the Custom tkinter library and selenium to scrape electrode data from MUSC's otopilot web database. Below is the information needed to setup and run the application. If you have any questions about using the application, or suggestions for updates, please contact Omar Aguilar via email: oaguilar6@gatech.edu.

# Setup
- Go to releases on right hand side, and download the latest version of the application.
- There might be a popup from Windows security saying that you should not download. Click "More Info", and "Run anyway".
- Once the .exe file is downloaded, it is ready for use.

# Using the Application
- You will have to login to the application using the same credentials that you currently use to access the MIP web database.
- Once you login, you will be given two options: entering Patient IDs manually or uploading an excel file with patient IDs listed. See more below on the requirements for uploading an excel sheet or entering patient ID's manually.
- Once you have either uploaded your patient IDs and the corresponding sides for their implants, you will be asked to upload a few more files: the csv import template and MRN matching file. (Please let me know once the csv import template for REDCap is stabilized, and I can embed this into the application -- I will leave a template below. As for the MRN matching file, it is dynamically updated, so there is no way of embedding this)
- You will also have to choose where your REDCap import will be placed on your computer. The application will save the CSV to this location, and it will be ready for uploading to the REDCap database (please check that all of the correct Patient IDs have been fulfilled with their corresponding electrode data).
- Lastly, click "Collect Data". Please do not interfere with this process, as it can cause the program to crash. It should take around 45 seconds to complete the collection for each patient ID.

**Uploading an Excel File for Patient ID Entry**
- 
