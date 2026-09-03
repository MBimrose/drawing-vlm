from build123d import *

width = 70.0
depth = 30.0
height = 12.0
wall_thickness = 2.0
rib_width = 8.0
rib_height = 6.0
rib_offset = 10.0
hole_diameter = 4.0
hole_depth = 6.0
fillet_radius = 1.5
chamfer_size = 1.0

base = Pos(0, 0, height/2) * Box(width, depth, height)
rib = Pos(width/2 - rib_offset, 0, height/2) * Box(rib_width, rib_height, height)
solid_body = base + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

hole = Pos(width/2 - hole_depth/2, 0, height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "box_with_rib_and_hole"
export_step(part, "output.step")