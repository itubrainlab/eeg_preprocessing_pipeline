import mne
from pyprep import NoisyChannels
from mne.preprocessing import ICA
import report_generator as rg
import read_directories as rd
import warnings
import configReader as cr
import pipeline_manager as pm
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


# Which algorithms to run
bads_by_nan_flat = cr.bads_by_nan_flat.lower() == 'true'
bads_by_hfnoise = cr.bads_by_hfnoise.lower() == 'true'
bads_by_deviation = cr.bads_by_deviation.lower() == 'true'
bads_by_correlation = cr.bads_by_correlation.lower() == 'true'
bads_by_SNR = cr.bads_by_SNR.lower() == 'true'
bads_by_ransac = cr.bads_by_ransac.lower() == 'true'
run_ica = cr.run_ica.lower() == 'true'

# for bads_by_hfnoise
hf_zscore_threshold = 5.0

# for bads_by_deviation
deviation_threshold = 5.0

# for bads_by_correlation
correlation_secs = 1.0
correlation_threshold = 0.4
frac_bad_corr = 0.01

# for bads_by_ransac
n_samples = 50
sample_prop = 0.25
corr_thresh = 0.75
frac_bad_ransac = 0.4
corr_window_secs= 5.0
channel_wise = cr.channel_wise.lower() == 'true'



def create_raw(run):
    """ Creates and returns raw. Sets the reference channel if provided
    in the config file using MNE functionality.

    Parameters
    - Data_path: the path to the given EEG file
    - File_extension: File extension for the given EEG file
    """
    filepath = run.get_filepath()
    file_extension = rd.file_extension
    print(filepath)
    if file_extension == ".edf":
        run.set_and_init_raw(mne.io.read_raw_edf(filepath, preload=True))
    else:
        print("Given file extension is not implemented. \
              Go to the function create_raw() in cleanup_functions.py to implement it.")
    run.get_raw().set_montage(pm.eeg_placement_scheme)
    if not pm.reference_channel_set_automatically:
        run.get_raw().set_eeg_reference(ref_channels=[pm.reference_channel])


def print_raw_info(run):
    """Prints raw for the given run using MNE functionality.

    Parameters
    - Run: A run object"""
    info = run.get_raw().info
    ch_names_list = info["ch_names"]
    delimiter = " "
    ch_names_string = delimiter.join(ch_names_list)
    no_of_channels = str(info["nchan"])
    rg.print_h4("Raw info for " + run.get_run_id(), run)
    rg.print_normal("Number of channels: " + no_of_channels, run)
    rg.print_normal("Channel list: ", run)
    rg.print_normal(ch_names_string, run)
    rg.print_normal("Highpass: " + str(info["highpass"]), run)
    rg.print_normal("Lowpass: " + str(info["lowpass"]), run)
    rg.print_normal("Sampling frequency: " + str(info["sfreq"]), run)

    
def raw_channel_plot(run):
    """This function uses the mne raw.plot() function to 
    plot raw channels over time for all channels.

    Parameters
    - A run object

    Outputs
    - A plot to report
    - Creates a plot file
    """
    filename = "raw_channel_plot"
    raw = run.get_raw()
    nr_channels = raw.info["nchan"]
    plot = raw.plot(duration=5, n_channels=nr_channels, clipping=None)
    rg.add_plot(run, plot, filename, True)


def plot_psd(run):
    """This function uses the mne raw.compute_psd().plot() function.
    Plotting spectral density.

    Parameters
    - A run object

    Outputs
    - A plot to report
    - Creates a plot file
    """
    filename = "psd_plot_before_filtering"
    raw_psd = run.get_raw().compute_psd()
    plot = raw_psd.plot()
    rg.add_plot(run, plot, filename, True)


def apply_notch_filter_and_plot_psd(run):
    """
    This function removes the line noise and calls the plot_psd function
    after removal. The noise is set at 50 Hz unless otherwise specified in config file.

    Parameters
    - A run object

    Outputs
    - A plot to report
    - Creates a plot file
    """    
    run.get_raw().notch_filter(freqs=pm.line_frequency)
    filename = "psd_plot_after_notch_filter_applied"
    raw_psd = run.get_raw().compute_psd()
    plot = raw_psd.plot()
    rg.add_plot(run, plot, filename, True)


