"""Schema v1"""

#  Copyright© 2024. Stephen Rigden.
#  Last modified 9/19/24, 12:26 PM by stephen.
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

from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

VERSION = "DBv1"
MUYBRIDGE = 1878
MAX_YEAR = 10000


class Base(DeclarativeBase):
    pass


movie_tag_table = Table(
    "movie_tag_table",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

movie_star_table = Table(
    "movie_star_table",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("person_id", ForeignKey("person.id"), primary_key=True),
)

movie_director_table = Table(
    "movie_director_table",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id"), primary_key=True),
    Column("person_id", ForeignKey("person.id"), primary_key=True),
)


class Movie(Base):
    __tablename__ = "movie"
    __table_args__ = (
        UniqueConstraint("title", "year"),
        CheckConstraint(f"year>{MUYBRIDGE}"),
        CheckConstraint(f"year<={MAX_YEAR}"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    notes: Mapped[str | None]

    title: Mapped[str]
    year: Mapped[int]
    duration: Mapped[int | None]
    synopsis: Mapped[str | None]

    stars: Mapped[set["Person"]] = relationship(
        secondary=movie_star_table, back_populates="star_of_movies"
    )
    directors: Mapped[set["Person"]] = relationship(
        secondary=movie_director_table, back_populates="director_of_movies"
    )
    tags: Mapped[set["Tag"]] = relationship(
        secondary=movie_tag_table, back_populates="movies"
    )

    def __repr__(self) -> str:  # pragma nocover
        return (
            f"{self.__class__.__qualname__}("
            f"id={self.id!r}, "
            f"created={self.created!r}, "
            f"created={self.created!r}, "
            f"updated={self.updated!r}, "
            f"title={self.title!r}, "
            f"year={self.year!r}, "
            f"duration={self.duration!r}, "
            f"synopsis={self.synopsis!r}, "
            f"notes={self.notes!r}, "
            f"stars={self.stars!r}, "
            f"directors={self.directors!r}, "
            f"tags={self.tags!r}), "
        )


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    notes: Mapped[str | None]

    name: Mapped[str] = mapped_column(unique=True)

    director_of_movies: Mapped[set[Movie]] = relationship(
        secondary=movie_director_table, back_populates="directors"
    )
    star_of_movies: Mapped[set[Movie]] = relationship(
        secondary=movie_star_table, back_populates="stars"
    )

    def __repr__(self) -> str:  # pragma nocover
        return f"{self.__class__.__qualname__}(id={self.id!r}, name={self.name!r})"


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(default=func.now())
    updated: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    notes: Mapped[str | None]

    text: Mapped[str] = mapped_column(unique=True)

    movies: Mapped[set[Movie]] = relationship(
        secondary=movie_tag_table, back_populates="tags"
    )

    def __repr__(self) -> str:  # pragma nocover
        return f"{self.__class__.__qualname__}(id={self.id!r}, text={self.text!r})"
