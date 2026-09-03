from build123d import *

outer_radius = 25.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 60.0
lip_height = 5.0
lip_thickness = 2.0
fillet_radius = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 12.0
draft_angle = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length, taper=draft_angle)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

lip = Pos(0, 0, length + lip_height/2) * Cylinder(outer_radius + lip_thickness, lip_height)
solid_body = solid_body + lip

solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, (length + lip_height)/2) * Cylinder(mount_hole_diameter/2, length + lip_height + 10)

part = solid_body
part.name = "drafted_cup_with_lip"
export_step(part, "output.step")