from build123d import *

jaw_length = 80
jaw_height = 25
jaw_thickness = 8
rib_width = 4
rib_height = 6
rib_spacing = 10
rib_depth = 3
hole_diameter = 5
hole_offset = 8
fillet_radius = 2

solid_body = Box(jaw_length, jaw_thickness, jaw_height)

cutout = Pos(0, 0, -jaw_thickness/2) * Box(jaw_length/2, jaw_thickness, jaw_height/2)
solid_body = solid_body - cutout

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib_count = int((jaw_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -jaw_length/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, jaw_thickness/2 + rib_height/2, jaw_thickness/2) * Box(rib_width, rib_height, rib_depth)
    solid_body = solid_body + rib

for z_off in [jaw_height/2 - hole_offset, -jaw_height/2 + hole_offset]:
    hole = Pos(jaw_length/2 - jaw_thickness/2, 0, z_off) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, jaw_thickness)
    solid_body = solid_body - hole

for z_off in [jaw_height/2 - hole_offset, -jaw_height/2 + hole_offset]:
    hole = Pos(-jaw_length/2 + jaw_thickness/2, 0, z_off) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, jaw_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "jaw_with_ribs_and_holes"
export_step(part, "output.step")