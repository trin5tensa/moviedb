"""Database table functions."""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 7/9/24, 2:00 PM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sqlalchemy import select
from sqlalchemy.orm import Session

from database_src import schema


def _select_tag(session: Session, match: str) -> schema.Tag:
    """Selects a single tag.

    Args:
        session: The current session.
        match: Search text
    Returns:
        A tag.
    """
    statement = select(schema.Tag).where(schema.Tag.text.like(f"%{match}%"))
    return session.scalars(statement).one()


def _select_all_tags(session: Session) -> set[schema.Tag]:
    """Returns a list of every tag.

    Args:
        session:
    Returns:
        A set of tags.
    """
    statement = select(schema.Tag)
    return {tag for tag in session.scalars(statement).all()}


def _add_tags(session: Session, tag_texts: list[str]):
    """Adds new tags from a list of tag texts.

    Args:
        session:
        tag_texts:
    """
    session.add_all([schema.Tag(text=tag) for tag in tag_texts])


def _edit_tag(session: Session, old_tag_text: str, new_tag_text: str):
    """Edits the text of a tag.

    Args:
        session:
        old_tag_text:
        new_tag_text:
    """
    tag = _select_tag(session, old_tag_text)
    tag.text = new_tag_text


def _delete_tag(session: Session, tag_text: str):
    """Deletes a tag.

    Args:
        session:
        tag_text:
    """
    tag = _select_tag(session, tag_text)
    session.delete(tag)
