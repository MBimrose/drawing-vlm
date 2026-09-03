from build123d import *

length = 80.0
width = 30.0
height = 20.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 5.0
hole_diameter = 5.0
cbore_diameter = 9.0
cbore_depth = 4.0
hole_spacing = 25.0
chamfer_size = 2.0

solid = Box(length, width, height)

rib1 = Pos(0, width/2 - wall_thickness - rib_thickness/2, height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
rib2 = Pos(0, -(width/2 - wall_thickness - rib_thickness/2), height/2 + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid = solid + rib1 + rib2

for x in [-hole_spacing, 0, hole_spacing]:
    solid = solid - Pos(x, width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, width + 10)
    solid = solid - Pos(x, width/2 - cbore_depth/2, 0) * Rot(90, 0, 0) * Cylinder(cbore_diameter/2, cbore_depth)

bottom_face = solid.faces().sort_by(Axis.Y)[0]
chamfer_edges = bottom_face.edges().filter_by(Axis.Z)
solid = chamfer(chamfer_edges, chamfer_size)

part = solid
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")