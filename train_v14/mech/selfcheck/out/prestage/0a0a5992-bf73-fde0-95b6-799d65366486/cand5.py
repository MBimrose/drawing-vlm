from build123d import *

outer_diameter = 80.0
wall_thickness = 4.0
height = 70.0
flange_width = 40.0
flange_thickness = 12.0
flange_hole_dia = 5.0
flange_hole_spacing = 20.0
vent_diameter = 12.0
vent_offset_z = 35.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness/2) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

for x, y in [(-flange_hole_spacing/2, -flange_hole_spacing/2),
             (flange_hole_spacing/2, -flange_hole_spacing/2),
             (-flange_hole_spacing/2, flange_hole_spacing/2),
             (flange_hole_spacing/2, flange_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, -flange_thickness/2) * Cylinder(flange_hole_dia/2, flange_thickness)

vent_cyl = Pos(outer_radius - wall_thickness/2, 0, vent_offset_z) * Rot(0, 90, 0) * Cylinder(vent_diameter/2, wall_thickness*2)
solid_body = solid_body - vent_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")