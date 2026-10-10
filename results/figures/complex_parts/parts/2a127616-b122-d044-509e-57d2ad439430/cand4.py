from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
shaft_radius = 10.0
shaft_length = 30.0
rib_width = 5.0
rib_height = 8.0
rib_count = 12
chamfer_size = 1.0

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)
result = result + Pos(0, 0, -length/2 - shaft_length/2) * Cylinder(shaft_radius, shaft_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_width/2, 0, 0) * Box(rib_width, rib_height, length)
    result = result + rib

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_shaft_and_ribs"
export_step(part, "output.step")