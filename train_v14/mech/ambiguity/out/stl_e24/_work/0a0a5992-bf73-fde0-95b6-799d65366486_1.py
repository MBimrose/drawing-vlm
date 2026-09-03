from build123d import *

outer_radius = 40
wall_thickness = 4
inner_radius = outer_radius - wall_thickness
housing_length = 70
flange_width = 40
flange_thickness = 8
flange_hole_dia = 5
flange_hole_spacing = 20
inlet_radius = 6
inlet_depth = 15
inlet_center_z = housing_length/2
chamfer_size = 1

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=housing_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, 0, -flange_thickness) * Box(flange_width, flange_width, flange_thickness)
solid_body = solid_body + flange

for x, y in [(flange_hole_spacing/2, flange_hole_spacing/2), (-flange_hole_spacing/2, flange_hole_spacing/2),
             (-flange_hole_spacing/2, -flange_hole_spacing/2), (flange_hole_spacing/2, -flange_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, -flange_thickness) * Cylinder(flange_hole_dia/2, flange_thickness * 2)

inlet_cyl = Pos(outer_radius - wall_thickness/2, 0, inlet_center_z - housing_length/2) * Rot(0, 90, 0) * Cylinder(inlet_radius, inlet_depth)
solid_body = solid_body - inlet_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "housed_flanged_component"
export_step(part, "output.step")