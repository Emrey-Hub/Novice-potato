import sys
from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QPushButton, QInputDialog, QVBoxLayout, QFileDialog, QRadioButton
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from datetime import datetime

def plot_pl_data(legend_by_file_name, custom_legend_name):
    # Set the reference time to zero
    ref_time = 0

    # Ask the user to select files
    file_paths, _ = QFileDialog.getOpenFileNames(window, "Select Files", "", "Text Files (*.txt)")
    if not file_paths:
        return  # No files selected, return

    # Create the plot for PL data
    fig, ax = plt.subplots()
    ax.set_xlabel('Wavelength (nm)', fontweight='bold', fontsize=14)
    ax.set_ylabel('Intensity (a.u.)', fontweight='bold', fontsize=14)

    # Parse the acquisition time from the file name and sort the files by acquisition time
    files = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        if legend_by_file_name:
            label = os.path.splitext(file_name)[0]
        else:
            # Convert the time string to seconds
            acquisition_time = datetime.strptime(file_name.split('_')[2].replace('.txt', ''), '%H-%M-%S-%f').timestamp()
            if ref_time == 0:
                ref_time = acquisition_time
            label = '{:.2f} s'.format(acquisition_time - ref_time)
        files.append((label, file_path))
    files = sorted(files)

    # Custom Legend functionality
    if custom_legend_name:
        custom_legends = []
        for file in files:
            legend_name, ok = QInputDialog.getText(window, 'Custom Legend', 'Enter the legend name for {}:'.format(file[0]))
            if ok:
                custom_legends.append(legend_name)
            else:
                custom_legends.append('')

    # Plot the data from each file
    for i, file in enumerate(files):
        file_label = file[0]
        if custom_legend_name and custom_legends[i]:
            file_label = custom_legends[i]

        file_path = file[1]

        # Open the file
        with open(file_path, 'r') as f:
            # Skip the header information
            for line in f:
                if line.strip() == '>>>>>Begin Spectral Data<<<<<':
                    break

            # Read in the data from the two columns
            x, y = [], []
            for line in f:
                if line.strip() == '>>>>>End Spectral Data<<<<<':
                    break
                data = line.split()
                x.append(float(data[0].replace(',', '.')))
                y.append(float(data[1]))

            # Plot the data and update the legend label
            ax.plot(x, y, label=file_label)

    # Add a legend and show the plot
    ax.legend(prop={'weight': 'bold'})

    # Increase font size and make it bold
    ax.tick_params(axis='both', which='major', labelsize=12, width=2, length=6, direction='in', pad=8)
    ax.tick_params(axis='both', which='minor', width=1, length=3, direction='in')
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, linestyle='--', alpha=0.5)

    # Update the plot window with the modifications
    fig.canvas.draw()

    # Show the plot
    plt.show()


def plot_afm_data():
    # Ask the user to select the AFM data file
    file_path, _ = QFileDialog.getOpenFileName(window, "Select AFM Data File", "", "Text Files (*.txt)")
    if not file_path:
        return  # No file selected, return

    # Open the file with the correct encoding
    with open(file_path, 'r', encoding='latin-1') as f:
        # Skip the first row
        next(f)

        # Read the data from the file
        lines = f.readlines()

    # Parse the data
    x = []
    y = []
    for line in lines:
        if line.strip().replace(',', '.').replace('e', 'E').replace('-', 'E-').replace('+', 'E+') == '':
            continue  # Skip empty lines or lines with non-numeric data
        data = line.split()
        x.append(float(data[0]))
        y.append(float(data[1]))

    # Create a figure and axis object
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(x, y)
    ax.set_xlabel('Distance (µm)', fontweight='bold', fontsize=16)
    ax.set_ylabel('Surface voltage (mV)', fontweight='bold', fontsize=16)

    # Increase font size and make it bold
    ax.tick_params(axis='both', which='major', labelsize=14, width=2, length=6, direction='in', pad=8)
    ax.tick_params(axis='both', which='minor', width=1, length=3, direction='in')
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, linestyle='--', alpha=0.5)

    # Update the plot window with the modifications
    fig.canvas.draw()

    # Show the plot
    plt.show()

# Create the application and main window
app = QApplication([])
window = QWidget()
window.setWindowTitle("Spectral Data Plotter")

# Create the layout
layout = QVBoxLayout()

# Add a radio button for PL Data
pl_radio = QRadioButton("PL Data")
layout.addWidget(pl_radio)

# Add checkboxes for legend by file name and custom legend name
legend_checkbox = QCheckBox("Legend by file name")
custom_legend_checkbox = QCheckBox("Custom Legend Name")
layout.addWidget(legend_checkbox)
layout.addWidget(custom_legend_checkbox)

# Add a radio button for AFM Data
afm_radio = QRadioButton("AFM Data")
layout.addWidget(afm_radio)

# Add a button to plot the data
plot_button = QPushButton("Plot Data")
layout.addWidget(plot_button)

# Set the layout for the main window
window.setLayout(layout)

# Connect the plot button to the respective plot functions
plot_button.clicked.connect(lambda: plot_pl_data(legend_checkbox.isChecked(), custom_legend_checkbox.isChecked()) if pl_radio.isChecked() else plot_afm_data())

# Disable checkboxes when AFM Data is selected
afm_radio.toggled.connect(lambda checked: legend_checkbox.setEnabled(not checked))
afm_radio.toggled.connect(lambda checked: custom_legend_checkbox.setEnabled(not checked))

# Show the main window
window.show()

# Run the application event loop
app.exec()