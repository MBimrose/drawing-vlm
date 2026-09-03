from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 20.0
rib_height = 4.0
rib_width = 6.0
hole_diameter = 8.5
hole_spacing = 20.0
counterbore_diameter = 13.0
counterbore_depth = 4.0
slot_width = 6.0
slot_length = 30.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_inner_radius = inner_radius
rib_outer_radius = inner_radius + rib_width

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

rib = Cylinder(rib_outer_radius, thickness) - Cylinder(rib_inner_radius, thickness)
solid_body = solid_body + rib

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, thickness) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - Pos(x, y, thickness) * Cylinder(counterbore_diameter/2, counterbore_depth)

slot_box = Box(slot_width, slot_length, thickness)
solid_body = solid_body - Pos(outer_radius - slot_width/2, 0, thickness/2) * slot_box
solid_body = solid_body - Pos(-outer_radius + slot_width/2, 0, thickness/2) * slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "flanged_disc_with_rib"
export_step(part, "output.step")