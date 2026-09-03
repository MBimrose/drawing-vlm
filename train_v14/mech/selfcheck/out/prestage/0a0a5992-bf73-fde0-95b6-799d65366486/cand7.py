from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
body_length = 70.0
flange_width = 40.0
flange_thickness = 10.0
vent_diameter = 12.0
vent_offset = 20.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=body_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

vent = Pos(outer_radius, 0, vent_offset) * Rot(0, 90, 0) * Cylinder(vent_diameter / 2, outer_diameter * 2)
solid_body = solid_body - vent

for dx in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    for dy in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
        hole = Pos(dx, dy, -flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 2)
        solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")