"""Calculates and visualizes (Delta F)/F0 versus time.

This script can be used for analyzing changes in neuronally-expressed
fluorescent sensor intensity (F) throughout the duration of a video
recording. It takes as input csv files that contain the mean
fluorescence intensities (i.e. the mean fluorescence intensities of
the neuron and background) for every frame of the video recording.

The script calculates baseline fluorescence intensity (F0) from a
user-defined number of initial frames, then calculates the change
in fluorescence intensity ((Delta F)/F0, in which Delta F = F - F0)
for subsequent frames as a function of time (note that the script
works with a frame rate of 1 Hz). The script then returns for each
neuron in a video recording a csv file that contains (Delta F)/F0 in
the first column and time (s) in the second column. These are stored
in the "data_analysis" subfolder under the "Results" folder. It also
returns graphs that visualize (Delta F)/F0 vs. time (s) for each neuron
in a video recording. These are stored in the "graphs" subfolder under
the "Results" folder.
"""

import glob
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import shutil

# Create directory for Results that lives in the same directory
# as your data. Within Results, create directories for data analysis
# and graphs.

# Input data's directory path here.
data_path = "/data/path/goes/here"

Results_path = "Results"
Results_folder = os.path.join(data_path, Results_path)
os.mkdir(Results_folder)

os.chdir(Results_folder)

data_analysis_path = "data_analysis"
data_analysis_subfolder = os.path.join(Results_folder, data_analysis_path)
os.mkdir(data_analysis_subfolder)

graphs_path = "graphs"
graphs_subfolder = os.path.join(Results_folder, graphs_path)
os.mkdir(graphs_subfolder)

# Go to the directory where the ImageJ data lives;
# this is equivalent to going up one directory (cd ..).
# This line results in being back in the data_path directory.
os.chdir(os.path.dirname(Results_folder))

# Open csv files containing mean values.
filenames = sorted(glob.glob('*.csv'))


def analyze_data(filenames, data_path):

    for imaging_file in filenames:
        # Go to the directory where the ImageJ data lives.
        os.chdir(data_path)

        # Open csv file and obtain mean fluorescence intensity values
        # for every frame. Odd values (mean_list_odd) contain the mean
        # fluorescence intensities for a region of interest (ROI)
        # that contains the neuron. Even values (mean_list_even)
        # contain the mean fluorescence intensities for an ROI
        # that contains background. There is 1 even and 1 odd value
        # for every frame. The ROIs for all frames are the same
        # area and shape.
        mean_values = open(imaging_file, 'r')
        mean_list = []
        frame_list = []
        mean_list_odd = []
        mean_list_even = []

        for line in mean_values:
            splitline = line.split(',')
            # Create frame list.
            try:
                frame_as_int = int(splitline[0])
                frame_list.append(frame_as_int)
            except:
                pass
            # Create mean list.
            try:
                mean_as_float = float(splitline[1])
                mean_list.append(mean_as_float)
            except:
                pass

        mean_values.close()

        # This list contains mean fluorescence intensity
        # measured over neuron.
        for odd_value in mean_list[::2]:
            mean_list_odd.append(odd_value)

        # This list contains mean fluorescence measured intensity
        # measured over background.
        for even_value in mean_list[1::2]:
            mean_list_even.append(even_value)

        mean_list_odd_array = np.asarray(mean_list_odd)
        mean_list_even_array = np.asarray(mean_list_even)

        # Calculate mean fluorescence intensity for each
        # frame, accounting for background subtraction
        # (odd mean - even mean).
        odd_minus_even = np.subtract(mean_list_odd_array, mean_list_even_array)

        # The number_of_initial_frames are the frames used to calculate
        # the mean baseline fluorescence intensity (F0). These are
        # frames taken at the beginning of the recording.  It's
        # important to change this if a different number of frames is
        # used to calculate F0.
        number_of_initial_frames = 3

        # Calculate F0.
        F_sum = 0

        for F in odd_minus_even[:number_of_initial_frames]:
            F_sum += F

        F0 = F_sum/number_of_initial_frames

        # Create F/F0 list.
        DeltaF_over_F0_list = []

        # Note that this for loop assumes not wanting to use the frames
        # used to calculate F0 (i.e. Frames ued to calculate F0
        # are never F).
        for F in odd_minus_even[number_of_initial_frames:]:
            DeltaF_over_F0_percent = ((F-F0)/F0)*100
            DeltaF_over_F0_list.append(DeltaF_over_F0_percent)

        # Create time list.

        # First, specify frame rate. Make sure time_sec is calculated
        # correctly when Hz does NOT equal 1.
        Hz = 1

        # Second, calculate imaging time in seconds (excluding the
        # initial frames).
        imaging_time_in_sec = (frame_list[-1]/(2*Hz)) - number_of_initial_frames

        # Third, specify start time
        start_time_sec = 1 / Hz
        time_sec = np.arange(start_time_sec, (imaging_time_in_sec+1),
                             start_time_sec)
        DeltaF_over_F0_array = np.asarray(DeltaF_over_F0_list)

        # Create plot (DeltaF/F0 vs time).
        fig, ax = plt.subplots()
        ax.plot(time_sec, DeltaF_over_F0_array)
        ax.set(xlabel='time (s)', ylabel='DeltaF/F0 (%)',
               title=str(imaging_file))
        graph = str(imaging_file)[:-4] + '_graph.png'

        # Save graph in the graphs directory.
        os.chdir(Results_path)
        os.chdir(graphs_path)
        fig.savefig(graph)
        plt.show()

        # Create csv file for results (containing DeltaF/F0 and time
        # calculations) and move to Results/data_analysis directory.

        # Move cwd to Results directory.
        os.chdir(Results_folder)
        # This provides structure for writing time and deltaF/F0
        # onto data_analysis csv file
        rows = zip(time_sec, DeltaF_over_F0_array)
        DeltaF_over_F0_vs_time_file = str(imaging_file)[:-4] + \
            '_DeltaF_F0_vs_time.csv'

        with open(DeltaF_over_F0_vs_time_file, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['time (s)', 'deltaF/F0 (%)'])
            for row in rows:
                filewriter.writerow(row)
            shutil.move(DeltaF_over_F0_vs_time_file, 'data_analysis')


analyze_data(filenames, data_path)
