from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
housing_length = 60.0
groove_width = 10.0
groove_depth = 5.0
chamfer_size = 1.5
mount_hole_diameter = 6.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 15.0
rib_width = 8.0
rib_height = 5.0
rib_thickness = 2.0
rib_count = 12

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
groove_radius = inner_radius + groove_depth

result = Cylinder(outer_radius, housing_length) - Cylinder(inner_radius, housing_length)

groove = Pos(0, 0, housing_length/2 - groove_width/2) * Cylinder(groove_radius, groove_width)
result = result - groove

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, housing_length)

rib = Pos(outer_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

result = result + ribs

part = result
part.name = "housing_with_ribs"
export_step(part, "output.step")