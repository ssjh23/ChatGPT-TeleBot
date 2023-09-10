CREATE TABLE "users" (
  "id" bigserial PRIMARY KEY,
  "chat_id" varchar NOT NULL UNIQUE,
  "password" varchar NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "password_updated_at" timestamp NOT NULL DEFAULT (now())
);

/* Create a table stores all string prompts with a UUID primary key, the user as a FK */   
CREATE TABLE "prompts" (
  "id" bigserial PRIMARY KEY,
  "prompt" varchar NOT NULL,
  "user_id" bigint NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

CREATE INDEX ON "users" ("chat_id");
