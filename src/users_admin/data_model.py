import os
import sys
from datetime import datetime
from enum import Enum
import uuid

from pydantic import BaseModel


class UserProvider(Enum):
    email = "email"
    google = "google"
    facebook = "facebook"
    twitter = "twitter"
    github = "github"
    linkedin = "linkedin"


class UserRole(Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class UserStatus(Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"
    deleted = "deleted"


class UserDataProxy(BaseModel):
    id: str
    name: str
    email: str
    password: str
    provider: UserProvider
    provider_id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
