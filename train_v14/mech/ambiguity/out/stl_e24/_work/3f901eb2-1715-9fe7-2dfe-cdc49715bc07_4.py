from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
hole_diameter = 6.0
hole_offset = 30.0
fillet_radius = 2.0
central_hole_diameter = 4.0
central_cbore_diameter = 16.0
central_cbore_depth = 4.0
notch_width = 10.0
notch_depth = 5.0

solid_body = Box(plate_width, plate_length, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness + boss_height + 1)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - central_cbore_depth/2) * Cylinder(central_cbore_diameter/2, central_cbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for x, y in [(plate_width/2 - notch_width/2, plate_length/2 - notch_depth/2),
             (-plate_width/2 + notch_width/2, plate_length/2 - notch_depth/2),
             (-plate_width/2 + notch_width/2, -plate_length/2 + notch_depth/2),
             (plate_width/2 - notch_width/2, -plate_length/2 + notch_depth/2)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - notch_depth/2) * Box(notch_width, notch_depth, notch_depth)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")