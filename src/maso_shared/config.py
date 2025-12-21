"""
Tenant Configuration Base Classes

This module provides base configuration classes for multi-tenant applications.
Both voice_agent and boulesclub can extend these for their specific needs.
"""
import os
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class BaseTenantConfig:
    """
    Base tenant configuration with settings shared across all apps.
    
    This includes:
    - Tenant/organisation identity
    - Business information
    - Contact details
    - Database settings
    - Common feature flags
    
    App-specific settings (voice, WhatsApp, etc.) should be in subclasses.
    """
    
    # ============================================================================
    # TENANT IDENTITY
    # ============================================================================
    
    tenant_id: str = ""
    organisation_id: Optional[int] = None
    
    # ============================================================================
    # BUSINESS INFO
    # ============================================================================
    
    business_name: str = ""
    business_name_spoken: str = ""  # For TTS pronunciation
    source_url: str = ""
    website_url: str = ""
    
    # ============================================================================
    # CONTACT INFORMATION
    # ============================================================================
    
    business_email: str = ""
    business_phone: str = ""
    
    # ============================================================================
    # BUSINESS RULES
    # ============================================================================
    
    cancellation_hours: int = 72
    timezone: str = "Europe/Amsterdam"
    default_language: str = "nl"
    
    # ============================================================================
    # INFRASTRUCTURE
    # ============================================================================
    
    app_url: str = ""
    database_url: str = ""
    
    # ============================================================================
    # KNOWLEDGE BASE
    # ============================================================================
    
    kb_refresh_interval: int = 300  # seconds (5 minutes)
    
    # ============================================================================
    # FEATURE FLAGS (common to all apps)
    # ============================================================================
    
    enable_reservations: bool = True
    enable_lost_items: bool = True
    enable_reservation_changes: bool = True
    
    @classmethod
    def from_env(cls) -> "BaseTenantConfig":
        """Create config from environment variables"""
        org_id = os.getenv("ORGANISATION_ID")
        return cls(
            tenant_id=os.getenv("TENANT_ID", ""),
            organisation_id=int(org_id) if org_id else None,
            business_name=os.getenv("BUSINESS_NAME", ""),
            business_name_spoken=os.getenv("BUSINESS_NAME_SPOKEN", ""),
            source_url=os.getenv("SOURCE_URL", ""),
            website_url=os.getenv("WEBSITE_URL", ""),
            business_email=os.getenv("BUSINESS_EMAIL", ""),
            business_phone=os.getenv("BUSINESS_PHONE", ""),
            cancellation_hours=int(os.getenv("CANCELLATION_HOURS", "72")),
            timezone=os.getenv("TIMEZONE", "Europe/Amsterdam"),
            default_language=os.getenv("DEFAULT_LANGUAGE", "nl"),
            app_url=os.getenv("APP_URL", ""),
            database_url=os.getenv("DATABASE_URL", ""),
            kb_refresh_interval=int(os.getenv("KB_REFRESH_INTERVAL", "300")),
            enable_reservations=os.getenv("ENABLE_RESERVATIONS", "true").lower() == "true",
            enable_lost_items=os.getenv("ENABLE_LOST_ITEMS", "true").lower() == "true",
            enable_reservation_changes=os.getenv("ENABLE_RESERVATION_CHANGES", "true").lower() == "true",
        )
    
    def validate(self) -> list[str]:
        """Validate required configuration. Returns list of errors."""
        errors = []
        
        if not self.tenant_id:
            errors.append("tenant_id is required")
        if not self.organisation_id:
            errors.append("organisation_id is required")
        if not self.business_name:
            errors.append("business_name is required")
        if not self.database_url:
            errors.append("database_url is required")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if config is valid"""
        return len(self.validate()) == 0


class TenantConfigStatic:
    """
    Static tenant configuration class (backward compatible with voice_agent).
    
    Uses class attributes loaded from environment variables.
    For new code, prefer BaseTenantConfig dataclass.
    """
    
    # ============================================================================
    # TENANT IDENTITY
    # ============================================================================
    
    TENANT_ID: str = os.getenv("TENANT_ID", "")
    ORGANISATION_ID: Optional[str] = os.getenv("ORGANISATION_ID")
    
    # ============================================================================
    # BUSINESS INFO
    # ============================================================================
    
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "")
    BUSINESS_NAME_SPOKEN: str = os.getenv("BUSINESS_NAME_SPOKEN", "")
    SOURCE_URL: str = os.getenv("SOURCE_URL", "")
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "")
    
    # ============================================================================
    # CONTACT INFORMATION
    # ============================================================================
    
    BUSINESS_EMAIL: str = os.getenv("BUSINESS_EMAIL", "")
    BUSINESS_PHONE: str = os.getenv("BUSINESS_PHONE", "")
    
    # ============================================================================
    # BUSINESS RULES
    # ============================================================================
    
    CANCELLATION_HOURS: int = int(os.getenv("CANCELLATION_HOURS", "72"))
    TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Amsterdam")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "nl")
    
    # ============================================================================
    # INFRASTRUCTURE
    # ============================================================================
    
    APP_URL: str = os.getenv("APP_URL", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # ============================================================================
    # KNOWLEDGE BASE
    # ============================================================================
    
    KB_REFRESH_INTERVAL: int = int(os.getenv("KB_REFRESH_INTERVAL", "300"))
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    ENABLE_RESERVATIONS: bool = os.getenv("ENABLE_RESERVATIONS", "true").lower() == "true"
    ENABLE_LOST_ITEMS: bool = os.getenv("ENABLE_LOST_ITEMS", "true").lower() == "true"
    ENABLE_RESERVATION_CHANGES: bool = os.getenv("ENABLE_RESERVATION_CHANGES", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration."""
        errors = []
        if not cls.TENANT_ID:
            errors.append("TENANT_ID is required")
        if not cls.ORGANISATION_ID:
            errors.append("ORGANISATION_ID is required")
        if not cls.BUSINESS_NAME:
            errors.append("BUSINESS_NAME is required")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)"""
        print("=" * 70)
        print("BASE TENANT CONFIGURATION")
        print("=" * 70)
        print(f"Tenant ID:        {cls.TENANT_ID}")
        print(f"Organisation ID:  {cls.ORGANISATION_ID or 'NULL'}")
        print(f"Business Name:    {cls.BUSINESS_NAME}")
        print(f"Contact Email:    {cls.BUSINESS_EMAIL}")
        print(f"App URL:          {cls.APP_URL}")
        print(f"Language:         {cls.DEFAULT_LANGUAGE}")
        print("=" * 70)
