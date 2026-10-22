"""Administrative provisioning only. Never mount these credentials in application services."""

import os

import psycopg
from psycopg import sql

OWNERS = {
    "identity": ("ms_identity", "svc_identity"),
    "knowledge": ("ms_knowledge", "svc_knowledge"),
    "conversation": ("ms_conversation", "svc_conversation"),
}


def provision(conn, passwords):
    conn.execute("SELECT pg_advisory_xact_lock(hashtext('secure-doc-service-roles'))")
    conn.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    database = conn.execute("SELECT current_database()").fetchone()[0]
    conn.execute(
        sql.SQL("REVOKE CREATE ON DATABASE {} FROM PUBLIC").format(
            sql.Identifier(database)
        )
    )
    for service, (schema, role) in OWNERS.items():
        password = passwords[service]
        if len(password) < 16:
            raise ValueError(
                f"{service} database password must be at least 16 characters"
            )
        if not conn.execute(
            "SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)
        ).fetchone():
            conn.execute(
                sql.SQL(
                    "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS"
                ).format(sql.Identifier(role))
            )
        conn.execute(
            sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                sql.Identifier(role), sql.Literal(password)
            )
        )
        conn.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {} AUTHORIZATION {}").format(
                sql.Identifier(schema), sql.Identifier(role)
            )
        )
        conn.execute(
            sql.SQL("REVOKE ALL ON SCHEMA {} FROM PUBLIC").format(
                sql.Identifier(schema)
            )
        )
        conn.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(database), sql.Identifier(role)
            )
        )


if __name__ == "__main__":
    with psycopg.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "secure_doc_agent"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    ) as conn:
        provision(
            conn,
            {
                service: os.environ[service.upper() + "_DB_PASSWORD"]
                for service in OWNERS
            },
        )
    print("Service roles and private schemas are ready.")
