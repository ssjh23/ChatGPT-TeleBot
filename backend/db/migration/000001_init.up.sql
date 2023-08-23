CREATE TABLE "users" (
  "id" bigserial PRIMARY KEY,
  "chat_id" varchar NOT NULL,
  "password" varchar NOT NULL,
  "user_prompts" varchar[]
);

CREATE INDEX ON "users" ("chat_id");



