# Salesforce Report Organizer

This tool helps organize Salesforce reports by moving them between folders based on a CSV mapping file.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Salesforce credentials:
```
SF_USERNAME=your.email@company.com
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_security_token
```

3. Prepare your report mapping CSV file following the template in `report_mapping.csv`:
- report_id: The Salesforce ID of the report
- report_name: Name of the report (for reference)
- source_folder: Current folder name (for reference)
- destination_folder: Target folder name
- is_private: true/false indicating if this is a private report
- owner_username: Required for private reports, leave empty for shared reports

## Usage

1. Update the `report_mapping.csv` file with your report information
2. Run the script:
```bash
python report_organizer.py
```

The script will:
- Validate the CSV structure
- Connect to Salesforce
- Process each report move operation
- Log all activities and any errors

## Notes

- The script includes error handling and logging
- Private reports require owner information
- Failed operations are logged but won't stop the entire process
- Make sure you have appropriate Salesforce permissions
