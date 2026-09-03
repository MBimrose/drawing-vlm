from build123d import *

outer_diameter = 80
inner_diameter = 60
length = 70
wall_thickness = (outer_diameter - inner_diameter) / 2
pocket_width = 20
pocket_depth = 15
pocket_offset = 30
fillet_radius = 2
hole_diameter = 5
hole_spacing = 30
rib_width = 10
rib_height = 20
rib_thickness = 5
relief_width = 30
relief_depth = 10
relief_offset = 10

solid_body = Cylinder(outer_diameter / 2, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(inner_diameter / 2 - rib_thickness / 2, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(outer_diameter / 2 - pocket_depth / 2, 0, pocket_offset - length / 2) * Box(pocket_depth, pocket_width, pocket_depth)
pocket = fillet(pocket.edges(), fillet_radius)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing / 2, 0), (hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, length / 2) * Cylinder(hole_diameter / 2, length)

relief = Pos(0, 0, length - relief_offset - relief_depth / 2) * Box(relief_width, relief_depth, relief_depth)
solid_body = solid_body - relief

part = solid_body
part.name = "hollow_cylinder_with_rib_pocket_holes_relief"
export_step(part, "output.step")