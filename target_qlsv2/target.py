"""QlsV2 target class."""

from typing import Type

from singer_sdk import typing as th
from singer_sdk.sinks import Sink
from singer_sdk.target_base import Target

from target_qlsv2.sinks import BuyOrdersV2Sink, UpdateInventorySink

SINK_TYPES = [BuyOrdersV2Sink, UpdateInventorySink]


class TargetQlsV2(Target):
    """Sample target for QlsV2."""

    name = "target-qlsv2"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "filepath", th.StringType, description="The path to the target output file"
        ),
    ).to_dict()

    def get_sink_class(self, stream_name: str) -> Type[Sink]:
        """Get sink for a stream."""
        return next(
            (
                sink_class
                for sink_class in SINK_TYPES
                if sink_class.name.lower() == stream_name.lower()
            ),
            None,
        )


if __name__ == "__main__":
    TargetQlsV2.cli()
