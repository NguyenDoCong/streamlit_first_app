import os
class Config:
  
# Database configuration
    USER_DATABASE       = os.environ.get("USER_DATABASE", "postgres")
    PASSWORD_DATABASE   = os.environ.get("PASSWORD_DATABASE", "postgres")
    HOST_DATABASE       = os.environ.get("HOST_DATABASE", "localhost")
    PORT_DATABASE       = os.environ.get("PORT_DATABASE", "5432")
    NAME_DATABASE       = os.environ.get("NAME_DATABASE", "postgres")
    URL_DATABASE        = f"postgresql://{USER_DATABASE}:{PASSWORD_DATABASE}@{HOST_DATABASE}:{PORT_DATABASE}/{NAME_DATABASE}"