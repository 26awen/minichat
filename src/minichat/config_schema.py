from enum import Enum
import os
import json

from pydantic import BaseModel
from pydantic import ConfigDict


"""
Config before any input
"""
class AiModels(Enum):
    NOMODEL = ""
    GPT4O = "gpt-4o"
    CLAUDE35  = "claude-3-5-sonnet-20240620"
    GPT4OMINI = "gpt-4o-mini"
    GPT35T = "gpt-3.5-turbo"
    SILI = "deepseek-ai/deepseek-coder-v2-Instruct"
    ll3 = "llama3-70b-8192"

class AiRoles(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ClientType(Enum):
    OPENAI = "openai"
    COZE = "coze"
    CLAUDE = "claude"

class CfigServre(BaseModel):
    host: str
    port: int
    secret: str

class CfigCoze(BaseModel):
    end_point: str
    bearer_token: str

    stream: bool

    bot_id: str
    user: str

class CfigOpenai(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    ai_model: AiModels
    openai_key: str | None
    openai_baseurl: str | None

    @property
    def model(self):
        return str(self.ai_model)

class CfigClaude(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    ai_model: AiModels
    claude_key: str | None
    claude_baseurl: str | None

    @property
    def model(self):
        return str(self.ai_model)


class Config(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    client_type: ClientType
    
    cfig_openai: CfigOpenai 
    cfig_coze: CfigCoze
    cfig_claude: CfigClaude
    
    server: CfigServre

    @classmethod
    def load(cls, path: str):
        if os.path.exists(path):
            with open(path, "r", encoding="utf8") as f:
                data = json.load(f)
                return cls(**data)
        else:
            raise FileNotFoundError(f"config file not exist:{path}")
