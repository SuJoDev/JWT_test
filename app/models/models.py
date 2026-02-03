from sqlalchemy import ForeignKey, JSON, Index, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TIME, TIMESTAMP, BYTEA, DATE, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from datetime import datetime, date
from sqlalchemy.dialects.postgresql import TIMESTAMP

import pytz


class Base(DeclarativeBase):
    pass

class IdMix:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class ArtistsModel(IdMix, Base):
    __tablename__ = "artists"

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(TEXT)
    country: Mapped[str] = mapped_column()
    # created_at: Mapped[datetime] = mapped_column(
    #     TIMESTAMP(timezone=True),
    #     default=lambda: datetime.now(pytz.UTC)
    # )
    
    track: Mapped[list["TracksModel"]] = relationship("TracksModel", back_populates="artist")
    
class AlbomsModel(IdMix, Base):
    __tablename__ = "albums"

    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    title: Mapped[str] = mapped_column()
    release_date: Mapped[date] = mapped_column(DATE())
    cover_url: Mapped[str] = mapped_column()
    
class TracksModel(IdMix, Base):
    __tablename__ = "tracks"
    
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"))
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    title: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column()
    file_url: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now()
    )
    
    artist: Mapped["ArtistsModel"] = relationship("ArtistsModel", back_populates="track")
    
class UsersModel(IdMix, Base):
    __tablename__ = "users"
    
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(pytz.UTC)
    )
    last_login: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now()
    )
    
class PlaylistsModels(IdMix, Base):
    __tablename__ = "playlists"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default= func.now()
    )
    
class FavoritiesTracks(Base):
    __tablename__ = "favorites"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default= func.now()
    )
    
class ListeningHistoryModel(IdMix, Base):
    __tablename__ = "listening_history"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    played_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default= func.now()
    )
    play_duraction: Mapped[int] = mapped_column()
    
# class TrackModels(IdMix, Base):
#     __tablename__ = "tracks"
    
#     album_id: Mapped[int] = mapped_column(ForeignKey("albums.id"))
#     artists_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
#     title: Mapped[str] = mapped_column()
#     duraction: Mapped[int] = mapped_column()
#     file_url: Mapped[str] = mapped_column(TEXT)
#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True),
#         default= func.now()
#     )

# class UsersModel(IdMix, Base):
#     __tablename__ = "Users"
    
#     username: Mapped[str] = mapped_column(unique=True)
#     password: Mapped[str] = mapped_column()
#     email: Mapped[str] = mapped_column()
#     date_joined: Mapped[date] = mapped_column()
#     is_subscribed: Mapped[bool] = mapped_column(Boolean)
#     last_login: Mapped[time] = mapped_column(TIME(timezone=True))
    
# class MoodsModel(IdMix, Base):
#     __tablename__ = "Moods"

#     name: Mapped[str] = mapped_column()
    
# class GenreModel(IdMix, Base):
#     __tablename__ = "Genres"

#     name: Mapped[str] = mapped_column()
    
# class AlbumsModel(IdMix, Base):
#     __tablename__ = "Albums"

#     title: Mapped[str] = mapped_column()
#     release_date: Mapped[date] = mapped_column()
#     photo: Mapped[bytes] = mapped_column(BYTEA)
#     artist_id: Mapped[int] = mapped_column(ForeignKey("Artists.id"))
    
#     albums: Mapped[list["AlbumsModel"]] = relationship(
#         "AlbumsModel",
#         back_populates="artist",
#         cascade="all, delete-orphan"
#     )
    
# class ArtistsModel(IdMix, Base):
#     __tablename__ = "Artists"

#     name: Mapped[str] = mapped_column()
#     bio: Mapped[str] = mapped_column()
#     photo: Mapped[bytes] = mapped_column(BYTEA)
    
#     artist: Mapped["ArtistsModel"] = relationship(
#         "ArtistsModel",
#         back_populates="albums"
#     )
    
# class LanguagesModel(IdMix, Base):
#     __tablename__ = "Languages"
    
#     name: Mapped[str] = mapped_column()
    
# class TracksModel(IdMix, Base):
#     __tablename__ = "Tracks"
    
#     title: Mapped[str] = mapped_column()
#     duraction: Mapped[str] = mapped_column()
#     file: Mapped[bytes] = mapped_column(BYTEA)
#     play_count: Mapped[int] = mapped_column()
#     album_id: Mapped[int] = mapped_column(ForeignKey("Albums.id"))
#     artist_id: Mapped[int] = mapped_column(ForeignKey("Artists.id"))
#     genre_id: Mapped[int] = mapped_column(ForeignKey("Genres.id"))
#     language_id: Mapped[int] = mapped_column(ForeignKey("Languages.id"))
#     mood_id: Mapped[int] = mapped_column(ForeignKey("Moods.id"))
    
# class ListeningHistoryModel(IdMix, Base):
#     __tablename__ = "ListeningHistory"
    
#     user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
#     track_id: Mapped[int] = mapped_column(ForeignKey("Tracks.id"))
#     listening_date: Mapped[date] = mapped_column()
#     play_duraction: Mapped[int] = mapped_column()
#     to_listened: Mapped[bool] = mapped_column(Boolean)
    
# # class PlaylistsModel(IdMix, Base):
# #     __tablename__ = "Playlists"
    
# #     author_id = Mapped[int] = mapped_column(ForeignKey("Artists.id"))
# #     is_publick = Mapped[bool] = mapped_column(Boolean)
# #     title = Mapped[str] = mapped_column()
    
# # class PlaylistTracks(IdMix, Base):
# #     __tablename__ = "PlaylistTracks"
    
# #     playlist_id = Mapped[int] = mapped_column(ForeignKey("Playlists.id"))
# #     track_id = Mapped[int] = mapped_column(ForeignKey("Tracks.id"))
    
# # class PrefareTrakcsModel(IdMix, Base):
# #     __tablename__ = "PrefareTrakcs"
    
# #     user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
# #     track_id = Mapped[int] = mapped_column(ForeignKey("Tracks.id"))