from build123d import *

outer_diameter = 80
inner_diameter = 60
housing_length = 70
wall_thickness = (outer_diameter - inner_diameter) / 2
pocket_width = 30
pocket_height = 20
pocket_depth = 10
pocket_offset = 15
mount_hole_diameter = 5
mount_hole_spacing = 40
tab_width = 20
tab_height = 10
tab_thickness = 5
rib_thickness = 3
rib_height = 15
rib_spacing = 20

outer_radius = outer_diameter / 2
inner_radius = inner_diameter / 2

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=housing_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(outer_radius - pocket_depth/2, 0, housing_length/2 + pocket_offset) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, housing_length/2) * Cylinder(mount_hole_diameter/2, housing_length)

tab = Pos(inner_radius + tab_thickness/2, 0, housing_length/2) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab

solid_body = solid_body - Pos(inner_radius + tab_thickness/2, 0, housing_length/2 + tab_height/2) * Cylinder(mount_hole_diameter/2, tab_height)

rib = Pos(inner_radius - rib_thickness/2, 0, housing_length/2) * Box(rib_thickness, rib_height, housing_length - 2*rib_spacing)
solid_body = solid_body + rib

part = solid_body
part.name = "housing_with_pocket_and_rib"
export_step(part, "output.step")