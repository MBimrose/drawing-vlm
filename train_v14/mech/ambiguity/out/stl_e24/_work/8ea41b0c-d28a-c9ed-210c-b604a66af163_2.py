from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
notch_width = 20.0
notch_depth = 10.0
slot_width = 12.0
slot_height = 30.0
hole_diameter = 6.0
hole_spacing = 20.0
rib_width = 8.0
rib_height = 10.0
rib_thickness = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as bl:
            Polyline(
                (-plate_width/2, -plate_height/2),
                (plate_width/2 - notch_depth, -plate_height/2),
                (plate_width/2 - notch_depth, -plate_height/2 + notch_width),
                (plate_width/2, -plate_height/2 + notch_width),
                (plate_width/2, plate_height/2),
                (-plate_width/2, plate_height/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

slot_cut = Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot_cut

hole_positions = [
    (-hole_spacing/2, 0),
    (hole_spacing/2, 0),
    (0, hole_spacing/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
rib2 = Pos(plate_width/2 - rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_notch_slot_holes_ribs"
export_step(part, "output.step")