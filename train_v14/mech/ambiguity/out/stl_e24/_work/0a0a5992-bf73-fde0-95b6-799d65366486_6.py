from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
length = 70.0
flange_width = 40.0
flange_thickness = 8.0
flange_hole_dia = 5.0
flange_hole_offset = 10.0
vent_hole_dia = 12.0
vent_hole_offset_z = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

hole_positions = [
    (flange_width/2 - flange_hole_offset, flange_width/2 - flange_hole_offset),
    (-flange_width/2 + flange_hole_offset, flange_width/2 - flange_hole_offset),
    (-flange_width/2 + flange_hole_offset, -flange_width/2 + flange_hole_offset),
    (flange_width/2 - flange_hole_offset, -flange_width/2 + flange_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, -flange_thickness) * Cylinder(flange_hole_dia/2, flange_thickness * 2)

vent_cyl = Pos(outer_radius, 0, vent_hole_offset_z) * Rot(0, 90, 0) * Cylinder(vent_hole_dia/2, outer_diameter * 2)
solid_body = solid_body - vent_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")