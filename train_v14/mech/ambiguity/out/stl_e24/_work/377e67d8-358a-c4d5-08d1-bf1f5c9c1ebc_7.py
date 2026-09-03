from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
rib_width = 5.0
rib_height = 5.0
hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 3.0
edge_margin = 10.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

slot_cut = Box(slot_width, slot_length, plate_thickness)
solid_body = solid_body - slot_cut

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, slot_length, rib_height)
solid_body = solid_body + rib

hole_positions = [
    (-plate_length/2 + edge_margin, -plate_width/2 + edge_margin),
    ( plate_length/2 - edge_margin, -plate_width/2 + edge_margin),
    ( plate_length/2 - edge_margin,  plate_width/2 - edge_margin),
    (-plate_length/2 + edge_margin,  plate_width/2 - edge_margin)
]

for x, y in hole_positions:
    cbore = Pos(x, y, -plate_thickness/2 + counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    shaft = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)
    solid_body = solid_body - cbore - shaft

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_slot_rib_and_holes"
export_step(part, "output.step")