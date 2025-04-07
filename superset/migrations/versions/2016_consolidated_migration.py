
"""Consolidated migration file for 2016"""

import sqlalchemy as sa
import logging
from alembic import op
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from superset import db
from superset.utils.core import generic_find_constraint_name
from sqlalchemy import Boolean
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from superset.utils.core import get_user_id
from sqlalchemy.dialects import mysql



class Slice(Base):
    """Declarative class to do query in upgrade"""

    __tablename__ = "slices"
    id = Column(Integer, primary_key=True)
    slice_name = Column(String(250))
    druid_datasource_id = Column(Integer, ForeignKey("datasources.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    perm = Column(String(2000))

class DruidMetric(Base):
    """Declarative class used to do query in upgrade"""

    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True)
    is_restricted = Column(Boolean, default=False, nullable=True)

class SqlMetric(Base):
    """Declarative class used to do query in upgrade"""

    __tablename__ = "sql_metrics"
    id = Column(Integer, primary_key=True)
    is_restricted = Column(Boolean, default=False, nullable=True)

class User(Base):
    """Declarative class to do query in upgrade"""

    __tablename__ = "ab_user"
    id = Column(Integer, primary_key=True)

class AuditMixin:
    @declared_attr
    def created_by_fk(cls):  # noqa: N805
        return Column(
            Integer, ForeignKey("ab_user.id"), default=get_user_id, nullable=False
        )

    @declared_attr
    def created_by(cls):  # noqa: N805
        return relationship(
            "User",
            primaryjoin=f"{cls.__name__}.created_by_fk == User.id",
            enable_typechecks=False,
        )

class Slice(AuditMixin, Base):
    """Declarative class to do query in upgrade"""

    __tablename__ = "slices"
    id = Column(Integer, primary_key=True)
    owners = relationship("User", secondary=slice_user)

class Dashboard(AuditMixin, Base):
    """Declarative class to do query in upgrade"""

    __tablename__ = "dashboards"
    id = Column(Integer, primary_key=True)
    owners = relationship("User", secondary=dashboard_user)

class Slice(Base):
    """Declarative class to do query in upgrade"""

    __tablename__ = "slices"
    id = Column(Integer, primary_key=True)
    datasource_id = Column(Integer)
    druid_datasource_id = Column(Integer)
    table_id = Column(Integer)
    datasource_type = Column(String(200))

class Database(Base):
    """An ORM object that stores Database related information"""

    __tablename__ = "dbs"
    id = Column(Integer, primary_key=True)
    allow_run_sync = Column(Boolean, default=True)

def upgrade():
    # From 2016-01-13_20-24_8e80a26a31db_.py
    op.create_table(
        "url",
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("changed_on", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("created_by_fk", sa.Integer(), nullable=True),
        sa.Column("changed_by_fk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_fk"], ["ab_user.id"]),
        sa.ForeignKeyConstraint(["created_by_fk"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

	# From 2016-01-17_22-00_7dbf98566af7_slice_description.py
    op.add_column("slices", sa.Column("description", sa.Text(), nullable=True))

	# From 2016-01-18_23-43_43df8de3a5f4_dash_json.py
    op.add_column("dashboards", sa.Column("json_metadata", sa.Text(), nullable=True))

	# From 2016-02-03_17-41_d827694c7555_css_templates.py
    op.create_table(
        "css_templates",
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("changed_on", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_name", sa.String(length=250), nullable=True),
        sa.Column("css", sa.Text(), nullable=True),
        sa.Column("changed_by_fk", sa.Integer(), nullable=True),
        sa.Column("created_by_fk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_fk"], ["ab_user.id"]),
        sa.ForeignKeyConstraint(["created_by_fk"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

	# From 2016-02-10_08-47_430039611635_log_more.py
    op.add_column("logs", sa.Column("dashboard_id", sa.Integer(), nullable=True))
    op.add_column("logs", sa.Column("slice_id", sa.Integer(), nullable=True))

	# From 2016-03-13_09-56_a2d606a761d9_adding_favstar_model.py
    op.create_table(
        "favstar",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("class_name", sa.String(length=50), nullable=True),
        sa.Column("obj_id", sa.Integer(), nullable=True),
        sa.Column("dttm", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

	# From 2016-03-13_21-30_18e88e1cc004_making_audit_nullable.py
    try:
        op.alter_column(
            "clusters", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "clusters", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.drop_constraint(None, "columns", type_="foreignkey")
        op.drop_constraint(None, "columns", type_="foreignkey")
        op.drop_column("columns", "created_on")
        op.drop_column("columns", "created_by_fk")
        op.drop_column("columns", "changed_on")
        op.drop_column("columns", "changed_by_fk")
        op.alter_column(
            "css_templates", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "css_templates", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "dashboards", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "dashboards", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.create_unique_constraint(None, "dashboards", ["slug"])
        op.alter_column(
            "datasources", "changed_by_fk", existing_type=sa.INTEGER(), nullable=True
        )
        op.alter_column(
            "datasources", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "datasources", "created_by_fk", existing_type=sa.INTEGER(), nullable=True
        )
        op.alter_column(
            "datasources", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column("dbs", "changed_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column("dbs", "created_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column(
            "slices", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "slices", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "sql_metrics", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "sql_metrics", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "table_columns", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "table_columns", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "tables", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "tables", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column("url", "changed_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column("url", "created_on", existing_type=sa.DATETIME(), nullable=True)
    except Exception:  # noqa: S110
        pass

	# From 2016-03-17_08-40_836c0bf75904_cache_timeouts.py
    op.add_column(
        "datasources", sa.Column("cache_timeout", sa.Integer(), nullable=True)
    )
    op.add_column("dbs", sa.Column("cache_timeout", sa.Integer(), nullable=True))
    op.add_column("slices", sa.Column("cache_timeout", sa.Integer(), nullable=True))
    op.add_column("tables", sa.Column("cache_timeout", sa.Integer(), nullable=True))

	# From 2016-03-22_23-25_d2424a248d63_.py
    pass

	# From 2016-03-24_14-13_763d4b211ec9_fixing_audit_fk.py
    op.add_column("metrics", sa.Column("changed_by_fk", sa.Integer(), nullable=True))
    op.add_column("metrics", sa.Column("changed_on", sa.DateTime(), nullable=True))
    op.add_column("metrics", sa.Column("created_by_fk", sa.Integer(), nullable=True))
    op.add_column("metrics", sa.Column("created_on", sa.DateTime(), nullable=True))
    try:
        op.alter_column(
            "columns", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "columns", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "css_templates", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "css_templates", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "dashboards", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "dashboards", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "datasources", "changed_by_fk", existing_type=sa.INTEGER(), nullable=True
        )
        op.alter_column(
            "datasources", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "datasources", "created_by_fk", existing_type=sa.INTEGER(), nullable=True
        )
        op.alter_column(
            "datasources", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column("dbs", "changed_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column("dbs", "created_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column(
            "slices", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "slices", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "sql_metrics", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "sql_metrics", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "table_columns", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "table_columns", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "tables", "changed_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column(
            "tables", "created_on", existing_type=sa.DATETIME(), nullable=True
        )
        op.alter_column("url", "changed_on", existing_type=sa.DATETIME(), nullable=True)
        op.alter_column("url", "created_on", existing_type=sa.DATETIME(), nullable=True)
        op.create_foreign_key(None, "metrics", "ab_user", ["changed_by_fk"], ["id"])
        op.create_foreign_key(None, "metrics", "ab_user", ["created_by_fk"], ["id"])
    except:  # noqa: E722, S110
        pass

	# From 2016-03-25_14-35_1d2ddd543133_log_dt.py
    op.add_column("logs", sa.Column("dt", sa.Date(), nullable=True))

	# From 2016-03-26_15-09_fee7b758c130_.py
    pass

	# From 2016-04-03_15-23_867bf4f117f9_adding_extra_field_to_database_model.py
    op.add_column("dbs", sa.Column("extra", sa.Text(), nullable=True))

	# From 2016-04-11_22-41_bb51420eaf83_add_schema_to_table_model.py
    op.add_column("tables", sa.Column("schema", sa.String(length=255), nullable=True))

	# From 2016-04-15_08-31_b4456560d4f3_change_table_unique_constraint.py
    try:
        # Trying since sqlite doesn't like constraints
        op.drop_constraint("tables_table_name_key", "tables", type_="unique")
        op.create_unique_constraint(
            "_customer_location_uc", "tables", ["database_id", "schema", "table_name"]
        )
    except Exception:  # noqa: S110
        pass

	# From 2016-04-15_17-58_4fa88fe24e94_owners_many_to_many.py
    op.create_table(
        "dashboard_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("dashboard_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "slice_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("slice_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["slice_id"], ["slices.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

	# From 2016-04-25_08-54_c3a8f8611885_materializing_permission.py
    bind = op.get_bind()
    op.add_column("slices", sa.Column("perm", sa.String(length=2000), nullable=True))
    session = db.Session(bind=bind)

    # Use Slice class defined here instead of models.Slice
    for slc in session.query(Slice).all():
        if slc.datasource:
            slc.perm = slc.datasource.perm
            session.commit()
    db.session.close()

	# From 2016-05-01_12-21_f0fbf6129e13_adding_verbose_name_to_tablecolumn.py
    op.add_column(
        "table_columns",
        sa.Column("verbose_name", sa.String(length=1024), nullable=True),
    )

	# From 2016-05-11_17-28_956a063c52b3_adjusting_key_length.py
    with op.batch_alter_table("clusters", schema=None) as batch_op:
        batch_op.alter_column(
            "broker_endpoint",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "broker_host",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "coordinator_endpoint",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "coordinator_host",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    with op.batch_alter_table("columns", schema=None) as batch_op:
        batch_op.alter_column(
            "column_name",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    with op.batch_alter_table("datasources", schema=None) as batch_op:
        batch_op.alter_column(
            "datasource_name",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    with op.batch_alter_table("table_columns", schema=None) as batch_op:
        batch_op.alter_column(
            "column_name",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

    with op.batch_alter_table("tables", schema=None) as batch_op:
        batch_op.alter_column(
            "schema",
            existing_type=sa.VARCHAR(length=256),
            type_=sa.String(length=255),
            existing_nullable=True,
        )

	# From 2016-05-27_15-03_1226819ee0e3_fix_wrong_constraint_on_table_columns.py
    try:
        constraint = find_constraint_name()
        with op.batch_alter_table(
            "columns", naming_convention=naming_convention
        ) as batch_op:
            if constraint:
                batch_op.drop_constraint(constraint, type_="foreignkey")
            batch_op.create_foreign_key(
                "fk_columns_datasource_name_datasources",
                "datasources",
                ["datasource_name"],
                ["datasource_name"],
            )
    except:  # noqa: E722
        logging.warning("Could not find or drop constraint on `columns`")

	# From 2016-06-07_12-33_d8bc074f7aad_add_new_field_is_restricted_to_.py
    op.add_column("metrics", sa.Column("is_restricted", sa.Boolean(), nullable=True))
    op.add_column(
        "sql_metrics", sa.Column("is_restricted", sa.Boolean(), nullable=True)
    )

    bind = op.get_bind()
    session = db.Session(bind=bind)

    # don't use models.DruidMetric
    # because it assumes the context is consistent with the application
    for obj in session.query(DruidMetric).all():
        obj.is_restricted = False

    for obj in session.query(SqlMetric).all():
        obj.is_restricted = False

    session.commit()
    session.close()

	# From 2016-06-16_14-15_960c69cb1f5b_.py
    op.add_column(
        "table_columns",
        sa.Column("python_date_format", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "table_columns",
        sa.Column("database_expression", sa.String(length=255), nullable=True),
    )

	# From 2016-06-27_08-43_27ae655e4247_make_creator_owners.py
    bind = op.get_bind()
    session = db.Session(bind=bind)

    objects = session.query(Slice).all()
    objects += session.query(Dashboard).all()
    for obj in objects:
        if obj.created_by and obj.created_by not in obj.owners:
            obj.owners.append(obj.created_by)
        session.commit()
    session.close()

	# From 2016-07-06_22-04_f162a1dea4c4_d3format_by_metric.py
    op.add_column(
        "metrics", sa.Column("d3format", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "sql_metrics", sa.Column("d3format", sa.String(length=128), nullable=True)
    )

	# From 2016-07-25_17-48_ad82a75afd82_add_query_model.py
    op.create_table(
        "query",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.String(length=11), nullable=False),
        sa.Column("database_id", sa.Integer(), nullable=False),
        sa.Column("tmp_table_name", sa.String(length=256), nullable=True),
        sa.Column("tab_name", sa.String(length=256), nullable=True),
        sa.Column("sql_editor_id", sa.String(length=256), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("schema", sa.String(length=256), nullable=True),
        sa.Column("sql", sa.Text(), nullable=True),
        sa.Column("select_sql", sa.Text(), nullable=True),
        sa.Column("executed_sql", sa.Text(), nullable=True),
        sa.Column("limit", sa.Integer(), nullable=True),
        sa.Column("limit_used", sa.Boolean(), nullable=True),
        sa.Column("select_as_cta", sa.Boolean(), nullable=True),
        sa.Column("select_as_cta_used", sa.Boolean(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("rows", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("start_time", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column("changed_on", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.Numeric(precision=20, scale=6), nullable=True),
        sa.ForeignKeyConstraint(["database_id"], ["dbs.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "dbs", sa.Column("select_as_create_table_as", sa.Boolean(), nullable=True)
    )
    op.create_index(
        op.f("ti_user_id_changed_on"), "query", ["user_id", "changed_on"], unique=False
    )

	# From 2016-08-18_14-06_3c3ffe173e4f_add_sql_string_to_table.py
    op.add_column("tables", sa.Column("sql", sa.Text(), nullable=True))

	# From 2016-08-31_10-26_41f6a59a61f2_database_options_for_sql_lab.py
    op.add_column("dbs", sa.Column("allow_ctas", sa.Boolean(), nullable=True))
    op.add_column("dbs", sa.Column("expose_in_sqllab", sa.Boolean(), nullable=True))
    op.add_column(
        "dbs", sa.Column("force_ctas_schema", sa.String(length=250), nullable=True)
    )

	# From 2016-09-07_23-50_33d996bcc382_update_slice_model.py
    bind = op.get_bind()
    op.add_column("slices", sa.Column("datasource_id", sa.Integer()))
    session = db.Session(bind=bind)

    for slc in session.query(Slice).all():
        if slc.druid_datasource_id:
            slc.datasource_id = slc.druid_datasource_id
        if slc.table_id:
            slc.datasource_id = slc.table_id
        session.commit()
    session.close()

	# From 2016-09-09_17-39_5e4a03ef0bf0_add_request_access_model.py
    op.create_table(
        "access_request",
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.Column("changed_on", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("datasource_type", sa.String(length=200), nullable=True),
        sa.Column("datasource_id", sa.Integer(), nullable=True),
        sa.Column("changed_by_fk", sa.Integer(), nullable=True),
        sa.Column("created_by_fk", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_fk"], ["ab_user.id"]),
        sa.ForeignKeyConstraint(["created_by_fk"], ["ab_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

	# From 2016-09-12_23-33_4500485bde7d_allow_run_sync_async.py
    op.add_column("dbs", sa.Column("allow_run_async", sa.Boolean(), nullable=True))
    op.add_column("dbs", sa.Column("allow_run_sync", sa.Boolean(), nullable=True))

	# From 2016-09-15_08-48_65903709c321_allow_dml.py
    op.add_column("dbs", sa.Column("allow_dml", sa.Boolean(), nullable=True))

	# From 2016-09-19_17-22_b347b202819b_.py
    pass

	# From 2016-09-22_10-21_3b626e2a6783_sync_db_with_models.py
    # cleanup after: https://github.com/airbnb/superset/pull/1078
    try:
        slices_ibfk_1 = generic_find_constraint_name(
            table="slices",
            columns={"druid_datasource_id"},
            referenced="datasources",
            database=db,
        )
        slices_ibfk_2 = generic_find_constraint_name(
            table="slices", columns={"table_id"}, referenced="tables", database=db
        )

        with op.batch_alter_table("slices") as batch_op:
            if slices_ibfk_1:
                batch_op.drop_constraint(slices_ibfk_1, type_="foreignkey")
            if slices_ibfk_2:
                batch_op.drop_constraint(slices_ibfk_2, type_="foreignkey")
            batch_op.drop_column("druid_datasource_id")
            batch_op.drop_column("table_id")
    except Exception as ex:
        logging.warning(str(ex))

    # fixed issue: https://github.com/airbnb/superset/issues/466
    try:
        with op.batch_alter_table("columns") as batch_op:
            batch_op.create_foreign_key(
                None, "datasources", ["datasource_name"], ["datasource_name"]
            )
    except Exception as ex:
        logging.warning(str(ex))
    try:
        with op.batch_alter_table("query") as batch_op:
            batch_op.create_unique_constraint("client_id", ["client_id"])
    except Exception as ex:
        logging.warning(str(ex))

    try:
        with op.batch_alter_table("query") as batch_op:
            batch_op.drop_column("name")
    except Exception as ex:
        logging.warning(str(ex))

	# From 2016-09-22_11-31_eca4694defa7_sqllab_setting_defaults.py
    bind = op.get_bind()
    session = db.Session(bind=bind)

    for obj in session.query(Database).all():
        obj.allow_run_sync = True

    session.commit()
    session.close()

	# From 2016-09-30_18-01_ab3d66c4246e_add_cache_timeout_to_druid_cluster.py
    op.add_column("clusters", sa.Column("cache_timeout", sa.Integer(), nullable=True))

	# From 2016-10-02_10-35_ef8843b41dac_.py
    pass

	# From 2016-10-05_11-30_b46fa1b0b39e_add_params_to_tables.py
    op.add_column("tables", sa.Column("params", sa.Text(), nullable=True))

	# From 2016-10-14_11-17_7e3ddad2a00b_results_key_to_query.py
    op.add_column(
        "query", sa.Column("results_key", sa.String(length=64), nullable=True)
    )

	# From 2016-10-25_10-16_ad4d656d92bc_add_avg_metric.py
    op.add_column("columns", sa.Column("avg", sa.Boolean(), nullable=True))
    op.add_column("table_columns", sa.Column("avg", sa.Boolean(), nullable=True))

	# From 2016-11-02_17-36_c611f2b591b8_dim_spec.py
    op.add_column("columns", sa.Column("dimension_spec_json", sa.Text(), nullable=True))

	# From 2016-11-14_15-23_e46f2d27a08e_materialize_perms.py
    op.add_column(
        "datasources", sa.Column("perm", sa.String(length=1000), nullable=True)
    )
    op.add_column("dbs", sa.Column("perm", sa.String(length=1000), nullable=True))
    op.add_column("tables", sa.Column("perm", sa.String(length=1000), nullable=True))

	# From 2016-11-23_10-27_f1f2d4af5b90_.py
    op.add_column(
        "datasources", sa.Column("filter_select_enabled", sa.Boolean(), default=False)
    )
    op.add_column(
        "tables", sa.Column("filter_select_enabled", sa.Boolean(), default=False)
    )

	# From 2016-12-06_17-40_1296d28ec131_druid_exports.py
    op.add_column(
        "datasources", sa.Column("params", sa.String(length=1000), nullable=True)
    )

	# From 2016-12-13_16-19_525c854f0005_log_this_plus.py
    op.add_column("logs", sa.Column("duration_ms", sa.Integer(), nullable=True))
    op.add_column("logs", sa.Column("referrer", sa.String(length=1024), nullable=True))

	# From 2016-12-19_09-57_6414e83d82b7_.py
    pass

def downgrade():
    # From 2016-12-19_09-57_6414e83d82b7_.py
    pass

	# From 2016-12-13_16-19_525c854f0005_log_this_plus.py
    op.drop_column("logs", "referrer")
    op.drop_column("logs", "duration_ms")

	# From 2016-12-06_17-40_1296d28ec131_druid_exports.py
    op.drop_column("datasources", "params")

	# From 2016-11-23_10-27_f1f2d4af5b90_.py
    op.drop_column("tables", "filter_select_enabled")
    op.drop_column("datasources", "filter_select_enabled")

	# From 2016-11-14_15-23_e46f2d27a08e_materialize_perms.py
    op.drop_column("tables", "perm")
    op.drop_column("datasources", "perm")
    op.drop_column("dbs", "perm")

	# From 2016-11-02_17-36_c611f2b591b8_dim_spec.py
    op.drop_column("columns", "dimension_spec_json")

	# From 2016-10-25_10-16_ad4d656d92bc_add_avg_metric.py
    with op.batch_alter_table("columns") as batch_op:
        batch_op.drop_column("avg")
    with op.batch_alter_table("table_columns") as batch_op:
        batch_op.drop_column("avg")

	# From 2016-10-14_11-17_7e3ddad2a00b_results_key_to_query.py
    op.drop_column("query", "results_key")

	# From 2016-10-05_11-30_b46fa1b0b39e_add_params_to_tables.py
    try:
        op.drop_column("tables", "params")
    except Exception as ex:
        logging.warning(str(ex))

	# From 2016-10-02_10-35_ef8843b41dac_.py
    pass

	# From 2016-09-30_18-01_ab3d66c4246e_add_cache_timeout_to_druid_cluster.py
    op.drop_column("clusters", "cache_timeout")

	# From 2016-09-22_11-31_eca4694defa7_sqllab_setting_defaults.py
    pass

	# From 2016-09-22_10-21_3b626e2a6783_sync_db_with_models.py
    try:
        with op.batch_alter_table("tables") as batch_op:
            batch_op.create_index("table_name", ["table_name"], unique=True)
    except Exception as ex:
        logging.warning(str(ex))

    try:
        with op.batch_alter_table("slices") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "table_id",
                    mysql.INTEGER(display_width=11),
                    autoincrement=False,
                    nullable=True,
                )
            )
            batch_op.add_column(
                sa.Column(
                    "druid_datasource_id",
                    sa.Integer(),
                    autoincrement=False,
                    nullable=True,
                )
            )
            batch_op.create_foreign_key(
                "slices_ibfk_1", "datasources", ["druid_datasource_id"], ["id"]
            )
            batch_op.create_foreign_key("slices_ibfk_2", "tables", ["table_id"], ["id"])
    except Exception as ex:
        logging.warning(str(ex))

    try:
        fk_columns = generic_find_constraint_name(
            table="columns",
            columns={"datasource_name"},
            referenced="datasources",
            database=db,
        )
        with op.batch_alter_table("columns") as batch_op:
            batch_op.drop_constraint(fk_columns, type_="foreignkey")
    except Exception as ex:
        logging.warning(str(ex))

    op.add_column("query", sa.Column("name", sa.String(length=256), nullable=True))
    try:
        with op.batch_alter_table("query") as batch_op:
            batch_op.drop_constraint("client_id", type_="unique")
    except Exception as ex:
        logging.warning(str(ex))

	# From 2016-09-19_17-22_b347b202819b_.py
    pass

	# From 2016-09-15_08-48_65903709c321_allow_dml.py
    try:
        op.drop_column("dbs", "allow_dml")
    except Exception as ex:
        logging.exception(ex)
        pass

	# From 2016-09-12_23-33_4500485bde7d_allow_run_sync_async.py
    try:
        op.drop_column("dbs", "allow_run_sync")
        op.drop_column("dbs", "allow_run_async")
    except Exception:  # noqa: S110
        pass

	# From 2016-09-09_17-39_5e4a03ef0bf0_add_request_access_model.py
    op.drop_table("access_request")

	# From 2016-09-07_23-50_33d996bcc382_update_slice_model.py
    bind = op.get_bind()
    session = db.Session(bind=bind)
    for slc in session.query(Slice).all():
        if slc.datasource_type == "druid":
            slc.druid_datasource_id = slc.datasource_id
        if slc.datasource_type == "table":
            slc.table_id = slc.datasource_id
        session.commit()
    session.close()
    op.drop_column("slices", "datasource_id")

	# From 2016-08-31_10-26_41f6a59a61f2_database_options_for_sql_lab.py
    op.drop_column("dbs", "force_ctas_schema")
    op.drop_column("dbs", "expose_in_sqllab")
    op.drop_column("dbs", "allow_ctas")

	# From 2016-08-18_14-06_3c3ffe173e4f_add_sql_string_to_table.py
    op.drop_column("tables", "sql")

	# From 2016-07-25_17-48_ad82a75afd82_add_query_model.py
    op.drop_table("query")
    op.drop_column("dbs", "select_as_create_table_as")

	# From 2016-07-06_22-04_f162a1dea4c4_d3format_by_metric.py
    op.drop_column("sql_metrics", "d3format")
    op.drop_column("metrics", "d3format")

	# From 2016-06-27_08-43_27ae655e4247_make_creator_owners.py
    pass

	# From 2016-06-16_14-15_960c69cb1f5b_.py
    op.drop_column("table_columns", "python_date_format")
    op.drop_column("table_columns", "database_expression")

	# From 2016-06-07_12-33_d8bc074f7aad_add_new_field_is_restricted_to_.py
    with op.batch_alter_table("sql_metrics", schema=None) as batch_op:
        batch_op.drop_column("is_restricted")

    with op.batch_alter_table("metrics", schema=None) as batch_op:
        batch_op.drop_column("is_restricted")

	# From 2016-05-27_15-03_1226819ee0e3_fix_wrong_constraint_on_table_columns.py
    constraint = find_constraint_name(False) or "fk_columns_datasource_name_datasources"
    with op.batch_alter_table(
        "columns", naming_convention=naming_convention
    ) as batch_op:
        batch_op.drop_constraint(constraint, type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_columns_column_name_datasources",
            "datasources",
            ["column_name"],
            ["datasource_name"],
        )

	# From 2016-05-11_17-28_956a063c52b3_adjusting_key_length.py
    with op.batch_alter_table("tables", schema=None) as batch_op:
        batch_op.alter_column(
            "schema",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )

    with op.batch_alter_table("table_columns", schema=None) as batch_op:
        batch_op.alter_column(
            "column_name",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )

    with op.batch_alter_table("datasources", schema=None) as batch_op:
        batch_op.alter_column(
            "datasource_name",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )

    with op.batch_alter_table("columns", schema=None) as batch_op:
        batch_op.alter_column(
            "column_name",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )

    with op.batch_alter_table("clusters", schema=None) as batch_op:
        batch_op.alter_column(
            "coordinator_host",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "coordinator_endpoint",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "broker_host",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "broker_endpoint",
            existing_type=sa.String(length=255),
            type_=sa.VARCHAR(length=256),
            existing_nullable=True,
        )

	# From 2016-05-01_12-21_f0fbf6129e13_adding_verbose_name_to_tablecolumn.py
    op.drop_column("table_columns", "verbose_name")

	# From 2016-04-25_08-54_c3a8f8611885_materializing_permission.py
    # Use batch_alter_table because dropping columns is not supported in SQLite
    with op.batch_alter_table("slices") as batch_op:
        batch_op.drop_column("perm")

	# From 2016-04-15_17-58_4fa88fe24e94_owners_many_to_many.py
    op.drop_table("slice_user")
    op.drop_table("dashboard_user")

	# From 2016-04-15_08-31_b4456560d4f3_change_table_unique_constraint.py
    try:
        # Trying since sqlite doesn't like constraints
        op.drop_constraint("_customer_location_uc", "tables", type_="unique")
    except Exception:  # noqa: S110
        pass

	# From 2016-04-11_22-41_bb51420eaf83_add_schema_to_table_model.py
    op.drop_column("tables", "schema")

	# From 2016-04-03_15-23_867bf4f117f9_adding_extra_field_to_database_model.py
    op.drop_column("dbs", "extra")

	# From 2016-03-26_15-09_fee7b758c130_.py
    pass

	# From 2016-03-25_14-35_1d2ddd543133_log_dt.py
    op.drop_column("logs", "dt")

	# From 2016-03-24_14-13_763d4b211ec9_fixing_audit_fk.py
    op.drop_column("metrics", "created_on")
    op.drop_column("metrics", "created_by_fk")
    op.drop_column("metrics", "changed_on")
    op.drop_column("metrics", "changed_by_fk")
    try:
        op.alter_column(
            "url", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "url", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "tables", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "tables", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "table_columns", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "table_columns", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "sql_metrics", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "sql_metrics", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "slices", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "slices", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.drop_constraint(None, "metrics", type_="foreignkey")
        op.drop_constraint(None, "metrics", type_="foreignkey")
        op.alter_column(
            "dbs", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "dbs", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "datasources", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "datasources", "created_by_fk", existing_type=sa.INTEGER(), nullable=False
        )
        op.alter_column(
            "datasources", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "datasources", "changed_by_fk", existing_type=sa.INTEGER(), nullable=False
        )
        op.alter_column(
            "dashboards", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "dashboards", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "css_templates", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "css_templates", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "columns", "created_on", existing_type=sa.DATETIME(), nullable=False
        )
        op.alter_column(
            "columns", "changed_on", existing_type=sa.DATETIME(), nullable=False
        )
    except:  # noqa: E722, S110
        pass

	# From 2016-03-22_23-25_d2424a248d63_.py
    pass

	# From 2016-03-17_08-40_836c0bf75904_cache_timeouts.py
    op.drop_column("tables", "cache_timeout")
    op.drop_column("slices", "cache_timeout")
    op.drop_column("dbs", "cache_timeout")
    op.drop_column("datasources", "cache_timeout")

	# From 2016-03-13_21-30_18e88e1cc004_making_audit_nullable.py
    pass

	# From 2016-03-13_09-56_a2d606a761d9_adding_favstar_model.py
    op.drop_table("favstar")

	# From 2016-02-10_08-47_430039611635_log_more.py
    op.drop_column("logs", "slice_id")
    op.drop_column("logs", "dashboard_id")

	# From 2016-02-03_17-41_d827694c7555_css_templates.py
    op.drop_table("css_templates")

	# From 2016-01-18_23-43_43df8de3a5f4_dash_json.py
    op.drop_column("dashboards", "json_metadata")

	# From 2016-01-17_22-00_7dbf98566af7_slice_description.py
    op.drop_column("slices", "description")

	# From 2016-01-13_20-24_8e80a26a31db_.py
    op.drop_table("url")
