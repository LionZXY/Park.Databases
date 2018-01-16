CREATE EXTENSION IF NOT EXISTS CITEXT;

CREATE TABLE "user"
(
  id       BIGSERIAL PRIMARY KEY,
  nickname CITEXT COLLATE ucs_basic NOT NULL UNIQUE,
  about    TEXT,
  email    CITEXT                   NOT NULL UNIQUE,
  fullname TEXT
);

CREATE TABLE forum
(
  id     BIGSERIAL PRIMARY KEY,
  slug   CITEXT NOT NULL UNIQUE,
  title  TEXT,
  userid BIGINT REFERENCES "user" (id)
);

CREATE TABLE thread
(
  id         BIGSERIAL PRIMARY KEY,
  slug       CITEXT UNIQUE,
  created_on TIMESTAMP,
  message    TEXT,
  title      TEXT,
  authorid   BIGINT REFERENCES "user" (id),
  forumid    BIGINT REFERENCES forum (id)
);

CREATE TABLE message
(
  id         BIGSERIAL PRIMARY KEY,
  created_on TIMESTAMP,
  message    TEXT,
  isedited   BOOLEAN DEFAULT FALSE,
  authorid   BIGINT REFERENCES "user" (id),
  parentid   BIGINT DEFAULT 0,
  threadid   BIGINT REFERENCES thread (id),
  forumid    BIGINT REFERENCES forum (id),
  parenttree BIGINT []                      DEFAULT NULL
);

CREATE OR REPLACE FUNCTION create_parent_tree()
  RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE treepath BIGINT [];
BEGIN
  IF (NEW.parentid = 0)
  THEN
    NEW.parenttree = treepath || NEW.id :: BIGINT;
    RETURN NEW;
  END IF;

  treepath = (SELECT parenttree
              FROM "message"
              WHERE id = NEW.parentid AND threadid = NEW.threadid);

  IF (cardinality(treepath) > 0)
  THEN
    treepath = treepath || NEW.id;
    NEW.parenttree = treepath || NEW.id :: BIGINT;
    RETURN NEW;
  END IF;

  RAISE invalid_foreign_key;
END;
$$;

CREATE TRIGGER trigger_create_tree BEFORE INSERT ON message FOR EACH ROW EXECUTE PROCEDURE create_parent_tree();

CREATE TABLE vote
(
  voice    INT CHECK (voice IN (1, -1)),
  userid   BIGINT REFERENCES "user" (id),
  threadid BIGINT REFERENCES thread (id),
  CONSTRAINT unique_vote UNIQUE (userid, threadid)
);
