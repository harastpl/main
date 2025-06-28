import os
import subprocess
import tempfile
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image
import json

logger = logging.getLogger(__name__)


class OrcaSlicerProcessor:
    """Handle STL file processing with OrcaSlicer"""
    
    def __init__(self):
        self.orca_slicer_path = getattr(settings, 'ORCA_SLICER_PATH', 'orca-slicer')
        self.temp_dir = tempfile.mkdtemp()
    
    def process_stl_file(self, stl_file_instance):
        """
        Process STL file with OrcaSlicer to generate preview and estimates
        """
        try:
            stl_file_instance.status = 'processing'
            stl_file_instance.save()
            
            # Create temporary files
            stl_path = stl_file_instance.stl_file.path
            preview_path = os.path.join(self.temp_dir, f'preview_{stl_file_instance.id}.png')
            gcode_path = os.path.join(self.temp_dir, f'output_{stl_file_instance.id}.gcode')
            
            # Generate preview image
            preview_success = self._generate_preview(stl_path, preview_path)
            
            # Generate G-code and estimates
            gcode_success, estimates = self._generate_gcode(stl_path, gcode_path, stl_file_instance)
            
            # Update the model with results
            if preview_success:
                with open(preview_path, 'rb') as f:
                    stl_file_instance.preview_image.save(
                        f'preview_{stl_file_instance.id}.png',
                        ContentFile(f.read()),
                        save=False
                    )
            
            if gcode_success:
                with open(gcode_path, 'rb') as f:
                    stl_file_instance.gcode_file.save(
                        f'gcode_{stl_file_instance.id}.gcode',
                        ContentFile(f.read()),
                        save=False
                    )
                
                # Update estimates
                if estimates:
                    stl_file_instance.estimated_print_time = estimates.get('print_time', '')
                    stl_file_instance.estimated_material_usage = estimates.get('material_usage')
                    stl_file_instance.estimated_cost = estimates.get('cost')
            
            stl_file_instance.status = 'processed'
            stl_file_instance.processed_at = timezone.now()
            stl_file_instance.processing_log = "Successfully processed with OrcaSlicer"
            
        except Exception as e:
            logger.error(f"Error processing STL file {stl_file_instance.id}: {str(e)}")
            stl_file_instance.status = 'failed'
            stl_file_instance.processing_log = f"Processing failed: {str(e)}"
        
        finally:
            stl_file_instance.save()
            self._cleanup_temp_files()
    
    def _generate_preview(self, stl_path, preview_path):
        """Generate preview image from STL file"""
        try:
            # Command to generate preview with OrcaSlicer
            cmd = [
                self.orca_slicer_path,
                '--export-png',
                '--output', preview_path,
                stl_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(preview_path):
                # Optimize the preview image
                self._optimize_preview_image(preview_path)
                return True
            else:
                logger.warning(f"Preview generation failed: {result.stderr}")
                # Create a placeholder preview
                self._create_placeholder_preview(preview_path)
                return True
                
        except subprocess.TimeoutExpired:
            logger.error("Preview generation timed out")
            self._create_placeholder_preview(preview_path)
            return True
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            return False
    
    def _generate_gcode(self, stl_path, gcode_path, stl_file_instance):
        """Generate G-code and extract estimates"""
        try:
            # Create config based on user settings
            config_path = self._create_slicer_config(stl_file_instance)
            
            cmd = [
                self.orca_slicer_path,
                '--load', config_path,
                '--export-gcode',
                '--output', gcode_path,
                stl_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(gcode_path):
                # Extract estimates from G-code comments
                estimates = self._extract_estimates_from_gcode(gcode_path)
                return True, estimates
            else:
                logger.warning(f"G-code generation failed: {result.stderr}")
                return False, None
                
        except subprocess.TimeoutExpired:
            logger.error("G-code generation timed out")
            return False, None
        except Exception as e:
            logger.error(f"Error generating G-code: {str(e)}")
            return False, None
    
    def _create_slicer_config(self, stl_file_instance):
        """Create OrcaSlicer configuration based on user settings"""
        config_path = os.path.join(self.temp_dir, f'config_{stl_file_instance.id}.ini')
        
        # Quality settings mapping
        layer_heights = {
            'draft': '0.3',
            'normal': '0.2',
            'fine': '0.15',
            'ultra_fine': '0.1'
        }
        
        config_content = f"""
[print]
layer_height = {layer_heights.get(stl_file_instance.print_quality, '0.2')}
fill_density = {int(stl_file_instance.infill_percentage)}%
support_material = {'1' if stl_file_instance.supports_needed else '0'}
nozzle_temperature = 210
bed_temperature = 60
print_speed = 50
travel_speed = 120
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return config_path
    
    def _extract_estimates_from_gcode(self, gcode_path):
        """Extract print time and material usage from G-code comments"""
        estimates = {}
        
        try:
            with open(gcode_path, 'r') as f:
                for line in f:
                    if line.startswith(';'):
                        # Look for common G-code comment patterns
                        if 'estimated printing time' in line.lower():
                            # Extract time estimate
                            time_part = line.split(':')[-1].strip()
                            estimates['print_time'] = time_part
                        elif 'filament used' in line.lower() or 'material usage' in line.lower():
                            # Extract material usage
                            try:
                                # Look for numbers followed by 'g' or 'gram'
                                import re
                                match = re.search(r'(\d+\.?\d*)\s*g', line)
                                if match:
                                    estimates['material_usage'] = float(match.group(1))
                            except:
                                pass
            
            # Calculate estimated cost (₹50 per gram - adjust as needed)
            if 'material_usage' in estimates:
                cost_per_gram = 50  # ₹50 per gram
                estimates['cost'] = estimates['material_usage'] * cost_per_gram
        
        except Exception as e:
            logger.error(f"Error extracting estimates: {str(e)}")
        
        return estimates
    
    def _optimize_preview_image(self, image_path):
        """Optimize preview image size and quality"""
        try:
            with Image.open(image_path) as img:
                # Resize if too large
                if img.width > 800 or img.height > 600:
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save with optimization
                img.save(image_path, 'PNG', optimize=True, quality=85)
        except Exception as e:
            logger.error(f"Error optimizing preview image: {str(e)}")
    
    def _create_placeholder_preview(self, preview_path):
        """Create a placeholder preview image"""
        try:
            # Create a simple placeholder image
            img = Image.new('RGB', (400, 300), color='lightgray')
            img.save(preview_path, 'PNG')
        except Exception as e:
            logger.error(f"Error creating placeholder preview: {str(e)}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")


def process_stl_file_async(stl_file_id):
    """
    Process STL file asynchronously
    This function can be called from a Celery task or similar
    """
    try:
        from .models import STLFile
        stl_file = STLFile.objects.get(id=stl_file_id)
        processor = OrcaSlicerProcessor()
        processor.process_stl_file(stl_file)
    except Exception as e:
        logger.error(f"Error in async STL processing: {str(e)}")


def get_file_info(file_path):
    """Get basic information about an STL file"""
    try:
        file_size = os.path.getsize(file_path)
        return {
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return {'size': 0, 'size_mb': 0}