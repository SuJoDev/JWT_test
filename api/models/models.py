from sqlalchemy import ForeignKey, JSON, Index, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TIME, TIMESTAMP, BYTEA
from sqlalchemy.ext.declarative import declarative_base

from datetime import date, time, datetime

import pytz


class Base(DeclarativeBase):
    pass

class IdMix:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class UsersModel(IdMix, Base):
    __tablename__ = "Users"
    
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    date_joined: Mapped[date] = mapped_column()
    is_subscribed: Mapped[bool] = mapped_column(Boolean)
    last_login: Mapped[time] = mapped_column(TIME(timezone=True))
    
class MoodsModel(IdMix, Base):
    __tablename__ = "Moods"

    name: Mapped[str] = mapped_column()
    
class GenreModel(IdMix, Base):
    __tablename__ = "Genres"

    name: Mapped[str] = mapped_column()
    
class AlbumsModel(IdMix, Base):
    __tablename__ = "Albums"

    title: Mapped[str] = mapped_column()
    release_date: Mapped[date] = mapped_column()
    photo: Mapped[bytes] = mapped_column(BYTEA)
    artist_id: Mapped[int] = mapped_column(ForeignKey("Artists.id"))
    
    albums: Mapped[list["AlbumsModel"]] = relationship(
        "AlbumsModel",
        back_populates="artist",
        cascade="all, delete-orphan"
    )
    
class ArtistsModel(IdMix, Base):
    __tablename__ = "Artists"

    name: Mapped[str] = mapped_column()
    bio: Mapped[str] = mapped_column()
    photo: Mapped[bytes] = mapped_column(BYTEA)
    
    artist: Mapped["ArtistsModel"] = relationship(
        "ArtistsModel",
        back_populates="albums"
    )
    
class LanguagesModel(IdMix, Base):
    __tablename__ = "Languages"
    
    name: Mapped[str] = mapped_column()
    
class TracksModel(IdMix, Base):
    __tablename__ = "Tracks"
    
    title: Mapped[str] = mapped_column()
    duraction: Mapped[str] = mapped_column()
    file: Mapped[bytes] = mapped_column(BYTEA)
    play_count: Mapped[int] = mapped_column()
    album_id: Mapped[int] = mapped_column(ForeignKey("Albums.id"))
    artist_id: Mapped[int] = mapped_column(ForeignKey("Artists.id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("Genres.id"))
    language_id: Mapped[int] = mapped_column(ForeignKey("Languages.id"))
    mood_id: Mapped[int] = mapped_column(ForeignKey("Moods.id"))
    
class ListeningHistoryModel(IdMix, Base):
    __tablename__ = "ListeningHistory"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    track_id: Mapped[int] = mapped_column(ForeignKey("Tracks.id"))
    listening_date: Mapped[date] = mapped_column()
    play_duraction: Mapped[int] = mapped_column()
    to_listened: Mapped[bool] = mapped_column(Boolean)
    
class PlaylistsModel(IdMix, Base):
    __tablename__ = "Playlists"
    
    author_id = Mapped[int] = mapped_column(ForeignKey("Artists.id"))
    is_publick = Mapped[bool] = mapped_column(Boolean)
    title = Mapped[str] = mapped_column()
    
class PlaylistTracks(IdMix, Base):
    __tablename__ = "PlaylistTracks"
    
    playlist_id = Mapped[int] = mapped_column(ForeignKey("Playlists.id"))
    track_id = Mapped[int] = mapped_column(ForeignKey("Tracks.id"))
    
class PrefareTrakcsModel(IdMix, Base):
    __tablename__ = "PrefareTrakcs"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    track_id = Mapped[int] = mapped_column(ForeignKey("Tracks.id"))