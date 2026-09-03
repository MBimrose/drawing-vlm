from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 60.0
wall_thickness = 5.0
bore_radius = 8.0
bore_depth = 45.0
countersink_angle = 60.0
countersink_depth = 10.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_height = 15.0
rib_thickness = 4.0

countersink_radius = bore_radius + countersink_depth * math.tan(math.radians(countersink_angle / 2))

result = Box(block_length, block_width, block_height)

bore = Pos(0, 0, block_height/2 - bore_depth/2) * Cylinder(bore_radius, bore_depth)
result = result - bore

csk = Pos(0, 0, block_height/2 - countersink_depth/2) * Cone(bore_radius, countersink_radius, countersink_depth)
result = result - csk

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
    result = result - hole

rib = Pos(-block_length/2 + wall_thickness/2, 0, block_height/2 - rib_height/2) * Box(wall_thickness, rib_thickness, rib_height)
result = result + rib

top_y_face = result.faces().sort_by(Axis.Y)[-1]
vertical_edges = top_y_face.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_distance)

part = result
part.name = "block_with_bore_and_mounts"
export_step(part, "output.step")