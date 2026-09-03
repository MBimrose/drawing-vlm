from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
slot_width = 12.0
slot_length = 30.0
hole_diameter = 6.0
hole_spacing = 20.0
chamfer_size = 0.8
rib_width = 6.0
rib_length = 10.0
rib_height = 5.0
rib_offset = 15.0
notch_width = 10.0
notch_depth = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

# Cut slot through center
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

# Cut notch on top edge at right end
notch_x = plate_length/2 - plate_thickness/2
notch_y = plate_width/2 - notch_depth/2
solid_body = solid_body - Pos(notch_x, notch_y, plate_thickness/2) * Box(plate_thickness, notch_depth, notch_width)

# Cut 3 holes in triangular pattern
hole_positions = [
    (-hole_spacing/2, 0),
    (hole_spacing/2, 0),
    (0, hole_spacing/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

# Add ribs on bottom face
rib_positions = [
    (-plate_length/2 + rib_offset, 0),
    (plate_length/2 - rib_offset, 0)
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, 0) * Box(rib_width, rib_length, rib_height)

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slot_notch_holes_ribs"
export_step(part, "output.step")