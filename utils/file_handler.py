"""
Enterprise File Handling Utilities
Professional file management for agricultural data
"""
import os
import io
import logging
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, BinaryIO
import pandas as pd
import numpy as np
from PIL import Image
import json
import csv
from datetime import datetime
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class FileHandler:
    """Enterprise file handling system with security and validation"""
    
    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 50 * 1024 * 1024):
        self.upload_dir = Path(upload_dir)
        self.max_file_size = max_file_size  # 50MB default
        self.upload_dir.mkdir(exist_ok=True)
        
        # Allowed file types for security
        self.allowed_extensions = {
            'image': {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'},
            'data': {'.csv', '.xlsx', '.xls', '.json'},
            'document': {'.pdf', '.txt', '.md'},
            'archive': {'.zip', '.tar', '.gz'}
        }
        
        # MIME type mappings
        self.mime_mappings = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp',
            'text/csv': '.csv',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/json': '.json',
            'text/plain': '.txt',
            'application/pdf': '.pdf'
        }
    
    def save_uploaded_file(self, uploaded_file, file_category: str = 'data', 
                          custom_name: str = None) -> Dict[str, Any]:
        """Save uploaded file with validation and security checks"""
        try:
            # Validate file
            validation_result = self._validate_uploaded_file(uploaded_file, file_category)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'file_path': None
                }
            
            # Generate secure filename
            if custom_name:
                filename = self._sanitize_filename(custom_name)
            else:
                filename = self._generate_secure_filename(uploaded_file.name)
            
            # Ensure proper extension
            if not any(filename.lower().endswith(ext) for ext in self.allowed_extensions[file_category]):
                # Add extension based on MIME type
                mime_type = getattr(uploaded_file, 'type', None)
                if mime_type in self.mime_mappings:
                    filename += self.mime_mappings[mime_type]
            
            # Create category subdirectory
            category_dir = self.upload_dir / file_category
            category_dir.mkdir(exist_ok=True)
            
            # Full file path
            file_path = category_dir / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.read())
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            logger.info(f"File saved successfully: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'file_info': file_info,
                'category': file_category
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def load_dataset(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load dataset from various file formats"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f"File not found: {file_path}",
                    'data': None
                }
            
            # Determine file type and load accordingly
            extension = file_path.suffix.lower()
            
            if extension == '.csv':
                df = self._load_csv(file_path)
            elif extension in ['.xlsx', '.xls']:
                df = self._load_excel(file_path)
            elif extension == '.json':
                df = self._load_json(file_path)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported file format: {extension}",
                    'data': None
                }
            
            # Basic data validation
            if df.empty:
                return {
                    'success': False,
                    'error': "Dataset is empty",
                    'data': None
                }
            
            # Generate dataset summary
            summary = self._generate_dataset_summary(df)
            
            return {
                'success': True,
                'data': df,
                'summary': summary,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def load_image(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load and preprocess image file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f"Image file not found: {file_path}",
                    'image': None
                }
            
            # Load image using PIL
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image info
            image_info = {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'file_size': file_path.stat().st_size
            }
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return {
                'success': True,
                'image': image,
                'image_array': image_array,
                'image_info': image_info,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return {
                'success': False,
                'error': str(e),
                'image': None
            }
    
    def export_data(self, data: pd.DataFrame, filename: str, 
                   format_type: str = 'csv', include_metadata: bool = True) -> Dict[str, Any]:
        """Export data in various formats"""
        try:
            # Create exports directory
            export_dir = self.upload_dir / 'exports'
            export_dir.mkdir(exist_ok=True)
            
            # Sanitize filename
            clean_filename = self._sanitize_filename(filename)
            
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = clean_filename.rsplit('.', 1)[0] if '.' in clean_filename else clean_filename
            
            if format_type.lower() == 'csv':
                export_path = export_dir / f"{base_name}_{timestamp}.csv"
                data.to_csv(export_path, index=False)
                
            elif format_type.lower() == 'excel':
                export_path = export_dir / f"{base_name}_{timestamp}.xlsx"
                with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                    data.to_excel(writer, sheet_name='Data', index=False)
                    
                    if include_metadata:
                        # Add metadata sheet
                        metadata = self._generate_export_metadata(data)
                        metadata_df = pd.DataFrame(list(metadata.items()), 
                                                 columns=['Attribute', 'Value'])
                        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                        
            elif format_type.lower() == 'json':
                export_path = export_dir / f"{base_name}_{timestamp}.json"
                export_data = {
                    'data': data.to_dict('records'),
                    'metadata': self._generate_export_metadata(data) if include_metadata else {}
                }
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                    
            else:
                return {
                    'success': False,
                    'error': f"Unsupported export format: {format_type}",
                    'file_path': None
                }
            
            file_info = self._get_file_info(export_path)
            
            return {
                'success': True,
                'file_path': str(export_path),
                'filename': export_path.name,
                'format': format_type,
                'file_info': file_info
            }
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def create_report_archive(self, files: List[str], archive_name: str) -> Dict[str, Any]:
        """Create ZIP archive of multiple files"""
        try:
            # Create exports directory
            export_dir = self.upload_dir / 'exports'
            export_dir.mkdir(exist_ok=True)
            
            # Generate archive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name = self._sanitize_filename(archive_name)
            archive_path = export_dir / f"{clean_name}_{timestamp}.zip"
            
            # Create ZIP archive
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    file_path = Path(file_path)
                    if file_path.exists():
                        # Add file to archive with just the filename (no path)
                        zipf.write(file_path, file_path.name)
                    else:
                        logger.warning(f"File not found for archive: {file_path}")
            
            file_info = self._get_file_info(archive_path)
            
            return {
                'success': True,
                'archive_path': str(archive_path),
                'filename': archive_path.name,
                'files_included': len(files),
                'file_info': file_info
            }
            
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            return {
                'success': False,
                'error': str(e),
                'archive_path': None
            }
    
    def clean_old_files(self, days_old: int = 7) -> Dict[str, Any]:
        """Clean old uploaded files"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            freed_space = 0
            
            for file_path in self.upload_dir.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        deleted_count += 1
                        freed_space += file_size
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'freed_space_mb': freed_space / (1024 * 1024),
                'cutoff_days': days_old
            }
            
        except Exception as e:
            logger.error(f"Error cleaning old files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_uploaded_file(self, uploaded_file, file_category: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        # Check file size
        if hasattr(uploaded_file, 'size') and uploaded_file.size:
            if uploaded_file.size > self.max_file_size:
                return {
                    'valid': False,
                    'error': f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
                }
        
        # Check file extension
        if hasattr(uploaded_file, 'name') and uploaded_file.name:
            file_ext = Path(uploaded_file.name).suffix.lower()
            if file_category in self.allowed_extensions:
                if file_ext not in self.allowed_extensions[file_category]:
                    allowed = ', '.join(self.allowed_extensions[file_category])
                    return {
                        'valid': False,
                        'error': f"Invalid file type. Allowed: {allowed}"
                    }
        
        # Check MIME type if available
        if hasattr(uploaded_file, 'type') and uploaded_file.type:
            mime_type = uploaded_file.type
            if mime_type.startswith('application/octet-stream'):
                # Generic binary - check extension instead
                pass
            elif file_category == 'image' and not mime_type.startswith('image/'):
                return {
                    'valid': False,
                    'error': "File is not a valid image"
                }
        
        return {'valid': True, 'error': None}
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace problematic characters
        import re
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure filename is not empty
        if not filename or filename == '.':
            filename = 'unnamed_file'
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        return filename
    
    def _generate_secure_filename(self, original_name: str) -> str:
        """Generate secure filename with timestamp"""
        # Sanitize original name
        clean_name = self._sanitize_filename(original_name)
        
        # Extract name and extension
        name, ext = os.path.splitext(clean_name)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{name}_{timestamp}{ext}"
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            return {
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': file_path.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(file_path))[0]
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {}
    
    def _load_csv(self, file_path: Path) -> pd.DataFrame:
        """Load CSV file with error handling"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                # Try to detect delimiter
                with open(file_path, 'r', encoding=encoding) as f:
                    sample = f.read(1024)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                
                # Load with detected delimiter
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                
                # Validate that we got actual data
                if not df.empty and len(df.columns) > 0:
                    return df
                    
            except Exception as e:
                logger.warning(f"Failed to load CSV with encoding {encoding}: {e}")
                continue
        
        # Fallback to default pandas loading
        return pd.read_csv(file_path)
    
    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """Load Excel file"""
        try:
            # Try to load first sheet
            df = pd.read_excel(file_path, sheet_name=0)
            return df
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            raise
    
    def _load_json(self, file_path: Path) -> pd.DataFrame:
        """Load JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    # Try to convert dict to DataFrame
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Unsupported JSON structure")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            raise
    
    def _generate_dataset_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive dataset summary"""
        summary = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'missing_values': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'data_types': df.dtypes.value_counts().to_dict(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'column_info': {}
        }
        
        # Column-specific information
        for col in df.columns:
            col_info = {
                'type': str(df[col].dtype),
                'non_null_count': df[col].notna().sum(),
                'unique_count': df[col].nunique()
            }
            
            if df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'std': df[col].std()
                })
            
            summary['column_info'][col] = col_info
        
        return summary
    
    def _generate_export_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate metadata for export"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'generated_by': 'Smart Sènè Enterprise Platform'
        }

# Global file handler instance
file_handler = FileHandler()

# Convenience functions for backward compatibility
def save_uploaded_file(uploaded_file, category: str = 'data') -> Dict[str, Any]:
    """Save uploaded file (convenience function)"""
    return file_handler.save_uploaded_file(uploaded_file, category)

def load_dataset(file_path: str) -> Dict[str, Any]:
    """Load dataset (convenience function)"""
    return file_handler.load_dataset(file_path)

def export_data(data: pd.DataFrame, filename: str, format_type: str = 'csv') -> Dict[str, Any]:
    """Export data (convenience function)"""
    return file_handler.export_data(data, filename, format_type)