def plot_sensors(run):
    """This function uses the mne raw.plot_sensors() function
    to plot relative sensors position.

    Parameters
    - A run object

    Outputs
    - outputs plot to report
    - creates plot file
    """
    filename = "sensors_plot"
    raw = run.get_raw()
    plot = raw.plot_sensors(ch_type='eeg', show_names=True, sphere=(0.0, 0.02, 0.015, 0.11), verbose=False)
    rg.add_plot(run, plot, filename, False)
    

def set_parameters_for_bad_channel_detection():
    """
    Sets parameters for finding bad channels to those inputted in config file.
    If not inputted, it leaves the default value.
    """
    if not cr.hf_zscore_threshold == "":
        global hf_zscore_threshold
        hf_zscore_threshold = float(cr.hf_zscore_threshold)
    
    if not cr.deviation_threshold == "":
        global deviation_threshold
        deviation_threshold = float(cr.deviation_threshold)

    if not cr.correlation_secs == "":
        global correlation_secs
        correlation_secs = float(cr.correlation_secs)
    
    if not cr.correlation_threshold == "":
        global correlation_threshold
        correlation_threshold = float(cr.correlation_threshold)

    if not cr.frac_bad_corr == "":
        global frac_bad_corr
        frac_bad_corr = float(cr.frac_bad_corr)

    if not cr.n_samples == "":
        global n_samples
        n_samples = int(cr.n_samples)

    if not cr.sample_prop == "":
        global sample_prop
        sample_prop = float(cr.sample_prop)

    if not cr.corr_thresh == "":
        global corr_thresh
        corr_thresh = float(cr.corr_thresh)

    if not cr.frac_bad_ransac == "":
        global frac_bad_ransac
        frac_bad_ransac = float(cr.frac_bad_ransac)

    if not cr.corr_window_secs == "":
        global corr_window_secs
        corr_window_secs = float(cr.corr_window_secs)
   

def find_bad_by_nan_flat(run):
    """Detect channels that contain NaN values or have near-flat signals.

        A channel is considered flat if its standard deviation or its median
        absolute deviation from the median (MAD) are below 1e-9 microvolts.

        This method is run automatically when a ``NoisyChannels`` object is
        initialized, preventing flat or NaN-containing channels from interfering
        with the detection of other types of bad channels.

        Source: pyprep Library

        """
    rg.print_h5("Bads by nan flat:", run)
    raw = run.get_raw()
    noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
    noisy_channels.find_bad_by_nan_flat()
    bads_list = __find_and_print_bads(run, noisy_channels)
    run.set_bads_by_nan_flat(bads_list)


def find_bad_by_hfnoise(run):
    """Detect channels with abnormally high amounts of high-frequency noise.

        The noisiness of a channel is defined as the amplitude of its
        high-frequency (>50 Hz) components divided by its overall amplitude.
        A channel is considered "bad-by-high-frequency-noise" if its noisiness
        is considerably higher than the median channel noisiness, as determined
        by a robust Z-scoring method and the given Z-score threshold.

        Due to the Nyquist theorem, this method will only attempt bad channel
        detection if the sample rate of the given signal is above 100 Hz.

        Parameters
        ----------
        HF_zscore_threshold : float, optional
            The minimum noisiness z-score of a channel for it to be considered
            bad-by-high-frequency-noise. Defaults to ``5.0``.

        Source: pyprep Library

        """

    rg.print_h5("Bads by hf noise:", run)
    global hf_zscore_threshold
    raw = run.get_raw()
    noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
    noisy_channels.find_bad_by_hfnoise(hf_zscore_threshold)
    bads_list = __find_and_print_bads(run, noisy_channels)
    run.set_bads_by_hfnoise(bads_list)


