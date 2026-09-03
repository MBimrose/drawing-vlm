from build123d import *
import math

bore_diameter = 20.0
outer_diameter = 36.0
collar_length = 30.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 15.0
set_screw_diameter = 2.4
set_screw_offset = 12.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_radius = outer_diameter/2 - 4.0

solid = Cylinder(outer_diameter/2, collar_length) - Cylinder(bore_diameter/2, collar_length)

keyway = Pos(bore_diameter/2 + keyway_depth/2, 0, collar_length/2 - keyway_length/2) * Box(keyway_depth, keyway_width, keyway_length)
solid = solid - keyway

set_screw = Pos(outer_diameter/2 - set_screw_offset, 0, 0) * Cylinder(set_screw_diameter/2, collar_length)
solid = solid - set_screw

for i in range(3):
    angle = math.radians(i * 120)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid = solid - Pos(px, py, collar_length/2) * Cylinder(mount_hole_diameter/2, collar_length + 2)

top_edges = solid.edges().sort_by(Axis.Z)[-1:]
solid = chamfer(top_edges, chamfer_size)

part = solid
part.name = "collar_with_keyway"
export_step(part, "output.step")