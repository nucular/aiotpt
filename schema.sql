create type UserElevation as enum (
  'none',
  'moderator',
  'administrator'
);

create type UserStatus as enum (
  'ok',
  'banned',
  'suspended'
);

create table Users (
  id serial
    primary key,
  name varchar(20)
    not null unique,
  passwordHash char(32)
    not null,
  email varchar(255)
    not null unique,
  dateRegistered timestamp
    not null,

  elevation UserElevation
    not null default 'none',
  status UserStatus
    not null default 'ok',
  unbanDate date,
  banReason text,

  location text,
  biography text,
  website text
);

create type SaveStatus as enum (
  'published',
  'unpublished',
  'deleted'
);

create table Saves (
  id serial
    primary key,
  userId serial
    not null references Users,
  name text
    not null,
  description text,
  dateCreated timestamp
    not null,
  dateChanged timestamp
    not null,
  status SaveStatus
    not null default 'published',

  saveData bytea
    not null,
  previewPng bytea
    not null,
  previewPngSmall bytea
    not null,
  previewPti bytea
    not null,
  previewPtiSmall bytea
    not null,

  score integer
    not null default 0,
  scoreUp integer
    not null default 0,
  scoreDown integer
    not null default 0,
  views integer
    not null default 0,
  host inet
    not null
);
create index Saves_userId on Saves(userId);
create index Saves_name on Saves(name);

create table FavouriteRefs (
  id serial
    primary key,
  userId serial
    not null references Users,
  saveId serial
    not null references Saves,
  unique(userId, saveId)
);
create index FavouriteRefs_userId on FavouriteRefs(userId);
create index FavouriteRefs_saveId on FavouriteRefs(saveId);

create table Sessions (
  userId serial
    not null references Users,
  sessionId char(30)
    not null unique,
  sessionKey char(10)
    not null,
  loginDate timestamp
    not null,
  host inet
    not null
);
create index Sessions_userId on Sessions(userId);

create type VoteDirection as Enum (
  'up',
  'down'
);

create table Votes (
  saveId serial
    not null references Saves,
  userId serial
    not null references Users,
  direction VoteDirection
    not null,
  date timestamp
    not null,
  host inet
    not null
);

create table Comments (
  id serial
    primary key,
  saveId serial
    not null references Saves,
  userId serial
    not null references Users,
  date timestamp
    not null,
  content text
    not null default '',
  host inet
    not null
);
create index Comments_saveId on Comments(saveId);
create index Comments_userId on Comments(userId);

create table Tags (
  id serial
    primary key,
  name text
    not null unique
);
create index Tags_name on Tags(name);

create table TagRefs (
  saveId serial
    not null references Saves,
  userId serial
    not null references Users,
  tagId serial
    not null references Tags,
  date timestamp
    not null,
  host inet
    not null,
  unique(saveId, tagId)
);
create index TagRefs_saveId on TagRefs(saveId);
create index TagRefs_tagId on TagRefs(tagId);
