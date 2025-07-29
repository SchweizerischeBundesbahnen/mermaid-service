from pydantic import BaseModel, Field


class VersionSchema(BaseModel):
    """Schema for response /version"""

    python: str = Field(description="Python version")
    mermaidCli: str = Field(description="Mermaid CLI version")
    mermaidService: str = Field(description="Service version")
    timestamp: str = Field(description="Build timestamp")
