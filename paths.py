def get_mrn_paths(computer_choice):
    if computer_choice == 'mac':
        mrn_path = '/Users/omaraguilarjr/Summer_24/musc_ent/Data/mrnMatch/MRNxMIPID.xlsx'
        mrn_path2 = '/Users/omaraguilarjr/Summer_24/musc_ent/Data/mrnMatch/Cochlear implant CT database (1).xlsx'
    elif computer_choice == 'pc':
        mrn_path = 'c:\\Users\\omarh\\Documents\\Summer 24 - MUSC\\musc_ent\\Data\\mrnMatch\\MRNxMIPID.xlsx'
        mrn_path2 = 'c:\\Users\\omarh\\Documents\\Summer 24 - MUSC\\musc_ent\\Data\\mrnMatch\\Cochlear implant CT database (1).xlsx'
    else:
        print("Invalid input. Please restart the script and enter 'mac' or 'pc'.")
        exit()

    return mrn_path, mrn_path2
