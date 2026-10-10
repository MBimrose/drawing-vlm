from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
pocket_diameter = 30.0
pocket_depth = 10.0
chamfer_size = 1.0
rib_count = 6
rib_thickness = 2.0
rib_width = 2.0
rib_height = 8.0
slot_width = 2.0
slot_depth = 1.0
slot_length = 30.0
mount_hole_diameter = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

pocket = Pos(0, 0, height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

slot = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot

mount_hole = Pos(0, 0, height/2) * Cylinder(mount_hole_diameter/2, height + 10)
solid_body = solid_body - mount_hole

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")