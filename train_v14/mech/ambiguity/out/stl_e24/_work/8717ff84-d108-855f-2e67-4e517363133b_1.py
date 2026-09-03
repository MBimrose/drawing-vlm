from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
gusset_height = 30.0
gusset_base = 20.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset_x = -plate_length/2 + 10.0
fillet_radius = 1.0
slot_width = 6.0
slot_length = plate_length - 20.0
slot_offset_y = plate_width/4

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_length/2, -plate_width/2),
                (plate_length/2 - gusset_base, -plate_width/2),
                (plate_length/2, 0),
                (plate_length/2 - gusset_base, plate_width/2),
                (-plate_length/2, plate_width/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(hole_offset_x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(0, slot_offset_y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

part = solid_body
part.name = "gusset_plate"
export_step(part, "output.step")