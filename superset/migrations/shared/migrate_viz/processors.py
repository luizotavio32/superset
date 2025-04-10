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
from typing import Any

from superset.utils.core import as_list
from superset.migrations.shared.migrate_viz.query_functions import *

from .base import MigrateViz


class MigrateTreeMap(MigrateViz):
    source_viz_type = "treemap"
    target_viz_type = "treemap_v2"
    remove_keys = {"metrics"}
    rename_keys = {"order_desc": "sort_by_metric"}

    def _pre_action(self) -> None:
        if (
            "metrics" in self.data
            and isinstance(self.data["metrics"], list)
            and len(self.data["metrics"]) > 0
        ):
            self.data["metric"] = self.data["metrics"][0]

    def build_query(form_data):
        pass


class MigratePivotTable(MigrateViz):
    source_viz_type = "pivot_table"
    target_viz_type = "pivot_table_v2"
    remove_keys = {"pivot_margins"}
    rename_keys = {
        "columns": "groupbyColumns",
        "combine_metric": "combineMetric",
        "groupby": "groupbyRows",
        "number_format": "valueFormat",
        "pandas_aggfunc": "aggregateFunction",
        "row_limit": "series_limit",
        "timeseries_limit_metric": "series_limit_metric",
        "transpose_pivot": "transposePivot",
    }
    aggregation_mapping = {
        "sum": "Sum",
        "mean": "Average",
        "median": "Median",
        "min": "Minimum",
        "max": "Maximum",
        "std": "Sample Standard Deviation",
        "var": "Sample Variance",
    }

    def _pre_action(self) -> None:
        if pivot_margins := self.data.get("pivot_margins"):
            self.data["colTotals"] = pivot_margins
            self.data["colSubTotals"] = pivot_margins

        if pandas_aggfunc := self.data.get("pandas_aggfunc"):
            self.data["pandas_aggfunc"] = self.aggregation_mapping[pandas_aggfunc]

        self.data["rowOrder"] = "value_z_to_a"

    def build_query():
        pass


class MigrateDualLine(MigrateViz):
    has_x_axis_control = True
    source_viz_type = "dual_line"
    target_viz_type = "mixed_timeseries"
    rename_keys = {
        "x_axis_format": "x_axis_time_format",
        "y_axis_2_format": "y_axis_format_secondary",
        "y_axis_2_bounds": "y_axis_bounds_secondary",
    }
    remove_keys = {"metric", "metric_2"}

    def _pre_action(self) -> None:
        self.data["yAxisIndex"] = 0
        self.data["yAxisIndexB"] = 1
        self.data["adhoc_filters_b"] = self.data.get("adhoc_filters")
        self.data["truncateYAxis"] = True
        self.data["metrics"] = [self.data.get("metric")]
        self.data["metrics_b"] = [self.data.get("metric_2")]

    def _migrate_temporal_filter(self, rv_data: dict[str, Any]) -> None:
        super()._migrate_temporal_filter(rv_data)
        rv_data["adhoc_filters_b"] = rv_data.get("adhoc_filters") or []

    def build_query():
        pass


class MigrateSunburst(MigrateViz):
    source_viz_type = "sunburst"
    target_viz_type = "sunburst_v2"
    rename_keys = {"groupby": "columns"}

    def build_query():
        pass


