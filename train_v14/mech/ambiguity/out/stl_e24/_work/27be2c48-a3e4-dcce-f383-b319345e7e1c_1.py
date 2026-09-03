from build123d import *

outer_diameter = 80.0
wall_thickness = 10.0
length = 70.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 15.0
fillet_radius = 2.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0
hole_diameter = 5.0
hole_spacing = 25.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket_box = Pos(outer_radius - pocket_depth/2, 0, pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

rib_box = Pos(inner_radius - rib_thickness/2, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib_box

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, length/2) * Cylinder(hole_diameter/2, length)

part = solid_body
part.name = "hollow_cylinder_with_pocket_rib_holes"
export_step(part, "output.step")