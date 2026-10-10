from build123d import *

outer_diameter = 60.0
wall_thickness = 5.0
housing_length = 80.0
shaft_diameter = 20.0
shaft_length = 30.0
rib_width = 5.0
rib_height = 8.0
rib_count = 12
keyway_width = 4.0
keyway_depth = 3.0
keyway_length = 20.0
central_hole_diameter = 8.0
counterbore_diameter = 12.0
counterbore_depth = 6.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
shaft_radius = shaft_diameter / 2.0

result = Pos(0, 0, housing_length / 2) * Cylinder(outer_radius, housing_length)
result = result - Pos(0, 0, housing_length / 2) * Cylinder(inner_radius, housing_length)
result = result + Pos(0, 0, -shaft_length / 2) * Cylinder(shaft_radius, shaft_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_height / 2.0, 0, housing_length / 2) * Box(rib_width, rib_height, housing_length)
    result = result + rib

keyway = Pos(shaft_radius - keyway_depth / 2.0, 0, -shaft_length / 2.0 + keyway_length / 2.0) * Box(keyway_width, keyway_depth, keyway_length)
result = result - keyway

result = result - Pos(0, 0, (housing_length - shaft_length) / 2) * Cylinder(central_hole_diameter / 2, housing_length + shaft_length)
result = result - Pos(0, 0, -shaft_length + counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "housing_with_shaft"
export_step(part, "output.step")