class TimeseriesChart(MigrateViz):
    has_x_axis_control = True
    rename_keys = {
        "bottom_margin": "x_axis_title_margin",
        "left_margin": "y_axis_title_margin",
        "show_controls": "show_extra_controls",
        "x_axis_label": "x_axis_title",
        "x_axis_format": "x_axis_time_format",
        "x_axis_showminmax": "truncateXAxis",
        "x_ticks_layout": "xAxisLabelRotation",
        "y_axis_label": "y_axis_title",
        "y_axis_showminmax": "truncateYAxis",
        "y_log_scale": "logAxis",
    }
    remove_keys = {
        "contribution",
        "line_interpolation",
        "reduce_x_ticks",
        "show_brush",
        "show_markers",
    }

    def _pre_action(self) -> None:
        self.data["contributionMode"] = "row" if self.data.get("contribution") else None
        self.data["zoomable"] = self.data.get("show_brush") == "yes"
        self.data["markerEnabled"] = self.data.get("show_markers") or False
        self.data["y_axis_showminmax"] = True

        bottom_margin = self.data.get("bottom_margin")
        if self.data.get("x_axis_label") and (
            not bottom_margin or bottom_margin == "auto"
        ):
            self.data["bottom_margin"] = 30

        left_margin = self.data.get("left_margin")
        if self.data.get("y_axis_label") and (not left_margin or left_margin == "auto"):
            self.data["left_margin"] = 30

        if (rolling_type := self.data.get("rolling_type")) and rolling_type != "None":
            self.data["rolling_type"] = rolling_type

        if time_compare := self.data.get("time_compare"):
            self.data["time_compare"] = [
                value + " ago" for value in as_list(time_compare) if value
            ]

        comparison_type = self.data.get("comparison_type") or "values"
        self.data["comparison_type"] = (
            "difference" if comparison_type == "absolute" else comparison_type
        )

        if x_ticks_layout := self.data.get("x_ticks_layout"):
            self.data["x_ticks_layout"] = 45 if x_ticks_layout == "45°" else 0

    def build_query(self):
        groupby = self.data.get("groupby")
    
        def query_builder(base_query_object):
            """
            The `pivot_operator_in_runtime` determines how to pivot the dataframe returned from the raw query.
            1. If it's a time compared query, there will return a pivoted dataframe that append time compared metrics. for instance:
            
                            MAX(value) MAX(value)__1 year ago MIN(value) MIN(value)__1 year ago
            city               LA                     LA         LA                     LA
            __timestamp
            2015-01-01      568.0                  671.0        5.0                    6.0
            2015-02-01      407.0                  649.0        4.0                    3.0
            2015-03-01      318.0                  465.0        0.0                    3.0
            
            2. If it's a normal query, there will return a pivoted dataframe.
            
                        MAX(value)  MIN(value)
            city               LA          LA
            __timestamp
            2015-01-01      568.0         5.0
            2015-02-01      407.0         4.0
            2015-03-01      318.0         0.0
            """
            # only add series limit metric if it's explicitly needed e.g. for sorting
            extra_metrics = extract_extra_metrics(self.data)
            
            pivot_operator_in_runtime = (
                time_compare_pivot_operator(self.data, base_query_object) 
                if is_time_comparison(self.data, base_query_object) 
                else pivot_operator(self.data, base_query_object)
            )
            
            columns = (
                (ensure_is_array(get_x_axis_column(self.data)) if is_x_axis_set(self.data) else []) +
                ensure_is_array(groupby)
            )
            
            time_offsets = self.data.get("time_compare") if is_time_comparison(self.data, base_query_object) else []
            
            result = {
                **base_query_object,
                "metrics": (base_query_object.get("metrics") or []) + extra_metrics,
                "columns": columns,
                "series_columns": groupby,
                **({"is_timeseries": True} if not is_x_axis_set(self.data) else {}),
                # todo: move `normalize_order_by to extract_query_fields`
                "orderby": normalize_order_by(base_query_object).get("orderby"),
                "time_offsets": time_offsets,
                # Note that:
                # 1. The resample, rolling, cum, timeCompare operators should be after pivot.
                # 2. the flatOperator makes multiIndex Dataframe into flat Dataframe
                "post_processing": [
                    pivot_operator_in_runtime,
                    rolling_window_operator(self.data, base_query_object),
                    time_compare_operator(self.data, base_query_object),
                    resample_operator(self.data, base_query_object),
                    rename_operator(self.data, base_query_object),
                    contribution_operator(self.data, base_query_object, time_offsets),
                    sort_operator(self.data, base_query_object),
                    flatten_operator(self.data, base_query_object),
                    # todo: move prophet before flatten
                    prophet_operator(self.data, base_query_object),
                ]
            }
            
            return [result]
    
        return build_query_context(self.data, query_builder)


class MigrateLineChart(TimeseriesChart):
    source_viz_type = "line"
    target_viz_type = "echarts_timeseries_line"

    def _pre_action(self) -> None:
        super()._pre_action()

        line_interpolation = self.data.get("line_interpolation")
        if line_interpolation == "cardinal":
            self.target_viz_type = "echarts_timeseries_smooth"
        elif line_interpolation == "step-before":
            self.target_viz_type = "echarts_timeseries_step"
            self.data["seriesType"] = "start"
        elif line_interpolation == "step-after":
            self.target_viz_type = "echarts_timeseries_step"
            self.data["seriesType"] = "end"

    def build_query(self):
        return super().build_query()

