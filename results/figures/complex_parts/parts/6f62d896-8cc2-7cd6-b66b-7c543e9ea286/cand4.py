from build123d import *

outer_diameter = 74.2
inner_diameter = 30.0
thickness = 10.0
central_hole_diameter = 8.0
counterbore_diameter = 9.0
counterbore_depth = 4.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_size = 0.5
rib_width = 4.0
rib_height = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(central_hole_diameter / 2, thickness)
solid_body = solid_body - Pos(0, 0, thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

keyway_box = Pos(outer_radius - keyway_depth / 2, 0, thickness / 2) * Box(keyway_depth, keyway_width, thickness)
solid_body = solid_body - keyway_box

rib_box = Pos(outer_radius + rib_height / 2, 0, thickness / 2) * Box(rib_height, rib_width, thickness)
solid_body = solid_body + rib_box

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ring_with_keyway_and_rib"
export_step(part, "output.step")