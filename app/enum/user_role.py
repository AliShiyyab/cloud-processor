import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
