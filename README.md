# marvel_universe
```
wget https://frontiernerds.com/files/state_of_the_union.txt

https://github.com/pgvector/pgvector
README
git clone https://github.com/pgvector/pgvector.git
sudo make install

sudo -u postgres psql
CREATE EXTENSION vector;
CREATE TABLE documents (id bigserial PRIMARY KEY, content TEXT, embedding vector(1536));

create database vectordb;
create user marvel_user with encrypted password 'password#1';
grant all privileges on database vectordb to marvel_user;
grant all privileges on table documents to marvel_user;
GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO marvel_user;

\c vectordb



sudo -u postgres psql
\c vectordb
CREATE EXTENSION vector;
CREATE TABLE documents (id bigserial PRIMARY KEY, content TEXT, embedding vector(1536));


alter table documents alter column embedding type vector(384);

show users:
\du 
psql -h localhost -d vectordb -U marvel_user
password#1

```
