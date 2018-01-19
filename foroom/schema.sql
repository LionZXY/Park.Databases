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
  id            BIGSERIAL PRIMARY KEY,
  slug          CITEXT NOT NULL UNIQUE,
  title         TEXT,
  userid        BIGINT REFERENCES "user" (id),
  posts_count   INT DEFAULT 0,
  threads_count INT DEFAULT 0
);

CREATE TABLE thread
(
  id         BIGSERIAL PRIMARY KEY,
  slug       CITEXT UNIQUE,
  created_on TIMESTAMP,
  message    TEXT,
  title      TEXT,
  authorid   BIGINT REFERENCES "user" (id),
  forumid    BIGINT REFERENCES forum (id),
  voice      INT DEFAULT 0
);

CREATE TABLE message
(
  id         BIGSERIAL PRIMARY KEY,
  created_on TIMESTAMP,
  message    TEXT,
  isedited   BOOLEAN   DEFAULT FALSE,
  authorid   BIGINT REFERENCES "user" (id),
  parentid   BIGINT    DEFAULT 0,
  threadid   BIGINT REFERENCES thread (id),
  forumid    BIGINT REFERENCES forum (id),
  parenttree BIGINT [] DEFAULT NULL
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

CREATE TRIGGER trigger_create_tree
  BEFORE INSERT
  ON message
  FOR EACH ROW EXECUTE PROCEDURE create_parent_tree();

CREATE TABLE vote
(
  voice    INT CHECK (voice IN (1, -1)),
  usernick CITEXT REFERENCES "user" (nickname),
  threadid BIGINT REFERENCES thread (id),
  CONSTRAINT unique_vote UNIQUE (usernick, threadid)
);

CREATE TABLE userforum
(
    usernick CITEXT COLLATE ucs_basic NOT NULL,
    userid INT,
    forumid INT NOT NULL,
    CONSTRAINT userforum_forumid_pk PRIMARY KEY (forumid)
);

CREATE INDEX IF NOT EXISTS userforum_forumid_usernick_desc ON userforum(forumid, usernick ASC, userid);
CREATE INDEX IF NOT EXISTS userforum_forumid_usernick_desc ON userforum(forumid, usernick DESC, userid);

CREATE OR REPLACE FUNCTION increment_voice_in_thread()
  RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE thread
  SET voice = voice + NEW.voice
  WHERE id = NEW.threadid;
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION update_voice_in_thread()
  RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE thread
  SET voice = voice + (NEW.voice - OLD.voice)
  WHERE id = NEW.threadid;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_create_vote
  AFTER INSERT
  ON vote
  FOR EACH ROW
EXECUTE PROCEDURE increment_voice_in_thread();

CREATE TRIGGER trigger_update_vote
  AFTER UPDATE
  ON vote
  FOR EACH ROW
EXECUTE PROCEDURE update_voice_in_thread();

CREATE INDEX message_threadid_id_index
  ON public.message (threadid, id);
CREATE INDEX message_threadid_id_desc_index
  ON public.message (threadid, id DESC);
CREATE INDEX thread_forumid_created_on_index
  ON public.thread (forumid, created_on);
CREATE INDEX thread_forumid_created_on_desc_index
  ON public.thread (forumid, created_on DESC);
CREATE INDEX message_id_parenttree_index
  ON public.message (id, parenttree);
CREATE INDEX message_threadid_parenttree_desc_index
  ON public.message (threadid, parenttree DESC);
CREATE INDEX message_threadid_parenttree_index
  ON public.message (threadid, parenttree);

CREATE INDEX message_threadid_parenttree_id_index
  ON public.message (threadid, parenttree, id)
  WHERE parentid = 0;
CREATE INDEX message_threadid_parenttree_id_desc_index
  ON public.message (threadid, parenttree DESC, id)
  WHERE parentid = 0;

CREATE INDEX "messages_tree[1]_index"
  ON message (threadid, (parenttree [1]));