

from pydantic_settings import BaseSettings, SettingsConfigDict 


class JarvisSettings(BaseSettings):     
    model_config = SettingsConfigDict(        
        env_prefix='J_',        
        env_file='.env' 
    )   
    api_key: str     
    log_level: str = "DEBUG"     
    server_port: int = 8000
    

settings = JarvisSettings() 
print(f"Server starting on port: {settings.server_port}")
print(f"Logging set to: {settings.log_level}")
print(f"API Key used: {settings.api_key}")