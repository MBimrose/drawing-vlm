from build123d import *

outer_radius = 40.0
inner_radius = 30.0
housing_length = 70.0
wall_thickness = outer_radius - inner_radius
relief_width = 12.0
relief_depth = 5.0
relief_position = 35.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=housing_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

relief_box = Pos(outer_radius - relief_depth/2, 0, relief_position + wall_thickness/2) * Box(relief_width, relief_depth, wall_thickness)
solid_body = solid_body - relief_box

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, housing_length/2) * Cylinder(mount_hole_dia/2, housing_length)

rib = Pos(inner_radius - rib_thickness/2, 0, housing_length/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_housing_with_relief"
export_step(part, "output.step")