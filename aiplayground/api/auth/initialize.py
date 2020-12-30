from redorm.exceptions import UniqueContstraintViolation
from aiplayground.api.auth.models import Role
from aiplayground.logging import logger


def initialize_auth():
    initialize_roles()


ROLES = ["guest", "admin", "user"]


def initialize_roles():
    for role in ROLES:
        try:
            logger.info(f"Creating role: {role}")
            Role.create(name=role, description=role)
        except UniqueContstraintViolation:
            logger.info("Role exists")
