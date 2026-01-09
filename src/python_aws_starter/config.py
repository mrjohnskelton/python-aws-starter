"""Configuration management for the timeline application."""

from typing import List, Dict, Optional, Any
from enum import Enum


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig:
    """Database configuration."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        engine: str = "postgresql",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.engine = engine


class CacheConfig:
    """Cache/Redis configuration."""

    def __init__(
        self,
        enabled: bool = True,
        host: str = "localhost",
        port: int = 6379,
        ttl_seconds: int = 3600,
    ):
        self.enabled = enabled
        self.host = host
        self.port = port
        self.ttl_seconds = ttl_seconds


class DimensionConfig:
    """Configuration for available dimensions."""

    def __init__(self):
        self.default_dimensions = {
            "timeline": {
                "name": "Timeline",
                "icon": "🕐",
                "color": "#FF6B6B",
                "zoom_levels": ["era", "century", "decade", "year", "month", "day"],
            },
            "geography": {
                "name": "Geography",
                "icon": "🌍",
                "color": "#4ECDC4",
                "zoom_levels": ["continent", "country", "region", "city", "location"],
            },
            "people": {
                "name": "People",
                "icon": "👥",
                "color": "#95E1D3",
                "zoom_levels": ["individual", "organization", "nationality", "group"],
            },
            "events": {
                "name": "Events",
                "icon": "📍",
                "color": "#F38181",
                "zoom_levels": ["event", "episode", "era", "age"],
            },
        }

    def get_all(self) -> Dict[str, Any]:
        """Get all dimension configurations."""
        return self.default_dimensions

    def get(self, dimension_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific dimension configuration."""
        return self.default_dimensions.get(dimension_id)

    def add_custom(self, dimension_id: str, config: Dict[str, Any]) -> None:
        """Add a custom dimension configuration."""
        self.default_dimensions[dimension_id] = config


class ApplicationConfig:
    """Main application configuration."""

    def __init__(
        self,
        environment: Environment = Environment.DEVELOPMENT,
        debug: bool = False,
        database: Optional[DatabaseConfig] = None,
        cache: Optional[CacheConfig] = None,
        wikidata_log_body: bool = False,
        data_log_body_max: int = 1000,
        data_source: str = "local",
        log_level: str = "INFO",
    ):
        self.environment = environment
        self.debug = debug
        self.database = database or DatabaseConfig(
            host="localhost",
            port=5432,
            username="timeline_user",
            password="changeme",
            database="timeline_db",
        )
        self.cache = cache or CacheConfig()
        self.dimensions = DimensionConfig()
        # Data source configuration: 'local' or 'wikidata'
        self.data_source = data_source
        # Wikidata specific options
        self.wikidata_api = {
            "base_url": "https://www.wikidata.org/w/api.php",
            "entity_url": "https://www.wikidata.org/wiki/Special:EntityData/",
            "limit": 10,
        }
        # Logging configuration
        self.log_level = log_level
        # Wikidata response body logging
        self.wikidata_log_body = wikidata_log_body
        self.data_log_body_max = data_log_body_max

    @classmethod
    def from_env(cls) -> "ApplicationConfig":
        """Load configuration from environment variables."""
        import os

        env = Environment(os.getenv("ENVIRONMENT", "development"))
        debug = os.getenv("DEBUG", "false").lower() == "true"

        db = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            username=os.getenv("DB_USER", "timeline_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
            database=os.getenv("DB_NAME", "timeline_db"),
            engine=os.getenv("DB_ENGINE", "postgresql"),
        )

        cache = CacheConfig(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            host=os.getenv("CACHE_HOST", "localhost"),
            port=int(os.getenv("CACHE_PORT", "6379")),
            ttl_seconds=int(os.getenv("CACHE_TTL", "3600")),
        )

        # data source selection
        data_source = os.getenv("DATA_SOURCE", "local")

        # wikidata settings
        wikidata_limit = int(os.getenv("WIKIDATA_LIMIT", "10"))
        wikidata_base = os.getenv("WIKIDATA_API_BASE", "https://www.wikidata.org/w/api.php")
        wikidata_entity = os.getenv("WIKIDATA_ENTITY_BASE", "https://www.wikidata.org/wiki/Special:EntityData/")
        
        # logging settings
        log_level = os.getenv("LOG_LEVEL", "DEBUG" if debug else "INFO")
        
        # wikidata body logging settings
        wikidata_log_body = os.getenv("WIKIDATA_LOG_BODY", "false").lower() == "true"
        data_log_body_max = int(os.getenv("DATA_LOG_BODY_MAX", "1000"))

        inst = cls(
            environment=env,
            debug=debug,
            database=db,
            cache=cache,
            wikidata_log_body=wikidata_log_body,
            data_log_body_max=data_log_body_max,
            data_source=data_source,
            log_level=log_level,
        )
        inst.wikidata_api["limit"] = wikidata_limit
        inst.wikidata_api["base_url"] = wikidata_base
        inst.wikidata_api["entity_url"] = wikidata_entity
        return inst


# Global configuration instance
config = ApplicationConfig.from_env()
