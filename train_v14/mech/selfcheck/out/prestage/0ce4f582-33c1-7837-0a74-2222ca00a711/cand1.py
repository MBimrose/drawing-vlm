from build123d import *

outer_diameter = 80.0
pulley_thickness = 20.0
rib_width = 10.0
rib_length = 30.0
rib_height = 5.0
hole_diameter = 8.5
hole_spacing = 20.0
counterbore_diameter = 13.0
counterbore_depth = 4.0
chamfer_size = 0.8
side_cut_width = 12.0
side_cut_depth = 6.0

base = Cylinder(outer_diameter / 2, pulley_thickness)
rib = Box(rib_width, rib_length, rib_height)
solid_body = base + rib

for x, y in [(-hole_spacing / 2, 0), (hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, pulley_thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, pulley_thickness / 2) * Cylinder(hole_diameter / 2, pulley_thickness + 1)

for x, y in [(-outer_diameter / 2, 0), (outer_diameter / 2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Box(side_cut_width, side_cut_depth, pulley_thickness + 1)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "pulley"
export_step(part, "output.step")