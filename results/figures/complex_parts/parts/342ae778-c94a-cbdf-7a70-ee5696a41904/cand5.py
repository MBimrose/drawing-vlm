from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
chamfer_size = 1.5
mount_hole_diameter = 6.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
rib_count = 12
rib_width = 8.0
rib_thickness = 4.0
rib_height = 5.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

result = Cylinder(outer_radius, height)
result = result - Cylinder(inner_radius, height)
result = result - Pos(0, 0, height/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
    result = result + rib

pocket = Pos(-outer_radius + pocket_depth/2, 0, height/2 - pocket_height/2) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

part = result
part.name = "cylindrical_housing"
export_step(part, "output.step")