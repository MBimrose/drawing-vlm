from build123d import *
import math

sleeve_length = 100.0
sleeve_width = 30.0
sleeve_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
rib_width = 10.0
rib_height = 2.0
rib_length = 80.0
rib_offset = (sleeve_length - rib_length) / 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0

outer = Pos(0, 0, sleeve_height/2) * Box(sleeve_length, sleeve_width, sleeve_height)
outer = fillet(outer.edges(), fillet_radius)
inner = Pos(0, 0, sleeve_height/2) * Box(sleeve_length - 2*wall_thickness, sleeve_width - 2*wall_thickness, sleeve_height)
sleeve = outer - inner

x_center = -sleeve_length/2 + wall_thickness + rib_offset + rib_length/2
y_center = -sleeve_width/2 + wall_thickness + rib_width/2
rib = Pos(x_center, y_center, rib_height/2) * Box(rib_length, rib_width, rib_height)
sleeve = sleeve + rib

hole_x = sleeve_length/2 - mount_hole_offset
hole_y = sleeve_width/2 - mount_hole_offset
for hx, hy in [(hole_x, hole_y), (-hole_x, hole_y), (-hole_x, -hole_y), (hole_x, -hole_y)]:
    sleeve = sleeve - Pos(hx, hy, sleeve_height/2) * Cylinder(mount_hole_diameter/2, sleeve_height)

part = sleeve
part.name = "sleeve_with_rib_and_mount_holes"
export_step(part, OUTPUT_PATH)