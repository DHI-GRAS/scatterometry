class BoundingBox:
    def __init__(
        self,
        bbox: str = None,
        lon_min: float = None,
        lat_min: float = None,
        lon_max: float = None,
        lat_max: float = None,
    ) -> None:

        if isinstance(bbox, (type(None), str)) is False:
            raise TypeError(f"Expected bbox type None or str not {type(bbox)}")

        if bbox:
            (self.lon_min, self.lat_min, self.lon_max, self.lat_max) = self.parse_bbox(
                bbox
            )
            return

        if not all(lon_min, lat_min, lon_max, lat_max):
            raise TypeError(
                f"Encountered empty or limits {lon_min, lat_min, lon_max, lat_max}"
            )

        self.lon_min = lon_min
        self.lat_min = lat_min
        self.lon_max = lon_max
        self.lat_max = lat_max

    def parse_bbox(self, bbox):
        limits = bbox.split(",")
        if len(limits) != 4:
            raise ValueError(
                f"Expected a bbox value of four comma separated numbers not {bbox}"
            )

        float_limits = []
        for limit in limits:
            try:
                float_limits.append(float(limit))
            except ValueError:
                raise ValueError(f"Encountered non numerical bbox limit: {limit}")

        return float_limits
