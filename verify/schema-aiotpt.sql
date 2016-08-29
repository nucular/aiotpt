-- Verify aiotpt:schema-aiotpt on pg

begin;

select pg_catalog.has_schema_privilege('aiotpt', 'usage');

rollback;
