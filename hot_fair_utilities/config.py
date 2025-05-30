"""
Configuration management for fAIr-utilities.

This module provides centralized configuration management with
environment variable support, validation, and production-ready defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from pathlib import Path


@dataclass
class TileDownloadConfig:
    """Configuration for tile downloading operations."""
    
    # Connection settings
    max_concurrent_downloads: int = 10
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    requests_per_second: float = 10.0
    burst_limit: int = 50
    
    # File settings
    cache_directory: str = ".tile_cache"
    max_cache_size_mb: int = 1000
    
    # Safety limits
    max_tiles_per_request: int = 1000
    max_area_sq_degrees: float = 100.0
    
    @classmethod
    def from_env(cls) -> 'TileDownloadConfig':
        """Create configuration from environment variables."""
        return cls(
            max_concurrent_downloads=int(os.getenv('FAIR_MAX_CONCURRENT_DOWNLOADS', 10)),
            timeout_seconds=int(os.getenv('FAIR_TIMEOUT_SECONDS', 30)),
            max_retries=int(os.getenv('FAIR_MAX_RETRIES', 3)),
            retry_delay=float(os.getenv('FAIR_RETRY_DELAY', 1.0)),
            requests_per_second=float(os.getenv('FAIR_REQUESTS_PER_SECOND', 10.0)),
            burst_limit=int(os.getenv('FAIR_BURST_LIMIT', 50)),
            cache_directory=os.getenv('FAIR_CACHE_DIRECTORY', '.tile_cache'),
            max_cache_size_mb=int(os.getenv('FAIR_MAX_CACHE_SIZE_MB', 1000)),
            max_tiles_per_request=int(os.getenv('FAIR_MAX_TILES_PER_REQUEST', 1000)),
            max_area_sq_degrees=float(os.getenv('FAIR_MAX_AREA_SQ_DEGREES', 100.0)),
        )


@dataclass
class ModelConfig:
    """Configuration for model operations."""
    
    # Model cache settings
    cache_directory: str = ".model_cache"
    max_cache_size_gb: int = 10
    cache_cleanup_threshold: float = 0.8
    
    # Download settings
    download_timeout_seconds: int = 300
    max_model_size_gb: int = 5
    verify_checksums: bool = True
    
    # Default model URLs
    default_models: Dict[str, str] = field(default_factory=lambda: {
        'ramp': 'https://api-prod.fair.hotosm.org/api/v1/workspace/download/ramp/baseline.tflite',
        'yolo_v1': 'https://api-prod.fair.hotosm.org/api/v1/workspace/download/yolo/yolov8s_v1-seg.onnx',
        'yolo_v2': 'https://api-prod.fair.hotosm.org/api/v1/workspace/download/yolo/yolov8s_v2-seg.onnx',
    })
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """Create configuration from environment variables."""
        return cls(
            cache_directory=os.getenv('FAIR_MODEL_CACHE_DIRECTORY', '.model_cache'),
            max_cache_size_gb=int(os.getenv('FAIR_MAX_MODEL_CACHE_SIZE_GB', 10)),
            cache_cleanup_threshold=float(os.getenv('FAIR_CACHE_CLEANUP_THRESHOLD', 0.8)),
            download_timeout_seconds=int(os.getenv('FAIR_MODEL_DOWNLOAD_TIMEOUT', 300)),
            max_model_size_gb=int(os.getenv('FAIR_MAX_MODEL_SIZE_GB', 5)),
            verify_checksums=os.getenv('FAIR_VERIFY_CHECKSUMS', 'true').lower() == 'true',
        )


@dataclass
class VectorizationConfig:
    """Configuration for vectorization operations."""
    
    # Algorithm settings
    default_algorithm: str = "rasterio"
    potrace_available: Optional[bool] = None
    
    # Processing settings
    default_simplify_tolerance: float = 0.2
    default_min_area: float = 1.0
    default_orthogonalize: bool = True
    
    # Performance settings
    max_features_per_file: int = 10000
    memory_limit_mb: int = 2000
    
    # Temporary file settings
    temp_directory: str = "temp"
    cleanup_temp_files: bool = True
    
    @classmethod
    def from_env(cls) -> 'VectorizationConfig':
        """Create configuration from environment variables."""
        return cls(
            default_algorithm=os.getenv('FAIR_VECTORIZATION_ALGORITHM', 'rasterio'),
            default_simplify_tolerance=float(os.getenv('FAIR_SIMPLIFY_TOLERANCE', 0.2)),
            default_min_area=float(os.getenv('FAIR_MIN_AREA', 1.0)),
            default_orthogonalize=os.getenv('FAIR_ORTHOGONALIZE', 'true').lower() == 'true',
            max_features_per_file=int(os.getenv('FAIR_MAX_FEATURES_PER_FILE', 10000)),
            memory_limit_mb=int(os.getenv('FAIR_MEMORY_LIMIT_MB', 2000)),
            temp_directory=os.getenv('FAIR_TEMP_DIRECTORY', 'temp'),
            cleanup_temp_files=os.getenv('FAIR_CLEANUP_TEMP_FILES', 'true').lower() == 'true',
        )


@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    
    # URL validation
    allowed_schemes: List[str] = field(default_factory=lambda: ['http', 'https'])
    blocked_hosts: List[str] = field(default_factory=lambda: ['localhost', '127.0.0.1', '0.0.0.0'])
    max_url_length: int = 2048
    
    # File validation
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        '.tif', '.tiff', '.png', '.jpg', '.jpeg', '.geojson', '.json',
        '.pt', '.pth', '.onnx', '.tflite', '.h5', '.pb'
    ])
    max_file_size_mb: int = 1000
    scan_uploads: bool = True
    
    # Input validation
    max_bbox_area: float = 100.0  # square degrees
    max_zoom_level: int = 22
    min_zoom_level: int = 0
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create configuration from environment variables."""
        blocked_hosts = os.getenv('FAIR_BLOCKED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')
        allowed_extensions = os.getenv(
            'FAIR_ALLOWED_EXTENSIONS', 
            '.tif,.tiff,.png,.jpg,.jpeg,.geojson,.json,.pt,.pth,.onnx,.tflite,.h5,.pb'
        ).split(',')
        
        return cls(
            blocked_hosts=[host.strip() for host in blocked_hosts],
            max_url_length=int(os.getenv('FAIR_MAX_URL_LENGTH', 2048)),
            allowed_file_extensions=[ext.strip() for ext in allowed_extensions],
            max_file_size_mb=int(os.getenv('FAIR_MAX_FILE_SIZE_MB', 1000)),
            scan_uploads=os.getenv('FAIR_SCAN_UPLOADS', 'true').lower() == 'true',
            max_bbox_area=float(os.getenv('FAIR_MAX_BBOX_AREA', 100.0)),
            max_zoom_level=int(os.getenv('FAIR_MAX_ZOOM_LEVEL', 22)),
            min_zoom_level=int(os.getenv('FAIR_MIN_ZOOM_LEVEL', 0)),
        )


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    
    # Log levels
    level: str = "INFO"
    file_level: str = "DEBUG"
    
    # File settings
    log_file: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    
    # Format settings
    format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    
    # Performance logging
    log_performance: bool = True
    log_system_stats: bool = True
    performance_threshold_seconds: float = 1.0
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create configuration from environment variables."""
        return cls(
            level=os.getenv('FAIR_LOG_LEVEL', 'INFO'),
            file_level=os.getenv('FAIR_FILE_LOG_LEVEL', 'DEBUG'),
            log_file=os.getenv('FAIR_LOG_FILE'),
            max_file_size_mb=int(os.getenv('FAIR_MAX_LOG_FILE_SIZE_MB', 100)),
            backup_count=int(os.getenv('FAIR_LOG_BACKUP_COUNT', 5)),
            log_performance=os.getenv('FAIR_LOG_PERFORMANCE', 'true').lower() == 'true',
            log_system_stats=os.getenv('FAIR_LOG_SYSTEM_STATS', 'true').lower() == 'true',
            performance_threshold_seconds=float(os.getenv('FAIR_PERFORMANCE_THRESHOLD', 1.0)),
        )


@dataclass
class FairConfig:
    """Main configuration class combining all settings."""
    
    tile_download: TileDownloadConfig = field(default_factory=TileDownloadConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    vectorization: VectorizationConfig = field(default_factory=VectorizationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Global settings
    environment: str = "development"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'FairConfig':
        """Create complete configuration from environment variables."""
        return cls(
            tile_download=TileDownloadConfig.from_env(),
            model=ModelConfig.from_env(),
            vectorization=VectorizationConfig.from_env(),
            security=SecurityConfig.from_env(),
            logging=LoggingConfig.from_env(),
            environment=os.getenv('FAIR_ENVIRONMENT', 'development'),
            debug=os.getenv('FAIR_DEBUG', 'false').lower() == 'true',
        )
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Validate tile download config
        if self.tile_download.max_concurrent_downloads <= 0:
            issues.append("max_concurrent_downloads must be positive")
        
        if self.tile_download.timeout_seconds <= 0:
            issues.append("timeout_seconds must be positive")
        
        # Validate model config
        if self.model.max_model_size_gb <= 0:
            issues.append("max_model_size_gb must be positive")
        
        # Validate vectorization config
        if self.vectorization.default_simplify_tolerance < 0:
            issues.append("default_simplify_tolerance must be non-negative")
        
        # Validate security config
        if self.security.max_bbox_area <= 0:
            issues.append("max_bbox_area must be positive")
        
        if not (0 <= self.security.min_zoom_level <= self.security.max_zoom_level <= 22):
            issues.append("Invalid zoom level range")
        
        return issues
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == 'production'


# Global configuration instance
config = FairConfig.from_env()

# Validate configuration on import
validation_issues = config.validate()
if validation_issues:
    import warnings
    warnings.warn(f"Configuration validation issues: {', '.join(validation_issues)}")


# Default model URLs for backward compatibility
DEFAULT_OAM_TMS_MOSAIC = "https://apps.kontur.io/raster-tiler/oam/mosaic/{z}/{x}/{y}.png"
DEFAULT_RAMP_MODEL = config.model.default_models['ramp']
DEFAULT_YOLO_MODEL_V1 = config.model.default_models['yolo_v1']
DEFAULT_YOLO_MODEL_V2 = config.model.default_models['yolo_v2']


__all__ = [
    'TileDownloadConfig',
    'ModelConfig', 
    'VectorizationConfig',
    'SecurityConfig',
    'LoggingConfig',
    'FairConfig',
    'config',
    'DEFAULT_OAM_TMS_MOSAIC',
    'DEFAULT_RAMP_MODEL',
    'DEFAULT_YOLO_MODEL_V1',
    'DEFAULT_YOLO_MODEL_V2',
]
