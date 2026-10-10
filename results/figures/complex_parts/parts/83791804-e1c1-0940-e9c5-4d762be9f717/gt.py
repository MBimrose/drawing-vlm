from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
perforation_hole_diameter = 5.0
perforation_spacing = 12.0
mounting_hole_diameter = 6.0
mounting_hole_offset = 8.0
gusset_length = 28.0
gusset_thickness = 4.0

solid_body = Box(plate_width, plate_thickness, plate_height)

solid_body = solid_body - Rot(90, 0, 0) * Cylinder(central_hole_diameter/2, plate_thickness)

num_x = max(1, int((plate_width - 2 * mounting_hole_offset) / perforation_spacing))
num_y = max(1, int((plate_height - 2 * mounting_hole_offset) / perforation_spacing))
for i in range(num_x):
    for j in range(num_y):
        x = (i - (num_x - 1) / 2) * perforation_spacing
        z = (j - (num_y - 1) / 2) * perforation_spacing
        solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(perforation_hole_diameter/2, plate_thickness)

for x, z in [(-plate_width/2 + mounting_hole_offset, 0), (plate_width/2 - mounting_hole_offset, 0)]:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mounting_hole_diameter/2, plate_thickness)

left_gusset = Pos(-plate_width/2 - gusset_thickness/2, -plate_height/4, 0) * Box(gusset_thickness, gusset_thickness, gusset_length)
right_gusset = Pos(plate_width/2 + gusset_thickness/2, -plate_height/4, 0) * Box(gusset_thickness, gusset_thickness, gusset_length)

solid_body = solid_body + left_gusset + right_gusset

part = solid_body
part.name = "perforated_plate_with_gussets"
export_step(part, OUTPUT_PATH)