def find_bad_by_deviation(run):
    """Detect channels with abnormally high or low overall amplitudes.

        A channel is considered "bad-by-deviation" if its amplitude deviates
        considerably from the median channel amplitude, as calculated using a
        robust Z-scoring method and the given deviation threshold.

        Amplitude Z-scores are calculated using the formula
        ``(channel_amplitude - median_amplitude) / amplitude_sd``, where
        channel amplitudes are calculated using a robust outlier-resistant estimate
        of the signals' standard deviations (IQR scaled to units of SD), and the
        amplitude SD is the IQR-based SD of those amplitudes.

        Parameters
        ----------
        deviation_threshold : float, optional
            The minimum absolute z-score of a channel for it to be considered
            bad-by-deviation. Defaults to ``5.0``.

        Source: pyprep Library
        """
    rg.print_h5("Bads by deviation:", run)
    global deviation_threshold
    raw = run.get_raw()
    noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
    noisy_channels.find_bad_by_deviation(deviation_threshold)
    bads_list = __find_and_print_bads(run, noisy_channels)
    run.set_bads_by_deviation(bads_list)


def find_bad_by_correlation(run):
    """Detect channels that sometimes don't correlate with any other channels.

        Channel correlations are calculated by splitting the recording into
        non-overlapping windows of time (default: 1 second), getting the absolute
        correlations of each usable channel with every other usable channel for
        each window, and then finding the highest correlation each channel has
        with another channel for each window (by taking the 98th percentile of
        the absolute correlations).

        A correlation window is considered "bad" for a channel if its maximum
        correlation with another channel is below the provided correlation
        threshold (default: ``0.4``). A channel is considered "bad-by-correlation"
        if its fraction of bad correlation windows is above the bad fraction
        threshold (default: ``0.01``).

        This method also detects channels with intermittent dropouts (i.e.,
        regions of flat signal). A channel is considered "bad-by-dropout" if
        its fraction of correlation windows with a completely flat signal is
        above the bad fraction threshold (default: ``0.01``).

        Parameters
        ----------
        correlation_secs : float, optional
            The length (in seconds) of each correlation window. Defaults to ``1.0``.
        correlation_threshold : float, optional
            The lowest maximum inter-channel correlation for a channel to be
            considered "bad" within a given window. Defaults to ``0.4``.
        frac_bad : float, optional
            The minimum proportion of bad windows for a channel to be considered
            "bad-by-correlation" or "bad-by-dropout". Defaults to ``0.01`` (1% of
            all windows).

        Source: Pyprep Library

        """
    rg.print_h5("Bads by correlation:", run)
    raw = run.get_raw()
    global correlation_secs
    global correlation_threshold
    global frac_bad_corr
    noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
    noisy_channels.find_bad_by_correlation(correlation_secs, correlation_threshold, frac_bad_corr)
    bads_list = __find_and_print_bads(run, noisy_channels)
    run.set_bads_by_correlation(bads_list)


def find_bad_by_SNR(run):
    """Detect channels that have a low signal-to-noise ratio.

    Channels are considered "bad-by-SNR" if they are bad by both high-frequency
    noise and bad by low correlation.

    Source: Pyprep Library

    """
    rg.print_h5("Bads by SNR:", run)
    raw = run.get_raw()

    global hf_zscore_threshold
    global correlation_secs, correlation_threshold, frac_bad_corr

    bad_by_hf_list = run.get_bads_by_hfnoise()
    bad_by_corr_list = run.get_bads_by_correlation()

    if(run.get_bads_by_hfnoise() == []):
        noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
        bad_by_hf_list = noisy_channels.get_bads(hf_zscore_threshold)

    if(run.get_bads_by_correlation() == []):
        noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
        bad_by_corr_list = noisy_channels.find_bad_by_correlation(correlation_secs, correlation_threshold, frac_bad_corr)
    
    bads_str = "None"
    
    if not (bad_by_hf_list is None or bad_by_corr_list is None):
        bad_by_hf = set(bad_by_hf_list)
        bad_by_corr = set(bad_by_corr_list)
        bad_by_SNR = list(bad_by_corr.intersection(bad_by_hf))
        if not (bad_by_SNR == []):
            delimiter = ", "
            bads_str = delimiter.join(bad_by_SNR)
            run.set_bads_by_correlation(bad_by_SNR)
    rg.print_normal(bads_str, run)
    


