from redorm.exceptions import UniqueContstraintViolation, InstanceNotFound
from aiplayground.api.auth.models import Role, User
from aiplayground.logging import logger
from aiplayground.settings import settings


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
    if settings.ADMIN_EMAIL is None or settings.ADMIN_PASSWORD is None:
        logger.info("Skipping creating admin as missing email and/or password")
    try:
        user = User.get(email=settings.ADMIN_EMAIL)
    except InstanceNotFound:
        user = User.create(email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD, username="test")
    roles = Role.list()
    logger.info(f"Roles = {roles!r}")
    admin_role = Role.get(name="admin")
    if admin_role not in user.roles:
        user.roles += [admin_role]
        user.save()
