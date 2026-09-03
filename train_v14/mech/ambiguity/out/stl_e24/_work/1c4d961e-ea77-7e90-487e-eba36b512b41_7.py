from build123d import *

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
rib_thickness = 5.0
rib_height = 5.0
chamfer_size = 2.0
hole_diameter = 12.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

solid_body = Box(outer_width, outer_depth, outer_height)
solid_body = solid_body - Box(inner_width, inner_depth, outer_height)
solid_body = solid_body - Cylinder(hole_diameter / 2, outer_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, 0, outer_height / 2 - rib_height / 2) * Box(inner_width, rib_thickness, rib_height)
rib2 = Pos(0, 0, outer_height / 2 - rib_height / 2) * Box(rib_thickness, inner_depth, rib_height)

part = solid_body + rib1 + rib2
part.name = "XMountSocket"
export_step(part, "output.step")