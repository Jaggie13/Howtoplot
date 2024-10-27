
# User Manual - Howtoplot Application

## Contents
1. **Introduction**
2. **Installation Instructions**
3. **Interface Overview**
4. **Main Features**
   - Data Loading
   - Label Customization
   - Plot Settings
   - Data Plotting
   - Data Saving and Loading
5. **Troubleshooting**
6. **Support Information**

---

### 1. Introduction
**Howtoplot** is a data visualization tool designed for loading, modifying, plotting, and saving datasets. It supports data loading from `.txt` files, provides various plot styles, and allows label customization, making it suitable for scientific data analysis and presentation.

---

### 2. Installation Instructions
#### System Requirements
- Windows 10 or higher
- Python 3.8 or above

#### Installation Steps
1. **Install Python**: Ensure Python is installed on your computer. Visit the [Python website](https://www.python.org/) for download and installation instructions.
2. **Install Required Libraries**: Run the following command in your terminal or command prompt to install the dependencies:
   ```bash
   pip install numpy matplotlib ttkbootstrap tkinterdnd2
   ```
3. **Run the Application**: Open the terminal or command prompt in the directory where the script is located and execute the following command to start the application:
   ```bash
   python howtoplot.py
   ```

---

### 3. Interface Overview
The main interface includes the following key areas:
- **Data Load Buttons**: Divided into `XYXY`, `XYYY`, and `Box Data` formats.
- **Drag and Drop Area**: Users can drag and drop data files into this area for quick loading.
- **Label Input Area**: Allows users to input labels for each dataset.
- **Plot Settings Area**: Includes style selection, font size, axis offset, and scaling options.
- **Plot Buttons**: For generating and saving plots.

---

### 4. Main Features

#### Data Loading
- **Load XYXY Format Data**: Click the “Load txt Data (XYXY)” button or drag a file to the designated area to load data containing x-y pairs from a `.txt` file.
- **Load XYYY Format Data**: Click the “Load txt Data (XYYY)” button or drag a file to the designated area to load data with the first column as x-values and the remaining columns as different y datasets.
- **Load Box Data Format**: Click the “Load Box Data” button or drag a file to the designated area to load each column as a dataset in a `.txt` file for box plot generation.

#### Label Customization
- **Dataset Labels**: After loading data, each dataset appears in the label input area. Users can enter labels for each dataset or use default labels.
- **Plot Selection**: Users can choose to plot or exclude specific datasets.

#### Plot Settings
- **Select Style**: Choose an appropriate style (e.g., `PL`, `Raman`, `I-V`, etc.) based on data type, and the system will adjust axis labels automatically.
- **Select Font Size**: Adjust font size to suit the visual requirements of the plot.
- **Axis Settings**: Apply offset and scaling to x and y data to fine-tune data position and scaling.

#### Data Plotting
- **Generate Plots**: Click the “Plot Data” button to generate a line plot based on settings, or select style and labels for box plot generation by clicking “Plot Boxplot”.
- **Save Image**: After plotting, use the “Save Plot” button to save the image in formats such as `.png`, `.jpg`, `.bmp`, `.tiff`, `.gif`, or `.pdf`.
  
#### Data Saving and Loading
- **Save Data**: Click the “Save Raw Data” button to save data, labels, and plot settings as a `.pkl` file.
- **Load Data**: Click the “Load Raw Data” button to load a saved `.pkl` file and restore data and settings for continued plotting.

---

### 5. Troubleshooting
- **Unable to Load Data**: Ensure the file format is `.txt` and meets the column requirements for the selected format.
- **Plot Display Issues**: Confirm that `Qt5Agg` display backend is installed, or reinstall `matplotlib`.
- **Plot or Save Failure**: Verify that data is loaded and settings are complete. Ensure the plot button is enabled after data is loaded.

---

### 6. Support Information
For additional assistance or unresolved issues, please contact support:  
- **Email**: liujiaqi@uec.ac.jp

---

I hope this manual helps you successfully use the **Howtoplot** application for data visualization!
