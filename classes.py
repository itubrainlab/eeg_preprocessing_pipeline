import pipeline_manager as pln
import os

class Participant:

    def __init__(self, sub_id, participant_path, has_multiple_sessions):
        self.sub_id = sub_id
        self.session_list = []
        self.participant_path = participant_path
        self.has_multiple_sessions_ = has_multiple_sessions
        self.create_sub_report_dir()
    
    def get_sub_id(self):
        return self.sub_id

    def get_sessions(self):
        return self.session_list
    
    def has_multiple_sessions(self):
        return self.has_multiple_sessions_
    
    def set_session_list(self, session_list):
        self.session_list = session_list
        
    def create_sub_report_dir(self):
        report_dir = os.path.join("report", self.sub_id)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        


class Session:

    def __init__(self, participant, session_id, session_path):
        self.report_dir = ""
        self.fif_dir = ""
        self.participant = participant
        self.session_id = session_id
        self.run_list = []
        self.session_path = session_path
        self.report_path = self.create_session_report_dir()
        self.log_filepath = ""

    def get_session_id(self):
        return self.session_id
    
    def get_run_list(self):
        return self.run_list
    
    def get_sub_id(self):
        return self.participant.get_sub_id()
    
    def set_run_paths(self, run_paths):
        self.run_list = run_paths
        
    def set_run_list(self, run_list):
        self.run_list = run_list

    def get_report_path(self):
        return self.report_path
    
    def create_session_report_dir(self):
        if self.participant.has_multiple_sessions():
            session_report_filename = self.participant.get_sub_id() + "_" + self.session_id + "_report.md"
        else: 
            session_report_filename = self.participant.get_sub_id() + "_report.md"
        report_dir = os.path.join("report", self.participant.get_sub_id(), self.session_id)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        self.set_report_dir(report_dir)
        self.set_fif_dir(os.path.join(report_dir, "eeg"))
        return os.path.join(report_dir, session_report_filename)
    
    def get_participant(self):
        return self.participant

    def set_report_dir(self, report_dir):
        self.report_dir = report_dir
    
    def set_fif_dir(self, fif_dir):
        self.fif_dir = fif_dir

    def get_report_dir(self):
        return self.report_dir
    
    def get_fif_dir(self):
        return self.fif_dir
    
    def get_log_filepath(self):
        if (self.log_filepath == ""):
            stdout_dir = self.get_report_dir()
            if self.participant.has_multiple_sessions():
                stdout_filename = (str(self.get_session_id()) + "_" + str(self.get_participant().get_sub_id()) + "_log.txt")
            else: 
                stdout_filename = (str(self.get_participant().get_sub_id()) + "_log.txt")
            self.log_filepath = os.path.join(stdout_dir, stdout_filename)
            return self.log_filepath
        else: 
            return self.log_filepath

class Run:

    def __init__(self, run_id, filepath, session):
        self.run_id = run_id
        self.filepath = filepath
        self.session = session
        self.raw = None
        self.fif_filepath = ""
        self.bads_by_nan_flat = []
        self.bads_by_hfnoise = []
        self.bads_by_deviation = []
        self.bads_by_correlation = []
        self.bads_by_SNR = []
        self.bads_by_ransac = []
        self.all_selected_bads = []
    
    def set_and_init_raw(self, raw):
        self.raw = raw
        self.set_montage_and_reference()
        
    def set_montage_and_reference(self):
        # This only needs to be done if the reference is not set automatically
        if(pln.reference_channel_set_automatically == False):
            self.raw.set_eeg_reference(ref_channels=[pln.reference_channel])
        self.raw.set_montage(pln.eeg_placement_scheme)

    def get_raw(self):
        return self.raw
    
    def set_raw(self, raw):
        self.raw = raw
        
    def get_fif_filepath(self):
        if (self.fif_filepath == ""):
            fif_dir = self.session.get_fif_dir()
            if not os.path.exists(fif_dir):
                os.makedirs(fif_dir)
            if self.session.get_participant().has_multiple_sessions():
                fif_filename = (str(self.run_id) + "_" + str(self.session.get_session_id()) + "_" + str(self.session.get_participant().get_sub_id()) + "_eeg.fif")
            else:
                fif_filename = (str(self.run_id) + "_" + str(self.session.get_participant().get_sub_id()) + "_eeg.fif")
            self.fif_filepath = os.path.join(fif_dir, fif_filename)
            return self.fif_filepath
        else: 
            return self.fif_filepath
    
    def get_report_path(self):
        return self.session.get_report_path()
    
    def get_filepath(self):
        return self.filepath
    
    def get_report_dir(self):
        return self.session.get_report_dir()
    
    def get_run_id(self):
        return self.run_id
    
    def get_session(self):
        return self.session
    
    # Setters and getters for bad channels  
    def set_bads_by_nan_flat(self, list):
        self.bads_by_nan_flat = list

    def set_bads_by_hfnoise(self, list):
        self.bads_by_hfnoise = list

    def set_bads_by_deviation(self, list):
        self.bads_by_deviation = list

    def set_bads_by_correlation(self, list):
        self.bads_by_correlation = list

    def set_bads_by_SNR(self, list):
        self.bads_by_SNR = list

    def set_bads_by_ransac(self, list):
        self.bads_by_ransac = list

    def set_all_selected_bads(self, list):
        self.all_selected_bads = list

    def get_bads_by_nan_flat(self):
        return self.bads_by_nan_flat
    
    def get_bads_by_hfnoise(self):
        return self.bads_by_hfnoise
    
    def get_bads_by_deviation(self):
        return self.bads_by_deviation

    def get_bads_by_correlation(self):
        return self.bads_by_correlation
    
    def get_bads_by_SNR(self):
        return self.bads_by_SNR
    
    def get_bads_by_ransac(self):
        return self.bads_by_ransac

    def get_all_selected_bads(self):
        return self.all_selected_bads
    

    

    

    
    