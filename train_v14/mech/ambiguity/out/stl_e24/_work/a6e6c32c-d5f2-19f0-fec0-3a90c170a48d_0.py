from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
corner_fillet_radius = 6.0
chamfer_distance = 0.7
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
hole_diameter = 3.0
cbore_diameter = 5.0
cbore_depth = 2.0
hole_offset_x = 20.0
hole_offset_y = 20.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 12.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

cbore = Pos(hole_offset_x, hole_offset_y, plate_thickness/2 - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
shaft = Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)
solid_body = solid_body - cbore - shaft

rib_count = int((plate_width - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -plate_width/2 + rib_spacing + i * rib_spacing
    rib = Pos(plate_length/2 + rib_thickness/2, y_pos, 0) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_hole_and_ribs"
export_step(part, "output.step")