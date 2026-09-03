from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
rib_thickness = 2.0
rib_height = 5.0
rib_offset = 12.0
hole_diameter = 9.0
hole_spacing = 25.0
chamfer_distance = 2.0

base = Box(block_length, block_width, block_height)
rib1 = Pos(0, rib_offset, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
rib2 = Pos(0, -rib_offset, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid_body = base + rib1 + rib2

hole_r = hole_diameter / 2
hole_tool = Rot(90, 0, 0) * Cylinder(hole_r, block_width + 10)
for x in [-hole_spacing, 0, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, 0) * hole_tool

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
bottom_edges = bottom_face.edges().filter_by(Axis.Z)
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")