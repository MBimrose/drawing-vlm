from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 20.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 5.0
hole_diameter = 9.0
hole_spacing = 25.0
chamfer_distance = 2.0
rib_thickness = 2.0
rib_height = 5.0
rib_offset = 12.0

solid = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, block_width)
    solid = solid - hole

front_face = solid.faces().sort_by(Axis.Y)[0]
chamfer_edges = front_face.edges().filter_by(Axis.Z)
solid = chamfer(chamfer_edges, chamfer_distance)

rib1 = Pos(0, -rib_offset, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
rib2 = Pos(0, rib_offset, block_height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid = solid + rib1 + rib2

part = solid
part.name = "block_with_pocket_holes_ribs"
export_step(part, "output.step")