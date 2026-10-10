from build123d import *
import math

hub_base_width = 20.0
hub_base_depth = 10.0
hub_base_height = 8.0
hub_top_diameter = 80.0
hub_cone_height = 30.0
rim_height = 8.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 30.0
hole_diameter = 5.0
hole_pattern_radius = 30.0
hole_count = 6
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(hub_base_width, hub_base_depth)
    with BuildSketch(Plane.XY.offset(hub_base_height + hub_cone_height)) as s2:
        Circle(hub_top_diameter / 2)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, hub_base_height + hub_cone_height + rim_height / 2) * Cylinder(hub_top_diameter / 2, rim_height)
solid_body = solid_body - Pos(hub_base_width / 2 - keyway_depth / 2, 0, hub_base_height / 2) * Box(keyway_depth, keyway_length, keyway_width)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, hub_base_height + hub_cone_height + rim_height / 2) * Cylinder(hole_diameter / 2, rim_height + hub_cone_height + hub_base_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "hub_with_rim_and_keyway"
export_step(part, "output.step")