from build123d import *
import math

hub_radius = 15.0
hub_thickness = 10.0
shaft_length = 70.0
shaft_radius_start = 12.0
shaft_radius_end = 5.0
twist_degrees = 30.0
chamfer_size = 1.0
keyway_width = 4.0
keyway_depth = 6.0
center_hole_diameter = 4.0

hub = Cylinder(hub_radius, hub_thickness)
hub = hub - Cylinder(center_hole_diameter / 2, hub_thickness)
keyway = Pos(hub_radius - keyway_depth / 2, 0, 0) * Box(keyway_depth, keyway_width, hub_thickness)
hub = hub - keyway
hub = chamfer(hub.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(shaft_radius_start)
    with BuildSketch(Plane.XY.offset(shaft_length).rotated((0, 0, twist_degrees))) as s2:
        Circle(shaft_radius_end)
    loft()
shaft = p.part

part = hub + shaft
part.name = "twisted_shaft_hub"
export_step(part, "output.step")