def find_bad_by_ransac(run):
    """Detect channels that are predicted poorly by other channels.

        This method uses a random sample consensus approach (RANSAC, see [1]_,
        and a short discussion in [2]_) to try and predict what the signal should
        be for each channel based on the signals and spatial locations of other
        currently-good channels. RANSAC correlations are calculated by splitting
        the recording into non-overlapping windows of time (default: 5 seconds)
        and correlating each channel's RANSAC-predicted signal with its actual
        signal within each window.

        A RANSAC window is considered "bad" for a channel if its predicted signal
        vs. actual signal correlation falls below the given correlation threshold
        (default: ``0.75``). A channel is considered "bad-by-RANSAC" if its fraction
        of bad RANSAC windows is above the given threshold (default: ``0.4``).

        Due to its random sampling component, the channels identified as
        "bad-by-RANSAC" may vary slightly between calls of this method.
        Additionally, bad channels may vary between different montages given that
        RANSAC's signal predictions are based on the spatial coordinates of each
        electrode.

        This method is a wrapper for the :func:`~ransac.find_bad_by_ransac`
        function.

        .. warning:: For optimal performance, RANSAC requires that channels bad by
                     deviation, correlation, and/or dropout have already been
                     flagged. Otherwise RANSAC will attempt to use those channels
                     when making signal predictions, decreasing accuracy and thus
                     increasing the likelihood of false positives.

        Parameters
        ----------
        n_samples : int, optional
            Number of random channel samples to use for RANSAC. Defaults
            to ``50``.
        sample_prop : float, optional
            Proportion of total channels to use for signal prediction per RANSAC
            sample. This needs to be in the range [0, 1], where 0 would mean no
            channels would be used and 1 would mean all channels would be used
            (neither of which would be useful values). Defaults to ``0.25``
            (e.g., 16 channels per sample for a 64-channel dataset).
        corr_thresh : float, optional
            The minimum predicted vs. actual signal correlation for a channel to
            be considered good within a given RANSAC window. Defaults
            to ``0.75``.
        frac_bad : float, optional
            The minimum fraction of bad (i.e., below-threshold) RANSAC windows
            for a channel to be considered bad-by-RANSAC. Defaults to ``0.4``.
        corr_window_secs : float, optional
            The duration (in seconds) of each RANSAC correlation window. Defaults
            to 5 seconds.
        channel_wise : bool, optional
            Whether RANSAC should predict signals for chunks of channels over the
            entire signal length ("channel-wise RANSAC", see `max_chunk_size`
            parameter). If ``False``, RANSAC will instead predict signals for all
            channels at once but over a number of smaller time windows instead of
            over the entire signal length ("window-wise RANSAC"). Channel-wise
            RANSAC generally has higher RAM demands than window-wise RANSAC
            (especially if `max_chunk_size` is ``None``), but can be faster on
            systems with lots of RAM to spare. Defaults to ``False``.
        max_chunk_size : {int, None}, optional
            The maximum number of channels to predict at once during
            channel-wise RANSAC. If ``None``, RANSAC will use the largest chunk
            size that will fit into the available RAM, which may slow down
            other programs on the host system. If using window-wise RANSAC
            (the default), this parameter has no effect. Defaults to ``None``.

        References
        ----------
        .. [1] Fischler, M.A., Bolles, R.C. (1981). Random sample consensus: A
            Paradigm for Model Fitting with Applications to Image Analysis and
            Automated Cartography. Communications of the ACM, 24, 381-395
        .. [2] Jas, M., Engemann, D.A., Bekhti, Y., Raimondo, F., Gramfort, A.
            (2017). Autoreject: Automated Artifact Rejection for MEG and EEG
            Data. NeuroImage, 159, 417-429

        Source: Pyprep Library

        """

    rg.print_h5("Bads by ransac:", run)

    global n_samples, sample_prop, corr_thresh, frac_bad_ransac, corr_window_secs, channel_wise
    raw = run.get_raw()
    noisy_channels = NoisyChannels(raw, do_detrend=True, random_state=42)
    noisy_channels.find_bad_by_correlation(correlation_secs, correlation_threshold, frac_bad_corr)
    noisy_channels.find_bad_by_deviation(deviation_threshold)
    noisy_channels.find_bad_by_ransac(n_samples=n_samples, sample_prop=sample_prop, corr_thresh=corr_thresh, frac_bad=frac_bad_ransac, corr_window_secs=corr_window_secs, channel_wise=channel_wise)
    bads_list = __find_and_print_bads(run, noisy_channels)
    run.set_bads_by_ransac(bads_list)


