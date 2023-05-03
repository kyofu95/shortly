"""
This module contains special pydantic magic to painlessly avoid circular references.
"""

from .user import UserInDB, UserOut
from .link import LinkInDB, LinkOut

# Update the references that are as strings
UserInDB.update_forward_refs(LinkInDB=LinkInDB)
UserOut.update_forward_refs(LinkOut=LinkOut)
LinkInDB.update_forward_refs(UserInDB=UserInDB)
