from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
housing_length = 60.0
flange_thickness = 12.0
flange_diameter = 45.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
rib_width = 6.0
rib_height = 8.0
rib_thickness = 4.0
rib_count = 12
slot_width = 10.0
slot_height = 20.0
slot_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
flange_radius = flange_diameter / 2.0

result = Cylinder(outer_radius, housing_length)
result = result - Cylinder(inner_radius, housing_length)
result = result - Pos(0, 0, housing_length/2 - flange_thickness/2) * Cylinder(flange_radius, flange_thickness)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, housing_length)

result = result - Pos(0, 0, housing_length/2 - slot_depth/2) * Box(slot_width, slot_height, slot_depth)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

part = result
part.name = "housing_with_flange_and_ribs"
export_step(part, "output.step")