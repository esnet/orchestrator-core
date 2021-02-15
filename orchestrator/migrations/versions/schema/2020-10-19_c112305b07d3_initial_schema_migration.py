"""Initial schema migration.

Revision ID: c112305b07d3
Revises:
Create Date: 2020-10-19 08:48:12.231037

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import postgresql

from orchestrator import db

# revision identifiers, used by Alembic.
revision = "c112305b07d3"
down_revision = None
branch_labels = ("schema",)
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public')

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "engine_settings",
        sa.Column("global_lock", sa.Boolean(), nullable=False),
        sa.Column("running_processes", sa.Integer(), nullable=False),
        sa.CheckConstraint("running_processes >= 0", name="check_running_processes_positive"),
        sa.PrimaryKeyConstraint("global_lock"),
    )
    op.create_table(
        "processes",
        sa.Column(
            "pid", sqlalchemy_utils.types.uuid.UUIDType(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("workflow", sa.String(length=255), nullable=False),
        sa.Column("assignee", sa.String(length=50), server_default="SYSTEM", nullable=False),
        sa.Column("last_status", sa.String(length=50), nullable=False),
        sa.Column("last_step", sa.String(length=255), nullable=True),
        sa.Column(
            "started_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.Column(
            "last_modified_at",
            db.UtcTimestamp(timezone=True),
            server_default=sa.text("current_timestamp"),
            nullable=False,
        ),
        sa.Column("failed_reason", sa.Text(), nullable=True),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("is_task", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.PrimaryKeyConstraint("pid"),
    )
    op.create_index(op.f("ix_processes_is_task"), "processes", ["is_task"], unique=False)
    op.create_index(op.f("ix_processes_pid"), "processes", ["pid"], unique=False)
    op.create_table(
        "product_blocks",
        sa.Column(
            "product_block_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("tag", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.Column("end_date", db.UtcTimestamp(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("product_block_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "products",
        sa.Column(
            "product_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("product_type", sa.String(length=255), nullable=False),
        sa.Column("tag", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.Column("end_date", db.UtcTimestamp(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("product_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_products_tag"), "products", ["tag"], unique=False)
    op.create_table(
        "resource_types",
        sa.Column(
            "resource_type_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("resource_type", sa.String(length=510), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("resource_type_id"),
        sa.UniqueConstraint("resource_type"),
    )
    op.create_table(
        "workflows",
        sa.Column(
            "workflow_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.PrimaryKeyConstraint("workflow_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "fixed_inputs",
        sa.Column(
            "fixed_input_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.Column("product_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("fixed_input_id"),
        sa.UniqueConstraint("name", "product_id"),
    )
    op.create_table(
        "process_steps",
        sa.Column(
            "stepid",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("pid", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column(
            "executed_at",
            db.UtcTimestamp(timezone=True),
            server_default=sa.text("statement_timestamp()"),
            nullable=False,
        ),
        sa.Column("commit_hash", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["pid"], ["processes.pid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("stepid"),
    )
    op.create_index(op.f("ix_process_steps_pid"), "process_steps", ["pid"], unique=False)
    op.create_table(
        "product_block_resource_types",
        sa.Column("product_block_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("resource_type_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(["product_block_id"], ["product_blocks.product_block_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resource_type_id"], ["resource_types.resource_type_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_block_id", "resource_type_id"),
    )
    op.create_table(
        "product_product_blocks",
        sa.Column("product_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("product_block_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(["product_block_id"], ["product_blocks.product_block_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "product_block_id"),
    )
    op.create_table(
        "products_workflows",
        sa.Column("product_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("workflow_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.workflow_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "workflow_id"),
    )
    op.create_table(
        "subscriptions",
        sa.Column(
            "subscription_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column("product_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("customer_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("insync", sa.Boolean(), nullable=False),
        sa.Column("start_date", db.UtcTimestamp(timezone=True), nullable=True),
        sa.Column("end_date", db.UtcTimestamp(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tsv", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.product_id"]),
        sa.PrimaryKeyConstraint("subscription_id"),
    )
    op.create_index(op.f("ix_subscriptions_customer_id"), "subscriptions", ["customer_id"], unique=False)
    op.create_index(op.f("ix_subscriptions_product_id"), "subscriptions", ["product_id"], unique=False)
    op.create_index(op.f("ix_subscriptions_status"), "subscriptions", ["status"], unique=False)
    op.create_index("subscription_customer_ix", "subscriptions", ["subscription_id", "customer_id"], unique=False)
    op.create_index("subscription_product_ix", "subscriptions", ["subscription_id", "product_id"], unique=False)
    op.create_index("subscription_tsv_ix", "subscriptions", ["tsv"], unique=False, postgresql_using="gin")
    op.create_table(
        "processes_subscriptions",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("pid", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("subscription_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "created_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.Column("workflow_target", sa.String(length=255), server_default="CREATE", nullable=False),
        sa.ForeignKeyConstraint(["pid"], ["processes.pid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.subscription_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_processes_subscriptions_pid"), "processes_subscriptions", ["pid"], unique=False)
    op.create_index(
        op.f("ix_processes_subscriptions_subscription_id"), "processes_subscriptions", ["subscription_id"], unique=False
    )
    op.create_index("processes_subscriptions_ix", "processes_subscriptions", ["pid", "subscription_id"], unique=False)
    op.create_table(
        "subscription_customer_descriptions",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("subscription_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("customer_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at", db.UtcTimestamp(timezone=True), server_default=sa.text("current_timestamp"), nullable=False
        ),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.subscription_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "subscription_id", name="uniq_customer_subscription_description"),
    )
    op.create_index(
        op.f("ix_subscription_customer_descriptions_customer_id"),
        "subscription_customer_descriptions",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_customer_descriptions_subscription_id"),
        "subscription_customer_descriptions",
        ["subscription_id"],
        unique=False,
    )
    op.create_table(
        "subscription_instances",
        sa.Column(
            "subscription_instance_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("subscription_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("product_block_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["product_block_id"], ["product_blocks.product_block_id"]),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.subscription_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("subscription_instance_id"),
    )
    op.create_index(
        op.f("ix_subscription_instances_product_block_id"), "subscription_instances", ["product_block_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscription_instances_subscription_id"), "subscription_instances", ["subscription_id"], unique=False
    )
    op.create_index(
        "subscription_instance_s_pb_ix",
        "subscription_instances",
        ["subscription_instance_id", "subscription_id", "product_block_id"],
        unique=False,
    )
    op.create_table(
        "subscription_instance_relations",
        sa.Column("parent_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("child_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("domain_model_attr", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["child_id"], ["subscription_instances.subscription_instance_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["subscription_instances.subscription_instance_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("parent_id", "child_id", "order_id"),
    )
    op.create_index(
        "subscription_relation_p_c_o_ix",
        "subscription_instance_relations",
        ["parent_id", "child_id", "order_id"],
        unique=True,
    )
    op.create_table(
        "subscription_instance_values",
        sa.Column(
            "subscription_instance_value_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("subscription_instance_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("resource_type_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["resource_type_id"], ["resource_types.resource_type_id"]),
        sa.ForeignKeyConstraint(
            ["subscription_instance_id"], ["subscription_instances.subscription_instance_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("subscription_instance_value_id"),
    )
    op.create_index(
        op.f("ix_subscription_instance_values_resource_type_id"),
        "subscription_instance_values",
        ["resource_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_instance_values_subscription_instance_id"),
        "subscription_instance_values",
        ["subscription_instance_id"],
        unique=False,
    )
    op.create_index(
        "siv_si_rt_ix",
        "subscription_instance_values",
        ["subscription_instance_value_id", "subscription_instance_id", "resource_type_id"],
        unique=False,
    )
    # ### end Alembic commands ###

    conn.execute(
        """
        CREATE TYPE public.tsq_state AS (
            search_query text,
            parentheses_stack integer,
            skip_for integer,
            current_token text,
            current_index integer,
            current_char text,
            previous_char text,
            tokens text[]
            )
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.array_nremove(anyarray, anyelement, integer) RETURNS anyarray
            LANGUAGE sql IMMUTABLE
            AS $_$
            WITH replaced_positions AS (
                SELECT UNNEST(
                    CASE
                    WHEN $2 IS NULL THEN
                        '{}'::int[]
                    WHEN $3 > 0 THEN
                        (array_positions($1, $2))[1:$3]
                    WHEN $3 < 0 THEN
                        (array_positions($1, $2))[
                            (cardinality(array_positions($1, $2)) + $3 + 1):
                        ]
                    ELSE
                        '{}'::int[]
                    END
                ) AS position
            )
            SELECT COALESCE((
                SELECT array_agg(value)
                FROM unnest($1) WITH ORDINALITY AS t(value, index)
                WHERE index NOT IN (SELECT position FROM replaced_positions)
            ), $1[1:0]);
        $_$;
        """
    )
    conn.execute(
        """
        CREATE FUNCTION public.fixed_inputs_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            UPDATE subscriptions SET tsv = NULL WHERE product_id = NEW.product_id;
            RETURN NEW;
        END
        $$;
        """
    )
    conn.execute(
        """
        CREATE FUNCTION public.generate_subscription_tsv(sub_id uuid) RETURNS tsvector
            LANGUAGE plpgsql
            AS $$
        DECLARE
            gen_tsv TSVECTOR := NULL;
        BEGIN
            /*
             To generate a `tsvector` we first need to construct a `text` 'document' with
             meaningful data. That document is then fed into the `to_tsvector`
             function. That 'document' in our case boils down to all relevant data of a
             subscription. Because of our data model this requires a fair amount of
             joins. To make the data gathering step somewhat easier to follow we've
             split up the gathering of:

             - resource type data
             - subscription and product data
             - fixed input data
             - subscription customer description data

             into three separate queries using a Common Table Expression (CTE or WITH
             query). These three queries can be referenced to as tables, namely as
             tables:

             - rt_info
             - sub_prod_info
             - fi_info
             - cust_info

             The final query concatenates the corresponding rows of these three tables
             into a single document to be fed to `to_tsvector`.

             One thing of note is the usage of LEFT JOINs in the last query. This is
             for subscriptions that have been just created. Eg those that are 'initial'
             and as such might not yet have any resource types. A regular JOIN would
             not produce a result in that case leaving use with no document to feed
             into the `to_tsvector` function to populate the `tsv` column. Using a LEFT
             JOIN, together with `coalesce` to turn NULL values into empty strings
             (ensuring `concat_ws` does not return NULL), we will always get a
             meaningful value.
            */
            WITH rt_info AS (
                SELECT s.subscription_id,
                       string_agg(rt.resource_type || ': ' || siv.value, ', ' ORDER BY rt.resource_type) AS rt_info
                FROM subscription_instance_values siv
                         JOIN resource_types rt ON siv.resource_type_id = rt.resource_type_id
                         JOIN subscription_instances si ON siv.subscription_instance_id = si.subscription_instance_id
                         JOIN subscriptions s ON si.subscription_id = s.subscription_id
                GROUP BY s.subscription_id),
                 sub_prod_info AS (
                     SELECT s.subscription_id,
                            array_to_string(
                                    ARRAY ['subscription_id: ' || s.subscription_id,
                                        'status: ' || s.status,
                                        'insync: ' || s.insync,
                                        'subscription_description: ' || s.description,
                                        'note: ' || coalesce(s.note, ''),
                                        'customer_id: ' || s.customer_id,
                                        'product_id: ' || s.product_id],
                                    ', ') AS sub_info,
                            array_to_string(
                                    ARRAY ['product_name: ' || p.name,
                                        'product_description: ' || p.description,
                                        'tag: ' || p.tag,
                                        'product_type: ', p.product_type],
                                    ', ') AS prod_info
                     FROM subscriptions s
                              JOIN products p ON s.product_id = p.product_id),
                 fi_info AS (
                     SELECT s.subscription_id,
                            string_agg(fi.name || ': ' || fi.value, ', ' ORDER BY fi.name) AS fi_info
                     FROM subscriptions s
                              JOIN products p ON s.product_id = p.product_id
                              JOIN fixed_inputs fi ON p.product_id = fi.product_id
                     GROUP BY s.subscription_id),
                 cust_info AS (
                     SELECT s.subscription_id,
                            string_agg('customer_description: ' || scd.description, ', ') AS cust_info
                     FROM subscriptions s
                              JOIN subscription_customer_descriptions scd ON s.subscription_id = scd.subscription_id
                     GROUP BY s.subscription_id
                 )
            SELECT to_tsvector('english',
                           concat_ws(', ',
                                     coalesce(spi.sub_info, ''),
                                     coalesce(spi.prod_info, ''),
                                     coalesce(fi.fi_info, ''),
                                     coalesce(rti.rt_info, ''),
                                     coalesce(ci.cust_info, '')
                               ))
            INTO STRICT gen_tsv
            FROM subscriptions s
                     LEFT JOIN sub_prod_info spi ON s.subscription_id = spi.subscription_id
                     LEFT JOIN fi_info fi ON s.subscription_id = fi.subscription_id
                     LEFT JOIN rt_info rti ON s.subscription_id = rti.subscription_id
                     LEFT JOIN cust_info ci ON s.subscription_id = ci.subscription_id
            WHERE s.subscription_id = sub_id;
            RETURN gen_tsv;
        END
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.products_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            UPDATE subscriptions SET tsv = NULL WHERE product_id = NEW.product_id;
            RETURN NEW;
        END
        $$;
        """
    )
    conn.execute(
        """
        CREATE FUNCTION public.subscription_customer_descriptions_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            UPDATE subscriptions SET tsv = NULL WHERE subscription_id = NEW.subscription_id;
            RETURN NEW;
        END
        $$;
        """
    )
    conn.execute(
        sa.text(
            """
        CREATE FUNCTION public.subscription_instance_values_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        DECLARE
            sub_id subscriptions.subscription_id%TYPE;
        BEGIN
            SELECT si.subscription_id
            INTO STRICT sub_id
            FROM subscription_instances si
            WHERE si.subscription_instance_id = NEW.subscription_instance_id;
            UPDATE subscriptions SET tsv = NULL WHERE subscription_id = sub_id;
            RETURN NEW;
        END
        $$;
        """
        )
    )

    conn.execute(
        """
        CREATE FUNCTION public.subscriptions_ins_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            /*
             We have a separate insert trigger for subscriptions for the simple reason
             that while we are processing the insert there is not yet a row, with the
             just generated NEW.subscription_id, in the database to join with. Hence
             this trigger will only use the values from the insert.
             */
            SELECT to_tsvector('english',
                           concat_ws(', ',
                                     array_to_string(
                                             ARRAY ['subscription_id: ' || NEW.subscription_id,
                                                 'status: ' || NEW.status,
                                                 'insync: ' || NEW.insync,
                                                 'subscription_description: ' || NEW.description,
                                                 'note: ' || coalesce(NEW.note, ''),
                                                 'customer_id: ' || NEW.customer_id,
                                                 'product_id: ' || NEW.product_id],
                                             ', '),
                                     array_to_string(
                                             ARRAY ['product_name: ' || p.name,
                                                 'product_description: ' || p.description,
                                                 'tag: ' || p.tag,
                                                 'product_type: ', p.product_type],
                                             ', ')))
            INTO STRICT NEW.tsv
            FROM products p
            WHERE p.product_id = NEW.product_id;
            RETURN NEW;
        END
        $$;
        """
    )

    conn.execute(
        """

        CREATE FUNCTION public.subscriptions_upd_trigger() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        DECLARE
            upd_tsv TSVECTOR := NULL;
        BEGIN
            upd_tsv := generate_subscription_tsv(NEW.subscription_id);
            UPDATE subscriptions
            SET tsv = upd_tsv
            WHERE subscription_id = NEW.subscription_id
            AND tsv IS DISTINCT FROM upd_tsv;
            RETURN NULL;
        END
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_append_current_token(state public.tsq_state) RETURNS public.tsq_state
            LANGUAGE plpgsql IMMUTABLE
            AS $$
        BEGIN
            IF state.current_token != '' THEN
                state.tokens := array_append(state.tokens, state.current_token);
                state.current_token := '';
            END IF;
            RETURN state;
        END;
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_process_tokens(config regconfig, tokens text[]) RETURNS tsquery
            LANGUAGE plpgsql IMMUTABLE
            AS $$
        DECLARE
            result_query text;
            previous_value text;
            value text;
        BEGIN
            result_query := '';

            FOREACH value IN ARRAY tokens LOOP
                IF value = '"' THEN
                    CONTINUE;
                END IF;

                IF value = 'or' THEN
                    value := ' | ';
                END IF;

                IF left(value, 1) = '"' AND right(value, 1) = '"' THEN
                    value := phraseto_tsquery(config, value);
                ELSIF value NOT IN ('(', ' | ', ')', '-') THEN
                    value := quote_literal(value) || ':*';
                END IF;

                IF previous_value = '-' THEN
                    IF value = '(' THEN
                        value := '!' || value;
                    ELSIF value = ' | ' THEN
                        CONTINUE;
                    ELSE
                        value := '!(' || value || ')';
                    END IF;
                END IF;

                SELECT
                    CASE
                        WHEN result_query = '' THEN value
                        WHEN previous_value = ' | ' AND value = ' | ' THEN result_query
                        WHEN previous_value = ' | ' THEN result_query || ' | ' || value
                        WHEN previous_value IN ('!(', '(') OR value = ')' THEN result_query || value
                        WHEN value != ' | ' THEN result_query || ' & ' || value
                        ELSE result_query
                    END
                INTO result_query;
                previous_value := value;
            END LOOP;

            IF result_query = ' | ' THEN
                RETURN to_tsquery('');
            END IF;

            RETURN to_tsquery(config, result_query);
        END;
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_tokenize(search_query text) RETURNS text[]
            LANGUAGE plpgsql IMMUTABLE
            AS $$
        DECLARE
            state tsq_state;
        BEGIN
            SELECT
                search_query::text AS search_query,
                0::int AS parentheses_stack,
                0 AS skip_for,
                ''::text AS current_token,
                0 AS current_index,
                ''::text AS current_char,
                ''::text AS previous_char,
                '{}'::text[] AS tokens
            INTO state;

            state.search_query := lower(trim(
                regexp_replace(search_query, '""+', '""', 'g')
            ));

            FOR state.current_index IN (
                SELECT generate_series(1, length(state.search_query))
            ) LOOP
                state.current_char := substring(
                    search_query FROM state.current_index FOR 1
                );

                IF state.skip_for > 0 THEN
                    state.skip_for := state.skip_for - 1;
                    CONTINUE;
                END IF;

                state := tsq_tokenize_character(state);
                state.previous_char := state.current_char;
            END LOOP;
            state := tsq_append_current_token(state);

            state.tokens := array_nremove(state.tokens, '(', -state.parentheses_stack);

            RETURN state.tokens;
        END;
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_parse(config regconfig, search_query text) RETURNS tsquery
            LANGUAGE sql IMMUTABLE
            AS $$
            SELECT tsq_process_tokens(config, tsq_tokenize(search_query));
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_parse(config text, search_query text) RETURNS tsquery
            LANGUAGE sql IMMUTABLE
            AS $$
            SELECT tsq_parse(config::regconfig, search_query);
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_parse(search_query text) RETURNS tsquery
            LANGUAGE sql IMMUTABLE
            AS $$
            SELECT tsq_parse(get_current_ts_config(), search_query);
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_process_tokens(tokens text[]) RETURNS tsquery
            LANGUAGE sql IMMUTABLE
            AS $$
            SELECT tsq_process_tokens(get_current_ts_config(), tokens);
        $$;
        """
    )

    conn.execute(
        """
        CREATE FUNCTION public.tsq_tokenize_character(state public.tsq_state) RETURNS public.tsq_state
            LANGUAGE plpgsql IMMUTABLE
            AS $$
        BEGIN
            IF state.current_char = '(' THEN
                state.tokens := array_append(state.tokens, '(');
                state.parentheses_stack := state.parentheses_stack + 1;
                state := tsq_append_current_token(state);
            ELSIF state.current_char = ')' THEN
                IF (state.parentheses_stack > 0 AND state.current_token != '') THEN
                    state := tsq_append_current_token(state);
                    state.tokens := array_append(state.tokens, ')');
                    state.parentheses_stack := state.parentheses_stack - 1;
                END IF;
            ELSIF state.current_char = '"' THEN
                state.skip_for := position('"' IN substring(
                    state.search_query FROM state.current_index + 1
                ));

                IF state.skip_for > 1 THEN
                    state.tokens = array_append(
                        state.tokens,
                        substring(
                            state.search_query
                            FROM state.current_index FOR state.skip_for + 1
                        )
                    );
                ELSIF state.skip_for = 0 THEN
                    state.current_token := state.current_token || state.current_char;
                END IF;
            ELSIF (
                state.current_char = '-' AND
                (state.current_index = 1 OR state.previous_char = ' ')
            ) THEN
                state.tokens := array_append(state.tokens, '-');
            ELSIF state.current_char = ' ' THEN
                state := tsq_append_current_token(state);
            ELSE
                state.current_token = state.current_token || state.current_char;
            END IF;
            RETURN state;
        END;
        $$;
        """
    )

    conn.execute(
        "CREATE TRIGGER fixed_inputs_trigger AFTER INSERT OR UPDATE ON public.fixed_inputs FOR EACH ROW EXECUTE FUNCTION public.fixed_inputs_trigger()"
    )
    conn.execute(
        "CREATE TRIGGER products_trigger AFTER INSERT OR UPDATE ON public.products FOR EACH ROW EXECUTE FUNCTION public.products_trigger()"
    )
    conn.execute(
        "CREATE TRIGGER subscription_customer_descriptions_trigger AFTER INSERT OR UPDATE ON public.subscription_customer_descriptions FOR EACH ROW EXECUTE FUNCTION public.subscription_customer_descriptions_trigger()"
    )
    conn.execute(
        "CREATE TRIGGER subscription_instance_values_trigger AFTER INSERT OR UPDATE ON public.subscription_instance_values FOR EACH ROW EXECUTE FUNCTION public.subscription_instance_values_trigger()"
    )
    conn.execute(
        "CREATE TRIGGER subscriptions_ins_trigger BEFORE INSERT ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION public.subscriptions_ins_trigger()"
    )
    conn.execute(
        "CREATE TRIGGER subscriptions_upd_trigger AFTER UPDATE ON public.subscriptions FOR EACH ROW WHEN ((NOT (old.tsv IS DISTINCT FROM new.tsv))) EXECUTE FUNCTION public.subscriptions_upd_trigger()"
    )

    conn.execute("INSERT INTO public.engine_settings VALUES (false, 0)")


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("siv_si_rt_ix", table_name="subscription_instance_values")
    op.drop_index(
        op.f("ix_subscription_instance_values_subscription_instance_id"), table_name="subscription_instance_values"
    )
    op.drop_index(op.f("ix_subscription_instance_values_resource_type_id"), table_name="subscription_instance_values")
    op.drop_table("subscription_instance_values")
    op.drop_index("subscription_relation_p_c_o_ix", table_name="subscription_instance_relations")
    op.drop_table("subscription_instance_relations")
    op.drop_index("subscription_instance_s_pb_ix", table_name="subscription_instances")
    op.drop_index(op.f("ix_subscription_instances_subscription_id"), table_name="subscription_instances")
    op.drop_index(op.f("ix_subscription_instances_product_block_id"), table_name="subscription_instances")
    op.drop_table("subscription_instances")
    op.drop_index(
        op.f("ix_subscription_customer_descriptions_subscription_id"), table_name="subscription_customer_descriptions"
    )
    op.drop_index(
        op.f("ix_subscription_customer_descriptions_customer_id"), table_name="subscription_customer_descriptions"
    )
    op.drop_table("subscription_customer_descriptions")
    op.drop_index("processes_subscriptions_ix", table_name="processes_subscriptions")
    op.drop_index(op.f("ix_processes_subscriptions_subscription_id"), table_name="processes_subscriptions")
    op.drop_index(op.f("ix_processes_subscriptions_pid"), table_name="processes_subscriptions")
    op.drop_table("processes_subscriptions")
    op.drop_index("subscription_tsv_ix", table_name="subscriptions")
    op.drop_index("subscription_product_ix", table_name="subscriptions")
    op.drop_index("subscription_customer_ix", table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_product_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_customer_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_table("products_workflows")
    op.drop_table("product_product_blocks")
    op.drop_table("product_block_resource_types")
    op.drop_index(op.f("ix_process_steps_pid"), table_name="process_steps")
    op.drop_table("process_steps")
    op.drop_table("fixed_inputs")
    op.drop_table("workflows")
    op.drop_table("resource_types")
    op.drop_index(op.f("ix_products_tag"), table_name="products")
    op.drop_table("products")
    op.drop_table("product_blocks")
    op.drop_index(op.f("ix_processes_pid"), table_name="processes")
    op.drop_index(op.f("ix_processes_is_task"), table_name="processes")
    op.drop_table("processes")
    op.drop_table("engine_settings")
    # ### end Alembic commands ###