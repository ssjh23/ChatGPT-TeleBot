/* Migration down file for the 000002_init_schema.up.sql file */
ALTER TABLE chatgpt_prompts RENAME TO prompts;