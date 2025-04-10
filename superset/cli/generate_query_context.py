# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from typing import Type, Any
import sqlalchemy as sa
import click
#import json
from click_option_group import optgroup, RequiredAnyOptionGroup
from flask.cli import with_appcontext
from superset import db
from sqlalchemy.ext.declarative import declarative_base
from superset.migrations.shared.migrate_viz.processors import MigrateLineChart
from superset.utils import core as utils, json

Base: Type[Any] = declarative_base()

class Slice(Base):
    __tablename__ = "slices"

    id = sa.Column(sa.Integer, primary_key=True)
    params = sa.Column(utils.MediumText())
    query_context = sa.Column(utils.MediumText())

@click.group()
def generate_query_context() -> None:
    """
    Generate a query context.
    """


@generate_query_context.command()
@with_appcontext
@optgroup.group(
    cls=RequiredAnyOptionGroup,
)
@optgroup.option(
    "--id",
    help="The chart ID.",
    type=int,
)
def run(id: int | None = None) -> None:
    """Generate a query context for a chart"""
    slice = db.session.query(Slice).filter(Slice.id == id).one_or_none()
    
    form_data = slice.params
    
    migrate_line_chart_obj = MigrateLineChart(form_data)
    result = migrate_line_chart_obj.build_query()
    print(result)


