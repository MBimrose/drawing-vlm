from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
body_length = 70.0
flange_width = 50.0
flange_thickness = 14.0
inlet_diameter = 12.0
inlet_offset = 20.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 2.0

solid_body = Pos(0, 0, body_length/2) * Cylinder(outer_diameter/2, body_length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness/2) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

hole_positions = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, -flange_thickness/2) * Cylinder(mount_hole_diameter/2, flange_thickness + 10)

inlet = Pos(outer_diameter/2, 0, inlet_offset) * Rot(0, 90, 0) * Cylinder(inlet_diameter/2, outer_diameter + 20)
solid_body = solid_body - inlet

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")