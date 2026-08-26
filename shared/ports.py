from pydantic import BaseModel


class ServicePorts(BaseModel):
    ui_client: int = 8000
    opportunity_finder: int = 8081
    pipeline_manager: int = 8082
    engagement_listener: int = 8083
    cdr: int = 8084
    mcp: int = 8085
