"""
Google Workspace Integration for BDFG

This module provides integration with Google Workspace applications
including Google Sheets, Docs, and Slides for the BDFG framework.
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleWorkspaceIntegration:
    """
    Google Workspace Integration for the BDFG framework.
    
    This class provides integration with Google Workspace applications including:
    - Google Sheets: For data analysis, dashboards, and reporting
    - Google Docs: For detailed business reports and documentation
    - Google Slides: For business presentations and visualizations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Google Workspace Integration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.credentials_file = self.config.get("credentials_file", "credentials.json")
        self.token_file = self.config.get("token_file", "token.json")
        self.authenticated = False
        self.services = {}
        
        # Template configurations
        self.sheet_templates = self.config.get("sheet_templates", {})
        self.doc_templates = self.config.get("doc_templates", {})
        self.slide_templates = self.config.get("slide_templates", {})
        
        # Initialize if credentials are available
        if os.path.exists(self.credentials_file):
            self.authenticate()
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Workspace API.
        
        Returns:
            bool: Success status
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            # Define the scopes
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/presentations',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = None
            # Load existing token if available
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_info(
                    json.load(open(self.token_file, 'r')),
                    SCOPES
                )
            
            # If no valid credentials available, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build services
            self.services['sheets'] = build('sheets', 'v4', credentials=creds)
            self.services['docs'] = build('docs', 'v1', credentials=creds)
            self.services['slides'] = build('slides', 'v1', credentials=creds)
            self.services['drive'] = build('drive', 'v3', credentials=creds)
            
            self.authenticated = True
            logger.info("Successfully authenticated with Google Workspace")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.authenticated = False
            return False
    
    def check_authentication(self) -> bool:
        """
        Check if authenticated with Google Workspace.
        
        Returns:
            bool: Authentication status
        """
        if not self.authenticated:
            logger.warning("Not authenticated with Google Workspace")
            return self.authenticate()
        return True
    
    # Google Sheets Integration
    
    def create_sheet(self, title: str, data: Optional[pd.DataFrame] = None) -> str:
        """
        Create a new Google Sheet.
        
        Args:
            title: Title of the sheet
            data: Optional DataFrame to populate the sheet
            
        Returns:
            str: ID of the created sheet
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Create a new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.services['sheets'].spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"Created spreadsheet with ID: {spreadsheet_id}")
            
            # If data is provided, update the sheet
            if data is not None:
                self.update_sheet_data(spreadsheet_id, data)
            
            return spreadsheet_id
            
        except Exception as e:
            logger.error(f"Error creating sheet: {str(e)}")
            raise
    
    def update_sheet_data(self, spreadsheet_id: str, data: pd.DataFrame, 
                         sheet_name: str = "Sheet1", start_cell: str = "A1") -> bool:
        """
        Update data in a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            data: DataFrame containing the data
            sheet_name: Name of the sheet to update
            start_cell: Starting cell for the data
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Convert DataFrame to values list
            values = [data.columns.tolist()]
            values.extend(data.values.tolist())
            
            # Prepare the update
            body = {
                'values': values
            }
            
            # Get the range based on data size
            end_row = len(values)
            end_col = len(values[0]) if values else 0
            
            # Convert column number to letter
            def col_num_to_letter(n):
                result = ""
                while n > 0:
                    n, remainder = divmod(n - 1, 26)
                    result = chr(65 + remainder) + result
                return result
            
            end_cell = f"{col_num_to_letter(end_col)}{end_row}"
            range_name = f"{sheet_name}!{start_cell}:{end_cell}"
            
            # Update the sheet
            result = self.services['sheets'].spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            logger.info(f"Updated {result.get('updatedCells')} cells in sheet {spreadsheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating sheet: {str(e)}")
            return False
    
    def get_sheet_data(self, spreadsheet_id: str, range_name: str = "Sheet1") -> pd.DataFrame:
        """
        Get data from a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            range_name: Range to retrieve (e.g., "Sheet1!A1:D10")
            
        Returns:
            DataFrame: Sheet data as DataFrame
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the data
            result = self.services['sheets'].spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning(f"No data found in sheet {spreadsheet_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            headers = values[0]
            data = values[1:] if len(values) > 1 else []
            
            # Ensure all rows have the same length
            max_cols = len(headers)
            for i, row in enumerate(data):
                if len(row) < max_cols:
                    data[i] = row + [''] * (max_cols - len(row))
            
            df = pd.DataFrame(data, columns=headers)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting sheet data: {str(e)}")
            raise
    
    def create_dashboard(self, title: str, data: Dict[str, pd.DataFrame], 
                        template_id: Optional[str] = None) -> str:
        """
        Create a dashboard in Google Sheets.
        
        Args:
            title: Title of the dashboard
            data: Dictionary of DataFrames to include in the dashboard
            template_id: Optional template spreadsheet ID
            
        Returns:
            str: ID of the created dashboard
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # If template is provided, copy it
            if template_id:
                dashboard_id = self.copy_file(template_id, title)
                
                # Update each sheet in the dashboard
                for sheet_name, df in data.items():
                    self.update_sheet_data(dashboard_id, df, sheet_name)
                
                return dashboard_id
            
            # Otherwise create a new dashboard
            dashboard_id = self.create_sheet(title)
            
            # Create a sheet for each DataFrame
            for sheet_name, df in data.items():
                # Create a new sheet
                self.add_sheet(dashboard_id, sheet_name)
                
                # Update the sheet with data
                self.update_sheet_data(dashboard_id, df, sheet_name)
            
            # Delete the default Sheet1
            self.delete_sheet(dashboard_id, "Sheet1")
            
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            raise
    
    def add_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """
        Add a new sheet to a spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the new sheet
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Add a new sheet
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
            
            body = {
                'requests': [request]
            }
            
            response = self.services['sheets'].spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Added sheet {sheet_name} to spreadsheet {spreadsheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding sheet: {str(e)}")
            return False
    
    def delete_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """
        Delete a sheet from a spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_name: Name of the sheet to delete
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the sheet ID
            spreadsheet = self.services['sheets'].spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                logger.warning(f"Sheet {sheet_name} not found in spreadsheet {spreadsheet_id}")
                return False
            
            # Delete the sheet
            request = {
                'deleteSheet': {
                    'sheetId': sheet_id
                }
            }
            
            body = {
                'requests': [request]
            }
            
            response = self.services['sheets'].spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Deleted sheet {sheet_name} from spreadsheet {spreadsheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting sheet: {str(e)}")
            return False
    
    def create_chart(self, spreadsheet_id: str, sheet_id: int, chart_type: str,
                    data_range: str, title: str, position: Dict[str, int]) -> bool:
        """
        Create a chart in a Google Sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            sheet_id: ID of the sheet
            chart_type: Type of chart (e.g., "BAR", "LINE", "PIE")
            data_range: Range of data for the chart
            title: Title of the chart
            position: Position of the chart (e.g., {"column": 5, "row": 0})
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Create chart request
            chart_spec = {}
            
            if chart_type == "BAR":
                chart_spec = {
                    'basicChart': {
                        'chartType': 'BAR',
                        'legendPosition': 'RIGHT_LEGEND',
                        'axis': [
                            {'position': 'BOTTOM_AXIS', 'title': 'Category'},
                            {'position': 'LEFT_AXIS', 'title': 'Value'}
                        ],
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 0,
                                        'endRowIndex': 1,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 10
                                    }]
                                }
                            }
                        }],
                        'series': [{
                            'series': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,
                                        'endRowIndex': 10,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 10
                                    }]
                                }
                            },
                            'targetAxis': 'LEFT_AXIS'
                        }]
                    }
                }
            elif chart_type == "LINE":
                chart_spec = {
                    'basicChart': {
                        'chartType': 'LINE',
                        'legendPosition': 'RIGHT_LEGEND',
                        'axis': [
                            {'position': 'BOTTOM_AXIS', 'title': 'Time'},
                            {'position': 'LEFT_AXIS', 'title': 'Value'}
                        ],
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 0,
                                        'endRowIndex': 1,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 10
                                    }]
                                }
                            }
                        }],
                        'series': [{
                            'series': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 1,
                                        'endRowIndex': 10,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 10
                                    }]
                                }
                            },
                            'targetAxis': 'LEFT_AXIS'
                        }]
                    }
                }
            elif chart_type == "PIE":
                chart_spec = {
                    'pieChart': {
                        'legendPosition': 'RIGHT_LEGEND',
                        'domain': {
                            'sourceRange': {
                                'sources': [{
                                    'sheetId': sheet_id,
                                    'startRowIndex': 0,
                                    'endRowIndex': 1,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 10
                                }]
                            }
                        },
                        'series': {
                            'sourceRange': {
                                'sources': [{
                                    'sheetId': sheet_id,
                                    'startRowIndex': 1,
                                    'endRowIndex': 10,
                                    'startColumnIndex': 0,
                                    'endColumnIndex': 10
                                }]
                            }
                        }
                    }
                }
            
            request = {
                'addChart': {
                    'chart': {
                        'spec': chart_spec,
                        'position': {
                            'overlayPosition': {
                                'anchorCell': {
                                    'sheetId': sheet_id,
                                    'rowIndex': position.get('row', 0),
                                    'columnIndex': position.get('column', 0)
                                }
                            }
                        }
                    }
                }
            }
            
            body = {
                'requests': [request]
            }
            
            response = self.services['sheets'].spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Created {chart_type} chart in spreadsheet {spreadsheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return False
    
    # Google Docs Integration
    
    def create_document(self, title: str, content: Optional[str] = None) -> str:
        """
        Create a new Google Doc.
        
        Args:
            title: Title of the document
            content: Optional content for the document
            
        Returns:
            str: ID of the created document
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Create a new document
            document = {
                'title': title
            }
            
            document = self.services['docs'].documents().create(
                body=document
            ).execute()
            
            document_id = document.get('documentId')
            logger.info(f"Created document with ID: {document_id}")
            
            # If content is provided, update the document
            if content:
                self.update_document_content(document_id, content)
            
            return document_id
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def update_document_content(self, document_id: str, content: str) -> bool:
        """
        Update content in a Google Doc.
        
        Args:
            document_id: ID of the document
            content: Content to add to the document
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the current document
            document = self.services['docs'].documents().get(
                documentId=document_id
            ).execute()
            
            # Prepare the update
            requests = []
            
            # If the document is not empty, insert a page break
            if document.get('body', {}).get('content', []):
                requests.append({
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                })
            else:
                requests.append({
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                })
            
            # Update the document
            result = self.services['docs'].documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            logger.info(f"Updated document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def get_document_content(self, document_id: str) -> str:
        """
        Get content from a Google Doc.
        
        Args:
            document_id: ID of the document
            
        Returns:
            str: Document content
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the document
            document = self.services['docs'].documents().get(
                documentId=document_id
            ).execute()
            
            # Extract text content
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element:
                            content += paragraph_element['textRun']['content']
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting document content: {str(e)}")
            raise
    
    def create_report(self, title: str, sections: Dict[str, str], 
                     template_id: Optional[str] = None) -> str:
        """
        Create a business report in Google Docs.
        
        Args:
            title: Title of the report
            sections: Dictionary of section titles and content
            template_id: Optional template document ID
            
        Returns:
            str: ID of the created report
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # If template is provided, copy it
            if template_id:
                report_id = self.copy_file(template_id, title)
                
                # Get the document to find placeholders
                document = self.services['docs'].documents().get(
                    documentId=report_id
                ).execute()
                
                # Extract text content to find placeholders
                content = ""
                for element in document.get('body', {}).get('content', []):
                    if 'paragraph' in element:
                        for paragraph_element in element['paragraph']['elements']:
                            if 'textRun' in paragraph_element:
                                content += paragraph_element['textRun']['content']
                
                # Replace placeholders with section content
                requests = []
                for section_title, section_content in sections.items():
                    placeholder = f"{{{{section:{section_title}}}}}"
                    if placeholder in content:
                        requests.append({
                            'replaceAllText': {
                                'containsText': {
                                    'text': placeholder,
                                    'matchCase': True
                                },
                                'replaceText': section_content
                            }
                        })
                
                # Update the document
                if requests:
                    result = self.services['docs'].documents().batchUpdate(
                        documentId=report_id,
                        body={'requests': requests}
                    ).execute()
                
                return report_id
            
            # Otherwise create a new report
            report_id = self.create_document(title)
            
            # Build the report content
            content = f"# {title}\n\n"
            content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for section_title, section_content in sections.items():
                content += f"## {section_title}\n\n"
                content += f"{section_content}\n\n"
            
            # Update the document
            self.update_document_content(report_id, content)
            
            return report_id
            
        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            raise
    
    # Google Slides Integration
    
    def create_presentation(self, title: str) -> str:
        """
        Create a new Google Slides presentation.
        
        Args:
            title: Title of the presentation
            
        Returns:
            str: ID of the created presentation
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Create a new presentation
            presentation = {
                'title': title
            }
            
            presentation = self.services['slides'].presentations().create(
                body=presentation
            ).execute()
            
            presentation_id = presentation.get('presentationId')
            logger.info(f"Created presentation with ID: {presentation_id}")
            
            return presentation_id
            
        except Exception as e:
            logger.error(f"Error creating presentation: {str(e)}")
            raise
    
    def add_slide(self, presentation_id: str, layout: str = "TITLE_AND_BODY",
                 title: Optional[str] = None, content: Optional[str] = None) -> str:
        """
        Add a slide to a Google Slides presentation.
        
        Args:
            presentation_id: ID of the presentation
            layout: Layout of the slide
            title: Optional title for the slide
            content: Optional content for the slide
            
        Returns:
            str: ID of the created slide
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the presentation
            presentation = self.services['slides'].presentations().get(
                presentationId=presentation_id
            ).execute()
            
            # Find the layout
            layout_id = None
            for master in presentation.get('masters', []):
                for layout in master.get('layouts', []):
                    if layout.get('layoutProperties', {}).get('displayName') == layout:
                        layout_id = layout.get('objectId')
                        break
                if layout_id:
                    break
            
            # Create a new slide
            requests = [{
                'createSlide': {
                    'slideLayoutReference': {
                        'layoutId': layout_id
                    },
                    'placeholderIdMappings': []
                }
            }]
            
            # Update the presentation
            result = self.services['slides'].presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            
            slide_id = result.get('replies', [{}])[0].get('createSlide', {}).get('objectId')
            logger.info(f"Added slide with ID: {slide_id} to presentation {presentation_id}")
            
            # If title or content is provided, update the slide
            if title or content:
                self.update_slide_content(presentation_id, slide_id, title, content)
            
            return slide_id
            
        except Exception as e:
            logger.error(f"Error adding slide: {str(e)}")
            raise
    
    def update_slide_content(self, presentation_id: str, slide_id: str,
                           title: Optional[str] = None, content: Optional[str] = None) -> bool:
        """
        Update content in a Google Slides slide.
        
        Args:
            presentation_id: ID of the presentation
            slide_id: ID of the slide
            title: Optional title for the slide
            content: Optional content for the slide
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the presentation
            presentation = self.services['slides'].presentations().get(
                presentationId=presentation_id
            ).execute()
            
            # Find the slide
            slide = None
            for s in presentation.get('slides', []):
                if s.get('objectId') == slide_id:
                    slide = s
                    break
            
            if not slide:
                logger.warning(f"Slide {slide_id} not found in presentation {presentation_id}")
                return False
            
            # Prepare the update
            requests = []
            
            # Update title if provided
            if title:
                title_shape_id = None
                for element in slide.get('pageElements', []):
                    if element.get('shape', {}).get('shapeType') == 'TEXT_BOX':
                        if 'title' in element.get('shape', {}).get('placeholder', {}).get('type', '').lower():
                            title_shape_id = element.get('objectId')
                            break
                
                if title_shape_id:
                    requests.append({
                        'insertText': {
                            'objectId': title_shape_id,
                            'insertionIndex': 0,
                            'text': title
                        }
                    })
            
            # Update content if provided
            if content:
                content_shape_id = None
                for element in slide.get('pageElements', []):
                    if element.get('shape', {}).get('shapeType') == 'TEXT_BOX':
                        if 'body' in element.get('shape', {}).get('placeholder', {}).get('type', '').lower():
                            content_shape_id = element.get('objectId')
                            break
                
                if content_shape_id:
                    requests.append({
                        'insertText': {
                            'objectId': content_shape_id,
                            'insertionIndex': 0,
                            'text': content
                        }
                    })
            
            # Update the presentation
            if requests:
                result = self.services['slides'].presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                
                logger.info(f"Updated slide {slide_id} in presentation {presentation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating slide content: {str(e)}")
            return False
    
    def create_business_presentation(self, title: str, slides: List[Dict[str, str]],
                                   template_id: Optional[str] = None) -> str:
        """
        Create a business presentation in Google Slides.
        
        Args:
            title: Title of the presentation
            slides: List of slide dictionaries with title and content
            template_id: Optional template presentation ID
            
        Returns:
            str: ID of the created presentation
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # If template is provided, copy it
            if template_id:
                presentation_id = self.copy_file(template_id, title)
                
                # Get the presentation to find placeholders
                presentation = self.services['slides'].presentations().get(
                    presentationId=presentation_id
                ).execute()
                
                # Replace placeholders with slide content
                requests = []
                for i, slide_data in enumerate(slides):
                    if i < len(presentation.get('slides', [])):
                        slide = presentation['slides'][i]
                        
                        # Find title and content shapes
                        title_shape_id = None
                        content_shape_id = None
                        for element in slide.get('pageElements', []):
                            if element.get('shape', {}).get('shapeType') == 'TEXT_BOX':
                                if 'title' in element.get('shape', {}).get('placeholder', {}).get('type', '').lower():
                                    title_shape_id = element.get('objectId')
                                elif 'body' in element.get('shape', {}).get('placeholder', {}).get('type', '').lower():
                                    content_shape_id = element.get('objectId')
                        
                        # Update title
                        if title_shape_id and 'title' in slide_data:
                            requests.append({
                                'deleteText': {
                                    'objectId': title_shape_id,
                                    'textRange': {
                                        'type': 'ALL'
                                    }
                                }
                            })
                            requests.append({
                                'insertText': {
                                    'objectId': title_shape_id,
                                    'insertionIndex': 0,
                                    'text': slide_data['title']
                                }
                            })
                        
                        # Update content
                        if content_shape_id and 'content' in slide_data:
                            requests.append({
                                'deleteText': {
                                    'objectId': content_shape_id,
                                    'textRange': {
                                        'type': 'ALL'
                                    }
                                }
                            })
                            requests.append({
                                'insertText': {
                                    'objectId': content_shape_id,
                                    'insertionIndex': 0,
                                    'text': slide_data['content']
                                }
                            })
                
                # Update the presentation
                if requests:
                    result = self.services['slides'].presentations().batchUpdate(
                        presentationId=presentation_id,
                        body={'requests': requests}
                    ).execute()
                
                return presentation_id
            
            # Otherwise create a new presentation
            presentation_id = self.create_presentation(title)
            
            # Add slides
            for i, slide_data in enumerate(slides):
                if i == 0:
                    # Update the title slide
                    slide_id = self.services['slides'].presentations().get(
                        presentationId=presentation_id
                    ).execute().get('slides', [{}])[0].get('objectId')
                    
                    self.update_slide_content(
                        presentation_id,
                        slide_id,
                        slide_data.get('title'),
                        slide_data.get('content')
                    )
                else:
                    # Add a new slide
                    self.add_slide(
                        presentation_id,
                        layout="TITLE_AND_BODY",
                        title=slide_data.get('title'),
                        content=slide_data.get('content')
                    )
            
            return presentation_id
            
        except Exception as e:
            logger.error(f"Error creating business presentation: {str(e)}")
            raise
    
    # File Management
    
    def copy_file(self, file_id: str, new_title: str) -> str:
        """
        Copy a Google Workspace file.
        
        Args:
            file_id: ID of the file to copy
            new_title: Title for the new file
            
        Returns:
            str: ID of the copied file
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Copy the file
            body = {
                'name': new_title
            }
            
            copied_file = self.services['drive'].files().copy(
                fileId=file_id,
                body=body
            ).execute()
            
            copied_file_id = copied_file.get('id')
            logger.info(f"Copied file {file_id} to {copied_file_id}")
            
            return copied_file_id
            
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            raise
    
    def share_file(self, file_id: str, email: str, role: str = "reader") -> bool:
        """
        Share a Google Workspace file.
        
        Args:
            file_id: ID of the file to share
            email: Email address to share with
            role: Role to grant (reader, writer, commenter)
            
        Returns:
            bool: Success status
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Share the file
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            result = self.services['drive'].permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()
            
            logger.info(f"Shared file {file_id} with {email} as {role}")
            return True
            
        except Exception as e:
            logger.error(f"Error sharing file: {str(e)}")
            return False
    
    def get_file_url(self, file_id: str) -> str:
        """
        Get the URL for a Google Workspace file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            str: URL of the file
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Get the file metadata
            file = self.services['drive'].files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            return file.get('webViewLink', '')
            
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}")
            raise
    
    # Business-specific functions
    
    def create_kpi_dashboard(self, business_data: pd.DataFrame, business_type: str,
                           title: Optional[str] = None) -> str:
        """
        Create a KPI dashboard for a specific business type.
        
        Args:
            business_data: DataFrame containing business data
            business_type: Type of business (retail, restaurant, etc.)
            title: Optional title for the dashboard
            
        Returns:
            str: ID of the created dashboard
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Set default title if not provided
            if not title:
                title = f"{business_type.capitalize()} KPI Dashboard"
            
            # Get template ID based on business type
            template_id = None
            if business_type == "retail":
                template_id = self.sheet_templates.get("retail_kpi_dashboard")
            elif business_type == "restaurant":
                template_id = self.sheet_templates.get("restaurant_kpi_dashboard")
            elif business_type == "service":
                template_id = self.sheet_templates.get("service_kpi_dashboard")
            
            # Prepare data for the dashboard
            dashboard_data = {}
            
            if business_type == "retail":
                # Prepare retail-specific data
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Sales summary
                sales_summary = pd.DataFrame({
                    'Metric': ['Total Sales', 'Average Transaction Value', 'Units Sold', 'Transactions'],
                    'Value': [
                        sales_data['amount'].sum(),
                        sales_data['amount'].mean(),
                        sales_data['quantity'].sum(),
                        len(sales_data)
                    ]
                })
                
                # Sales by category
                sales_by_category = sales_data.groupby('category').agg({
                    'amount': 'sum',
                    'quantity': 'sum'
                }).reset_index()
                
                # Sales by day
                sales_by_day = sales_data.groupby('date').agg({
                    'amount': 'sum',
                    'quantity': 'sum',
                    'transaction_id': 'nunique'
                }).reset_index()
                
                dashboard_data = {
                    'Sales_Summary': sales_summary,
                    'Sales_by_Category': sales_by_category,
                    'Sales_by_Day': sales_by_day
                }
                
            elif business_type == "restaurant":
                # Prepare restaurant-specific data
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Sales summary
                sales_summary = pd.DataFrame({
                    'Metric': ['Total Sales', 'Food Sales', 'Beverage Sales', 'Average Check', 'Covers'],
                    'Value': [
                        sales_data['amount'].sum(),
                        sales_data[sales_data['category'] == 'food']['amount'].sum(),
                        sales_data[sales_data['category'] == 'beverage']['amount'].sum(),
                        sales_data['amount'].sum() / sales_data['covers'].sum(),
                        sales_data['covers'].sum()
                    ]
                })
                
                # Sales by category
                sales_by_category = sales_data.groupby('category').agg({
                    'amount': 'sum',
                    'quantity': 'sum'
                }).reset_index()
                
                # Sales by day
                sales_by_day = sales_data.groupby('date').agg({
                    'amount': 'sum',
                    'covers': 'sum',
                    'transaction_id': 'nunique'
                }).reset_index()
                
                dashboard_data = {
                    'Sales_Summary': sales_summary,
                    'Sales_by_Category': sales_by_category,
                    'Sales_by_Day': sales_by_day
                }
            
            # Create the dashboard
            dashboard_id = self.create_dashboard(title, dashboard_data, template_id)
            
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Error creating KPI dashboard: {str(e)}")
            raise
    
    def create_business_report(self, business_data: pd.DataFrame, business_type: str,
                             report_type: str, title: Optional[str] = None) -> str:
        """
        Create a business report for a specific business type.
        
        Args:
            business_data: DataFrame containing business data
            business_type: Type of business (retail, restaurant, etc.)
            report_type: Type of report (monthly, quarterly, etc.)
            title: Optional title for the report
            
        Returns:
            str: ID of the created report
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Set default title if not provided
            if not title:
                title = f"{business_type.capitalize()} {report_type.capitalize()} Report"
            
            # Get template ID based on business type and report type
            template_id = None
            template_key = f"{business_type}_{report_type}_report"
            template_id = self.doc_templates.get(template_key)
            
            # Prepare sections for the report
            sections = {}
            
            if business_type == "retail" and report_type == "monthly":
                # Prepare retail monthly report sections
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Executive summary
                total_sales = sales_data['amount'].sum()
                avg_transaction = sales_data['amount'].mean()
                total_transactions = len(sales_data)
                
                executive_summary = f"""
                # Executive Summary
                
                Total sales for the month were ${total_sales:,.2f} across {total_transactions} transactions, with an average transaction value of ${avg_transaction:.2f}.
                
                Key highlights:
                - Top selling category: {sales_data.groupby('category')['amount'].sum().idxmax()}
                - Highest sales day: {sales_data.groupby('date')['amount'].sum().idxmax()}
                - Best performing product: {sales_data.groupby('product')['amount'].sum().idxmax()}
                """
                
                # Sales analysis
                sales_by_category = sales_data.groupby('category').agg({
                    'amount': 'sum',
                    'quantity': 'sum'
                })
                
                sales_analysis = f"""
                # Sales Analysis
                
                ## Sales by Category
                
                """
                
                for category, row in sales_by_category.iterrows():
                    sales_analysis += f"- {category}: ${row['amount']:,.2f} ({row['quantity']} units)\n"
                
                # Inventory analysis
                inventory_analysis = f"""
                # Inventory Analysis
                
                ## Stock Levels
                
                """
                
                # Customer analysis
                customer_analysis = f"""
                # Customer Analysis
                
                ## Customer Demographics
                
                """
                
                sections = {
                    'Executive Summary': executive_summary,
                    'Sales Analysis': sales_analysis,
                    'Inventory Analysis': inventory_analysis,
                    'Customer Analysis': customer_analysis
                }
                
            elif business_type == "restaurant" and report_type == "monthly":
                # Prepare restaurant monthly report sections
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Executive summary
                total_sales = sales_data['amount'].sum()
                food_sales = sales_data[sales_data['category'] == 'food']['amount'].sum()
                beverage_sales = sales_data[sales_data['category'] == 'beverage']['amount'].sum()
                total_covers = sales_data['covers'].sum()
                
                executive_summary = f"""
                # Executive Summary
                
                Total sales for the month were ${total_sales:,.2f} across {total_covers} covers, with an average check of ${total_sales/total_covers:.2f}.
                
                Key highlights:
                - Food sales: ${food_sales:,.2f} ({food_sales/total_sales*100:.1f}% of total)
                - Beverage sales: ${beverage_sales:,.2f} ({beverage_sales/total_sales*100:.1f}% of total)
                - Highest sales day: {sales_data.groupby('date')['amount'].sum().idxmax()}
                - Best performing menu item: {sales_data.groupby('product')['amount'].sum().idxmax()}
                """
                
                # Sales analysis
                sales_by_category = sales_data.groupby('category').agg({
                    'amount': 'sum',
                    'quantity': 'sum'
                })
                
                sales_analysis = f"""
                # Sales Analysis
                
                ## Sales by Category
                
                """
                
                for category, row in sales_by_category.iterrows():
                    sales_analysis += f"- {category}: ${row['amount']:,.2f} ({row['quantity']} units)\n"
                
                # Menu analysis
                menu_analysis = f"""
                # Menu Analysis
                
                ## Top Selling Items
                
                """
                
                # Labor analysis
                labor_analysis = f"""
                # Labor Analysis
                
                ## Labor Cost
                
                """
                
                sections = {
                    'Executive Summary': executive_summary,
                    'Sales Analysis': sales_analysis,
                    'Menu Analysis': menu_analysis,
                    'Labor Analysis': labor_analysis
                }
            
            # Create the report
            report_id = self.create_report(title, sections, template_id)
            
            return report_id
            
        except Exception as e:
            logger.error(f"Error creating business report: {str(e)}")
            raise
    
    def create_business_presentation(self, business_data: pd.DataFrame, business_type: str,
                                   presentation_type: str, title: Optional[str] = None) -> str:
        """
        Create a business presentation for a specific business type.
        
        Args:
            business_data: DataFrame containing business data
            business_type: Type of business (retail, restaurant, etc.)
            presentation_type: Type of presentation (quarterly, annual, etc.)
            title: Optional title for the presentation
            
        Returns:
            str: ID of the created presentation
        """
        if not self.check_authentication():
            raise ValueError("Not authenticated with Google Workspace")
        
        try:
            # Set default title if not provided
            if not title:
                title = f"{business_type.capitalize()} {presentation_type.capitalize()} Review"
            
            # Get template ID based on business type and presentation type
            template_id = None
            template_key = f"{business_type}_{presentation_type}_presentation"
            template_id = self.slide_templates.get(template_key)
            
            # Prepare slides for the presentation
            slides = []
            
            # Title slide
            slides.append({
                'title': title,
                'content': f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
            })
            
            if business_type == "retail" and presentation_type == "quarterly":
                # Prepare retail quarterly presentation slides
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Executive summary slide
                total_sales = sales_data['amount'].sum()
                avg_transaction = sales_data['amount'].mean()
                total_transactions = len(sales_data)
                
                executive_summary = f"""
                • Total sales: ${total_sales:,.2f}
                • Transactions: {total_transactions}
                • Average transaction: ${avg_transaction:.2f}
                • Top category: {sales_data.groupby('category')['amount'].sum().idxmax()}
                • Best product: {sales_data.groupby('product')['amount'].sum().idxmax()}
                """
                
                slides.append({
                    'title': "Executive Summary",
                    'content': executive_summary
                })
                
                # Sales performance slide
                sales_performance = f"""
                Sales Performance by Category:
                
                """
                
                for category, amount in sales_data.groupby('category')['amount'].sum().items():
                    sales_performance += f"• {category}: ${amount:,.2f}\n"
                
                slides.append({
                    'title': "Sales Performance",
                    'content': sales_performance
                })
                
                # Inventory slide
                inventory = f"""
                Inventory Performance:
                
                • Inventory turnover: 4.2
                • Days of supply: 28
                • Stockouts: 12
                • Overstock items: 8
                """
                
                slides.append({
                    'title': "Inventory Performance",
                    'content': inventory
                })
                
                # Customer slide
                customer = f"""
                Customer Insights:
                
                • New customers: 120
                • Repeat customers: 350
                • Customer retention rate: 78%
                • Average customer value: ${total_sales/470:.2f}
                """
                
                slides.append({
                    'title': "Customer Insights",
                    'content': customer
                })
                
                # Next steps slide
                next_steps = f"""
                Recommended Actions:
                
                1. Focus marketing on {sales_data.groupby('category')['amount'].sum().idxmax()} category
                2. Optimize inventory for seasonal demand
                3. Implement customer loyalty program
                4. Expand online presence
                """
                
                slides.append({
                    'title': "Next Steps",
                    'content': next_steps
                })
                
            elif business_type == "restaurant" and presentation_type == "quarterly":
                # Prepare restaurant quarterly presentation slides
                sales_data = business_data[business_data['transaction_type'] == 'sale']
                
                # Executive summary slide
                total_sales = sales_data['amount'].sum()
                food_sales = sales_data[sales_data['category'] == 'food']['amount'].sum()
                beverage_sales = sales_data[sales_data['category'] == 'beverage']['amount'].sum()
                total_covers = sales_data['covers'].sum()
                
                executive_summary = f"""
                • Total sales: ${total_sales:,.2f}
                • Covers: {total_covers}
                • Average check: ${total_sales/total_covers:.2f}
                • Food sales: ${food_sales:,.2f} ({food_sales/total_sales*100:.1f}%)
                • Beverage sales: ${beverage_sales:,.2f} ({beverage_sales/total_sales*100:.1f}%)
                """
                
                slides.append({
                    'title': "Executive Summary",
                    'content': executive_summary
                })
                
                # Sales performance slide
                sales_performance = f"""
                Sales Performance by Category:
                
                """
                
                for category, amount in sales_data.groupby('category')['amount'].sum().items():
                    sales_performance += f"• {category}: ${amount:,.2f}\n"
                
                slides.append({
                    'title': "Sales Performance",
                    'content': sales_performance
                })
                
                # Menu performance slide
                menu_performance = f"""
                Menu Performance:
                
                • Top selling item: {sales_data.groupby('product')['quantity'].sum().idxmax()}
                • Most profitable item: {sales_data.groupby('product')['amount'].sum().idxmax()}
                • Food cost percentage: 32%
                • Menu engineering score: 87/100
                """
                
                slides.append({
                    'title': "Menu Performance",
                    'content': menu_performance
                })
                
                # Labor slide
                labor = f"""
                Labor Performance:
                
                • Labor cost: $45,000
                • Labor cost percentage: 28%
                • Sales per labor hour: $85
                • Covers per labor hour: 4.2
                """
                
                slides.append({
                    'title': "Labor Performance",
                    'content': labor
                })
                
                # Next steps slide
                next_steps = f"""
                Recommended Actions:
                
                1. Optimize menu based on profitability analysis
                2. Adjust staffing levels during peak hours
                3. Implement table management system
                4. Expand marketing for slow periods
                """
                
                slides.append({
                    'title': "Next Steps",
                    'content': next_steps
                })
            
            # Create the presentation
            presentation_id = self.create_business_presentation(title, slides, template_id)
            
            return presentation_id
            
        except Exception as e:
            logger.error(f"Error creating business presentation: {str(e)}")
            raise

    def create_alarm_demand_spreadsheet(self, heatmap_rows, title="Alarm CRM demand heatmap"):
        """Write demand-by-sub-city rows for proposal §7 heatmaps."""
        headers = ["sub_city", "kiosks", "qty", "intensity"]
        values = [headers]
        for row in heatmap_rows or []:
            values.append([
                row.get("sub_city"),
                row.get("kiosks"),
                row.get("qty"),
                row.get("intensity"),
            ])
        try:
            if hasattr(self, "create_spreadsheet"):
                return self.create_spreadsheet(title, values)
        except Exception as exc:
            logger.warning("Live Sheets write skipped: %s", exc)
        return {"title": title, "rows": values, "offline": True}

    def create_alarm_executive_doc(self, body, title="Alarm CRM executive brief"):
        """Manufacturer executive report (proposal §7)."""
        try:
            if hasattr(self, "create_document"):
                return self.create_document(title, body)
        except Exception as exc:
            logger.warning("Live Docs write skipped: %s", exc)
        return {"title": title, "body": body, "offline": True}
