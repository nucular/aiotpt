-- Revert aiotpt:create-schema-aiotpt from pg

begin;

drop schema aiotpt cascade;

commit;
