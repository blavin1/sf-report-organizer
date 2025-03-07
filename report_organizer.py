import os
import pandas as pd
from simple_salesforce import Salesforce
from dotenv import load_dotenv
import logging
from typing import Dict, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SalesforceReportOrganizer:
    def __init__(self):
        """Initialize Salesforce connection using environment variables."""
        load_dotenv()
        
        # Connect to Salesforce
        try:
            self.sf = Salesforce(
                username=os.getenv('SF_USERNAME'),
                password=os.getenv('SF_PASSWORD'),
                security_token=os.getenv('SF_SECURITY_TOKEN'),
                domain='login'  # or 'test' for sandbox
            )
            logger.info("Successfully connected to Salesforce")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {str(e)}")
            raise

    def get_folder_id(self, folder_name: str) -> str:
        """Get the Salesforce folder ID by name."""
        try:
            query = f"SELECT Id FROM Folder WHERE Name = '{folder_name}' AND Type = 'Report'"
            result = self.sf.query(query)
            
            if result['totalSize'] == 0:
                raise ValueError(f"Folder not found: {folder_name}")
                
            return result['records'][0]['Id']
        except Exception as e:
            logger.error(f"Error getting folder ID for {folder_name}: {str(e)}")
            raise

    def move_report(self, report_id: str, destination_folder_id: str) -> bool:
        """Move a report to the specified destination folder."""
        try:
            # Update the report's folderId
            self.sf.Report.update(report_id, {'FolderId': destination_folder_id})
            logger.info(f"Successfully moved report {report_id} to folder {destination_folder_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to move report {report_id}: {str(e)}")
            return False

    def process_mapping_file(self, csv_path: str) -> None:
        """Process the CSV mapping file and move reports accordingly."""
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)
            required_columns = ['report_id', 'destination_folder', 'is_private', 'owner_username']
            
            # Validate CSV structure
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV file is missing required columns")

            # Create a cache for folder IDs to minimize API calls
            folder_id_cache: Dict[str, str] = {}
            
            # Process each row in the CSV
            for index, row in df.iterrows():
                try:
                    # Get destination folder ID (with caching)
                    if row['destination_folder'] not in folder_id_cache:
                        folder_id_cache[row['destination_folder']] = self.get_folder_id(row['destination_folder'])
                    
                    destination_id = folder_id_cache[row['destination_folder']]
                    
                    # Validate ownership if report is private
                    if row['is_private']:
                        if not row['owner_username']:
                            logger.warning(f"Skipping private report {row['report_id']}: missing owner username")
                            continue
                            
                        # Here you might want to add additional ownership validation logic
                        
                    # Move the report
                    success = self.move_report(row['report_id'], destination_id)
                    if success:
                        logger.info(f"Processed report {row['report_id']} successfully")
                    else:
                        logger.error(f"Failed to process report {row['report_id']}")
                        
                except Exception as e:
                    logger.error(f"Error processing row {index}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise

def main():
    """Main execution function."""
    try:
        organizer = SalesforceReportOrganizer()
        organizer.process_mapping_file('report_mapping.csv')
        logger.info("Report organization completed successfully")
    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