def __find_and_print_bads(run, noisy_channels):
    """Helper function to create and print a list of bad channels.

    Parameters
    - A run object
    - A NoisyChannels objecy

    Outputs
    - Prints a list of bad channels to the report
    - Returns a list of bad channels
    
    """
    bads_list = noisy_channels.get_bads()
    bads_str = "None"
    if not bads_list == []:
        delimiter = ", "
        bads_str = delimiter.join(bads_list)
    rg.print_normal(bads_str, run)
    return bads_list


def set_bad_channels(run):
    """Sets the run's bad channels to the ones found by 
    selected function as per config file.

    Also sets the bad channels in the raw of each run.

    Parameters
    - A run object

    Outputs
    - Prints a list of channels that were identified as bad by selected functions
    """

    global bads_by_nan_flat, bads_by_hfnoise, bads_by_deviation, bads_by_correlation, bads_by_SNR, bads_by_ransac
    all_bads = []

    if bads_by_nan_flat:
        all_bads.extend(run.get_bads_by_nan_flat())
    
    if bads_by_hfnoise:
        all_bads.extend(run.get_bads_by_hfnoise())

    if bads_by_deviation:
        all_bads.extend(run.get_bads_by_deviation())

    if bads_by_correlation:
        all_bads.extend(run.get_bads_by_correlation())

    if bads_by_SNR:
        all_bads.extend(run.get_bads_by_SNR())

    if bads_by_ransac:
        all_bads.extend(run.get_bads_by_ransac())

    all_bads = list(set(all_bads))

    run.set_all_selected_bads(all_bads)
    run.get_raw().info["bads"] = all_bads

    bads_str = "None"

    if not all_bads == []:
        delimiter = ", "
        bads_str = delimiter.join(all_bads)

    rg.print_h5("Channels flagged as bad: ", run)
    rg.print_normal(bads_str, run)


def ica(run):
    """Runs ICA using MNE functionality"""
    global run_ica
    raw_for_ica = run.get_raw().copy() #.filter(l_freq=1)
    raw_for_ica.drop_channels(run.get_raw().info["bads"])

    ica = ICA(max_iter='auto')
    ica.fit(raw_for_ica)

    plot = ica.plot_sources(raw_for_ica)
    filename = "ICA_time_series_plot"
    rg.add_plot(run, plot, filename, True)

    plotlist = ica.plot_components(show=False)
    filename2 = "ICA_spatial_components_plot"

    for idx, pl in enumerate(plotlist):
        filenm = f"{filename2}_{idx}" 
        rg.add_plot(run, pl, filenm, True)


def interpolate_bads(run):
    """Interpolates bad channels using MNE functionality"""
    run.set_raw(run.get_raw().interpolate_bads(reset_bads=True))
    rg.print_normal(f"Interpolation of bad channels for {run.get_run_id()} ran. To get detailed output of the interpolation see the log file at location: {run.get_session().get_log_filepath()}", run)

    
def save_raw_as_fif(run): 
    """Saves raw to .fif file using MNE functionality"""
    fif_path = run.get_fif_filepath()
    run.get_raw().save(fname=fif_path, overwrite=True)
    rg.print_normal(f"The cleaned EEG file for {run.get_run_id()} was saved at the following location: {fif_path}", run)