class MigrateAreaChart(TimeseriesChart):
    source_viz_type = "area"
    target_viz_type = "echarts_area"
    stacked_map = {
        "expand": "Expand",
        "stack": "Stack",
        "stream": "Stream",
    }

    def _pre_action(self) -> None:
        super()._pre_action()

        self.remove_keys.add("stacked_style")

        self.data["stack"] = self.stacked_map.get(
            self.data.get("stacked_style") or "stack"
        )

        self.data["opacity"] = 0.7


class MigrateBarChart(TimeseriesChart):
    source_viz_type = "bar"
    target_viz_type = "echarts_timeseries_bar"

    def _pre_action(self) -> None:
        super()._pre_action()

        self.rename_keys["show_bar_value"] = "show_value"

        self.remove_keys.add("bar_stacked")

        self.data["stack"] = "Stack" if self.data.get("bar_stacked") else None


class MigrateDistBarChart(TimeseriesChart):
    source_viz_type = "dist_bar"
    target_viz_type = "echarts_timeseries_bar"
    has_x_axis_control = False

    def _pre_action(self) -> None:
        super()._pre_action()

        groupby = self.data.get("groupby") or []
        columns = self.data.get("columns") or []
        if len(groupby) > 0:
            # x-axis supports only one value
            self.data["x_axis"] = groupby[0]

        self.data["groupby"] = []
        if len(groupby) > 1:
            # rest of groupby will go into dimensions
            self.data["groupby"] += groupby[1:]
        if len(columns) > 0:
            self.data["groupby"] += columns

        self.rename_keys["show_bar_value"] = "show_value"

        self.remove_keys.add("columns")
        self.remove_keys.add("bar_stacked")

        self.data["stack"] = "Stack" if self.data.get("bar_stacked") else None
        self.data["x_ticks_layout"] = 45


class MigrateBubbleChart(MigrateViz):
    source_viz_type = "bubble"
    target_viz_type = "bubble_v2"
    rename_keys = {
        "bottom_margin": "x_axis_title_margin",
        "left_margin": "y_axis_title_margin",
        "limit": "row_limit",
        "x_axis_format": "xAxisFormat",
        "x_log_scale": "logXAxis",
        "x_ticks_layout": "xAxisLabelRotation",
        "y_axis_showminmax": "truncateYAxis",
        "y_log_scale": "logYAxis",
    }
    remove_keys = {"x_axis_showminmax"}

    def _pre_action(self) -> None:
        bottom_margin = self.data.get("bottom_margin")
        if self.data.get("x_axis_label") and (
            not bottom_margin or bottom_margin == "auto"
        ):
            self.data["bottom_margin"] = 30

        if x_ticks_layout := self.data.get("x_ticks_layout"):
            self.data["x_ticks_layout"] = 45 if x_ticks_layout == "45°" else 0

        # Truncate y-axis by default to preserve layout
        self.data["y_axis_showminmax"] = True

    def build_query():
        pass


class MigrateHeatmapChart(MigrateViz):
    source_viz_type = "heatmap"
    target_viz_type = "heatmap_v2"
    rename_keys = {
        "all_columns_x": "x_axis",
        "all_columns_y": "groupby",
        "y_axis_bounds": "value_bounds",
        "show_perc": "show_percentage",
    }
    remove_keys = {"sort_by_metric", "canvas_image_rendering"}

    def _pre_action(self) -> None:
        self.data["legend_type"] = "continuous"

    def build_query():
        pass


class MigrateHistogramChart(MigrateViz):
    source_viz_type = "histogram"
    target_viz_type = "histogram_v2"
    rename_keys = {
        "x_axis_label": "x_axis_title",
        "y_axis_label": "y_axis_title",
        "normalized": "normalize",
    }
    remove_keys = {"all_columns_x", "link_length", "queryFields"}

    def _pre_action(self) -> None:
        all_columns_x = self.data.get("all_columns_x")
        if all_columns_x and len(all_columns_x) > 0:
            self.data["column"] = all_columns_x[0]

        link_length = self.data.get("link_length")
        self.data["bins"] = int(link_length) if link_length else 5

        groupby = self.data.get("groupby")
        if not groupby:
            self.data["groupby"] = []

    def build_query():
        pass


class MigrateSankey(MigrateViz):
    source_viz_type = "sankey"
    target_viz_type = "sankey_v2"
    remove_keys = {"groupby"}

    def _pre_action(self) -> None:
        groupby = self.data.get("groupby")
        if groupby and len(groupby) > 1:
            self.data["source"] = groupby[0]
            self.data["target"] = groupby[1]

    def build_query():
        pass
