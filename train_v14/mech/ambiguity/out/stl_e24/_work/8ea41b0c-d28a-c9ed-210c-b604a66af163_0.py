from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
notch_width = 10.0
notch_depth = 15.0
hole_diameter = 6.0
hole_spacing = 20.0
chamfer_size = 0.5
rib_width = 6.0
rib_height = 10.0
slot_width = 12.0
slot_length = 30.0
slot_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_width/2, -plate_height/2),
                (plate_width/2, -plate_height/2),
                (plate_width/2, plate_height/2 - notch_depth),
                (plate_width/2 - notch_width, plate_height/2 - notch_depth),
                (plate_width/2 - notch_width, plate_height/2),
                (-plate_width/2, plate_height/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0), (0, hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = solid_body - Pos(slot_offset, 0, 0) * Box(slot_width, slot_length, plate_thickness * 2)

solid_body = solid_body + Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
solid_body = solid_body + Pos(plate_width/2 - rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_notch_holes_slot_ribs"
export_step(part, "output.step")