from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 20.0
knurl_height = 4.0
knurl_width = 6.0
knurl_count = 12
spline_depth = 2.0
spline_width = 4.0
spline_count = 6
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    knurl = Pos(outer_radius + knurl_height / 2.0, 0, collar_length / 2.0) * Rot(0, 0, angle) * Box(knurl_height, knurl_width, collar_length)
    result = result + knurl

for i in range(spline_count):
    angle = i * 360.0 / spline_count
    spline = Pos(inner_radius + spline_depth / 2.0, 0, 0) * Rot(0, 0, angle) * Box(spline_depth, spline_width, collar_length)
    result = result - spline

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "knurled_collar_with_spline"
export_step(part, "output.step")