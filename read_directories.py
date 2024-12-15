#Import libraries
import os 
from mne.time_frequency import tfr_morlet
import classes as c

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

file_extension = ".edf"
dataset_path = ""

def set_eeg_file_extension(eeg_file_extension):
    """Function for changing eeg file extension, called from pipeline_manager"""
    global file_extension
    file_extension = eeg_file_extension
    
def set_dataset_path(dataset_path_):
    """Function for setting the global dataset_path parameter"""
    global dataset_path
    dataset_path = dataset_path_
    
    
def get_participant_list(dataset_path):
    """ Returns a list of participant objects based on the given path to a BIDS-compliant dataset"""
    participant_dir_list = get_dir_list(dataset_path)
    
    #If the data is BIDS-compliant either all subjects will have folders for sessions called "ses_id" or 
    #none of them will.
    #This function checks for the very first participant in the list.
    participant_path = os.path.join(dataset_path, participant_dir_list[0])
    has_multiple_sessions = check_for_multiple_sessions(participant_path)
    
    participant_list = []
        
    for participant in participant_dir_list:
        sub_id = participant
        new_participant = create_participant_obj(sub_id, os.path.join(dataset_path, participant), has_multiple_sessions)
        try:
            if (len(new_participant.get_sessions()[0].get_run_list()) > 0):
                participant_list.append(new_participant)
        except Exception as e:
            print(f"Error in creating participant based on directory: {sub_id}. Directory might not comply to BIDS standard and is skipped.")
    
    return participant_list
    
    
def create_participant_obj(sub_id, participant_path, has_multiple_sessions):
    if is_subject_directory(sub_id):
        participant = c.Participant(sub_id, participant_path, has_multiple_sessions)
        session_list = create_session_list(sub_id, participant, participant_path, has_multiple_sessions)
        participant.set_session_list(session_list)
        return participant
    
def create_session_list(sub_id, participant, participant_path, has_multiple_sessions):
    session_list = [] # list of session objects
    session_paths = [] # list of session paths
    session_ids = []
    # this if-else ensures we can handle both multiple sessions and one session
    # if-block loops through all directories in the participant folder, find session folders and
    # adds then to a list of session paths. Else-block just saves a singular participant path
    if has_multiple_sessions:
        participant_directories = get_dir_list(participant_path)
        for dir in participant_directories:
          if(is_session_directory(dir)):
            session_paths.append(os.path.join(participant_path, dir, "eeg"))
            session_ids.append(dir)
    elif not has_multiple_sessions:
        session_paths.append(os.path.join(participant_path, "eeg"))
        session_ids.append("") # Rename later
    index = 0
    for session_path in session_paths:
        run_paths_list = get_run_path_list(session_path)
        session_id = session_ids[index]
        session_list.append(create_session_obj(participant, session_id, run_paths_list, session_path))
        index += 1
    return session_list
    
def create_session_obj(participant, session_id, run_paths_list, session_path):
    session = c.Session(participant, session_id, session_path)
    run_list = create_run_list(run_paths_list, session)
    session.set_run_list(run_list)
    return session

def create_run_list(run_paths_list, session):
    run_list = []
    id = 0
    run_paths_list.sort()
    for run_path in run_paths_list:
        run_id = "run-" + str(id)
        run_list.append(c.Run(run_id, run_path, session))
        id +=1
    return run_list

# a list of names of all contents of a folder (that are not starting with a . (eg. .env))
def get_contents_list_helper(directory_in_str):
    directories = []

    pathlist = os.listdir(directory_in_str)
    
    for path in pathlist:
        # skipping any filenames/directorynames that starts with a dot, since this will be mac system folder or file 
        if path.startswith("."):
            continue  
        directories.append(path)
        
    # directories = [path for path in pathlist if not path.startswith(".")]

    return directories

# a list of names of all directores in a folder (that are not starting with a . (eg. .env))
def get_dir_list(directory_path_in_string):
    directories = []
    dir_and_files = get_contents_list_helper(directory_path_in_string)
    for dir in dir_and_files:
        if "." in dir:
            continue
        directories.append(dir)
    return directories

# a list of names of all eeg files in a given folder
def get_run_path_list(eeg_directory_path):
    eeg_files = [] 
    try: 
        dir_and_files = get_contents_list_helper(eeg_directory_path)
        for elem in dir_and_files:
            if file_extension in elem:
                eeg_files.append(os.path.join(eeg_directory_path, elem))
    except:
        print("The directory" + eeg_directory_path + " does not exist. It seems this participant does not have an eeg folder.")
    finally: 
        return eeg_files
    

def check_for_multiple_sessions(participant_path):
    """ Given a participant directory this functions checks if there are multiple 
    sessions for the participant and returns a boolean."""
    dir_list = get_dir_list(participant_path)
    multiple_sessions = False
    for dir in dir_list: 
        if is_session_directory(dir):
            multiple_sessions = True
            break
    return multiple_sessions

def is_session_directory(dir):
    return dir.startswith("ses")

def is_subject_directory(dir):
    return dir.startswith("sub")

