from redorm.exceptions import UniqueContstraintViolation, InstanceNotFound
from aiplayground.api.auth.models import Role, User
from aiplayground.logging import logger


def initialize_auth():
    initialize_roles()
    initialize_users()


ROLES = ["guest", "admin", "user"]


def initialize_roles():
    for role in ROLES:
        try:
            logger.info(f"Creating role: {role}")
            Role.create(name=role, description=role)
        except UniqueContstraintViolation:
            logger.info("Role exists")


def initialize_users():
    # TODO: Remove hard coded creds
    email = "test@test.com"
    password = "test"
    try:
        User.get(email=email)
    except InstanceNotFound:
        User.create(email=email, password=password, username="test")
