from build123d import *
import math

outer_radius = 30
hub_radius = 10
thickness = 12
fillet_radius = 1.5
keyway_width = 15
keyway_depth = 6
hole_diameter = 5
hole_count = 4
hole_radius = outer_radius - 5
rib_width = 3
rib_height = 6
rib_count = 6

solid_body = Cylinder(outer_radius, thickness)

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, fillet_radius)

keyway = Pos(outer_radius - keyway_width/2, 0, 0) * Box(keyway_width, keyway_depth, thickness)
solid_body = solid_body - keyway

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, thickness)

for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_width/2, 0, 0) * Box(rib_width, rib_height, thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "pulley_with_keyway"
export_step(part, "output.step")