from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
length = 70.0
flange_width = 40.0
flange_thickness = 12.0
mount_hole_dia = 5.0
mount_hole_spacing = 20.0
port_diameter = 12.0
port_offset_from_base = 15.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness/2) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

hole_positions = [
    (mount_hole_spacing/2, mount_hole_spacing/2),
    (-mount_hole_spacing/2, mount_hole_spacing/2),
    (-mount_hole_spacing/2, -mount_hole_spacing/2),
    (mount_hole_spacing/2, -mount_hole_spacing/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, -flange_thickness/2) * Cylinder(mount_hole_dia/2, flange_thickness)

port = Pos(outer_radius, 0, port_offset_from_base) * Rot(0, 90, 0) * Cylinder(port_diameter/2, outer_diameter)
solid_body = solid_body - port

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")