from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, Any, Dict


# Data model for connecting to the switch
class Options(BaseModel):
    """Data model for switch connection settings using netmiko"""
    ip: Optional[IPvAnyAddress]
    host: Optional[IPvAnyAddress]
    username: Optional[str]
    password: Optional[str]
    secret: Optional[str]
    port: int = Field(5010, ge=0, le=65536)
    device_type: str = 'cisco_ios_telnet'
    verbose: bool = False
    global_delay_factor: float = 1.0
    global_cmd_verify: Optional[bool]
    use_keys: bool = False
    key_file: Optional[str]
    pkey: Optional[Any]
    passphrase: Optional[str]
    disabled_algorithms: Optional[Dict[str, Any]] = None
    allow_agent: bool = False
    ssh_strict: bool = False
    system_host_keys: bool = False
    alt_host_keys: bool = False
    alt_key_file: Optional[str]
    ssh_config_file: Optional[str]
    conn_timeout: int = 10
    auth_timeout: Optional[int]
    banner_timeout: int = 15
    blocking_timeout: int = 20
    timeout: int = 100
    session_timeout: int = 60
    read_timeout_override: Optional[float]
    keepalive: int = 0
    default_enter: Optional[str]
    response_return: Optional[str]
    serial_settings: Optional[Dict[str, Any]]
    fast_cli: bool = True
    session_log: Optional[Any] = "session.log"
    session_log_record_writes: bool = False
    session_log_file_mode: str = 'write'
    allow_auto_change: bool = False
    encoding: str = 'utf-8'
    sock: Optional[Any]
    auto_connect: bool = True
    delay_factor_compat: bool = False


# Data model for switch version
class SwVersion(BaseModel):
    """# Data model to store data with switch version"""
    soft_version: Optional[str]
    hard_version: Optional[str]


# Data model for switch configuration
class SwConf(BaseModel):
    """Data model for storing settings for connecting to the switch using netmiko"""
    start_config: Optional[str]
    running_config: Optional[str]


# Data model for all received data
class AllData(BaseModel):
    """Data model for storing all data received from the switch"""
    sw_version: dict = SwVersion().dict()
    sw_config: dict = SwConf().dict()
    sw_acl: Optional[str]
    sw_interface: Optional[str]
    sw_ip_interface: Optional[str]
