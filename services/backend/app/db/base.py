# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.chat import Chat
from app.models.chat_room import ChatRoom
from app.models.user import User