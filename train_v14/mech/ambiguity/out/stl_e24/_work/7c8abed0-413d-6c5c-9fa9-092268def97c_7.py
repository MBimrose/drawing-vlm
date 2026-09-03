from build123d import *

length = 80.0
width = 30.0
height = 20.0
wall_thickness = 3.0
groove_width = 12.0
groove_depth = 4.0
groove_length = 60.0
hole_diameter = 9.0
hole_spacing = 25.0
chamfer_size = 2.0
rib_thickness = 2.0
rib_width = 2.0
rib_height = 5.0
rib_spacing = 10.0

solid_body = Box(length, width, height)

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
bottom_edges = bottom_face.edges().filter_by(Axis.Z)
solid_body = chamfer(bottom_edges, chamfer_size)

groove = Pos(0, 0, -height/2 + groove_depth/2) * Box(groove_length, groove_width, groove_depth)
solid_body = solid_body - groove

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, width + 20)
    solid_body = solid_body - hole

rib1 = Pos(0, -width/2 + wall_thickness + rib_width/2, height/2 + rib_height/2) * Box(rib_thickness, rib_width, rib_height)
rib2 = Pos(0, width/2 - wall_thickness - rib_width/2, height/2 + rib_height/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "chamfered_block_with_groove_holes_and_ribs"
export_step(part, "output.step")