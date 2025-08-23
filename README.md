# EVA Vehicle Data Analyzer

A modern, beautiful interface for analyzing vehicle data from MDF files with comprehensive HTML report generation.

## 🚗 Features

- **Modern UI**: Beautiful, responsive interface with dark theme
- **Multi-language Support**: French and English interfaces
- **File Analysis**: Load and analyze MDF, MF4, and DAT files
- **Use Case Detection**: Automatic detection of vehicle use cases
- **SWEET Verification**: Verify signal presence and compliance
- **Comprehensive Reports**: Generate beautiful, Word-like HTML reports
- **Real-time Progress**: Visual progress tracking during analysis

## 📋 Requirements

- Python 3.7+
- tkinter (usually included with Python)
- PIL/Pillow for image handling
- pandas for data processing
- asammdf for MDF file reading (optional)

## 🚀 Installation

1. **Clone or download the project**
2. **Install required packages**:

   ```bash
   pip install pillow pandas
   ```

3. **Optional: Install asammdf for MDF support**:
   ```bash
   pip install asammdf
   ```

## 🎯 Quick Start

### Method 1: Using the Activation Script (Recommended)

```bash
./activate_and_run.sh
```

### Method 2: Manual Virtual Environment Activation

```bash
# Activate virtual environment
source eva_env/bin/activate

# Run the interface
python run_eva.py

# Deactivate when done
deactivate
```

### Method 3: Direct Launch (if tkinter is available)

```bash
python eva_interface.py
```

## 📖 Usage Guide

### 1. Launch the Interface

- Run the launcher script or interface directly
- The modern interface will open with a dark theme

### 2. Import MDF File

- Click "Browse..." button
- Select your MDF, MF4, or DAT file
- The file will be loaded and validated

### 3. Configure Options

- **Language**: Switch between French (FR) and English (EN) - Default is English
- **MyF Version**: Choose Auto-detect or specific version
- **SWEET Version**: Select SWEET 400 or SWEET 500

### 4. Run Analysis

- Click "Start Analysis" button
- Watch the progress bar as analysis runs
- Results will be displayed in real-time

### 5. Generate Report

- Click "Generate Report" button
- A comprehensive HTML report will be created
- Click "Open Report" to view it

## 📊 Report Features

The generated HTML reports include:

- **Executive Summary**: Overview of analysis results
- **File Information**: Details about the analyzed file
- **Use Case Detection**: Results of use case analysis
- **SWEET Verification**: Signal compliance verification
- **Detailed Breakdown**: Comprehensive analysis results
- **Recommendations**: Actionable insights and suggestions

### Report Sections:

1. **Header**: Report title and generation timestamp
2. **Executive Summary**: Key metrics and overall status
3. **File Information**: File details and metadata
4. **Analysis Results**: Use case detection results
5. **SWEET Verification**: Signal verification results
6. **Detailed Breakdown**: In-depth analysis information
7. **Recommendations**: Suggestions and next steps

## 🎨 Interface Features

### Modern Design

- Dark theme with blue accent colors
- Smooth animations and hover effects
- Responsive layout that adapts to window size
- Professional typography and spacing

### User Experience

- Intuitive file selection and validation
- Real-time progress tracking
- Clear status indicators and badges
- Toast notifications for user feedback
- Language switching without losing state

### Analysis Capabilities

- Automatic use case detection
- Signal presence verification
- SWEET compliance checking
- Requirements validation
- Comprehensive error handling

## 📁 File Structure

```
python_exo-etudiant/
├── eva_interface.py          # Main interface application
├── eva_report_generator.py   # HTML report generator
├── run_eva.py               # Launcher script
├── README.md                # This file
├── Gmail/                   # Original EVA project files
│   ├── interface.py         # Original interface
│   ├── eva_detecteur.py     # Analysis engine
│   ├── ReportGenerator.py   # Original report generator
│   └── ...                  # Other project files
└── *.mdf                    # MDF files for analysis
```

## 🔧 Configuration

### Language Settings

The interface supports French and English. Switch languages using the FR/EN buttons in the header.

### Analysis Options

- **MyF Version**: Auto-detect, MyF2, MyF3, MyF4.1, MyF4.2
- **SWEET Version**: SWEET 400, SWEET 500
- **File Types**: MDF, MF4, DAT

### Report Customization

Reports are generated as HTML files with:

- Professional styling
- Print-friendly layout
- Responsive design
- Interactive elements

## 🐛 Troubleshooting

### Common Issues

1. **Module Import Errors**

   - Ensure all required packages are installed
   - Check Python version (3.7+ required)

2. **File Loading Issues**

   - Verify file format (MDF, MF4, DAT)
   - Check file permissions
   - Ensure file is not corrupted

3. **Analysis Errors**
   - Check file compatibility
   - Verify signal availability
   - Review error messages in console

### Error Messages

- **"No file selected"**: Select a valid MDF file first
- **"File error"**: Check file format and permissions
- **"Analysis error"**: Review file content and compatibility

## 📈 Performance

- **File Loading**: Optimized for large MDF files
- **Analysis Speed**: Multi-threaded processing
- **Memory Usage**: Efficient data handling
- **Report Generation**: Fast HTML generation

## 🔮 Future Enhancements

- Additional file format support
- More analysis algorithms
- Export to PDF functionality
- Batch processing capabilities
- Advanced visualization options

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review error messages in the console
3. Verify file compatibility
4. Ensure all requirements are met

## 📄 License

This project is part of the EVA (Vehicle Data Analysis) system developed for Renault/Ampere.

---

**EVA Vehicle Data Analyzer v2.0.0**  
_Modern interface for comprehensive vehicle data analysis_
