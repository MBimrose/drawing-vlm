from build123d import *

plate_length = 80.0
plate_width = 55.0
plate_thickness = 10.0
gusset_height = 25.0
hole_diameter = 6.0
hole_offset_x = 10.0
hole_offset_y = 15.0
fillet_radius = 1.0
slot_length = 50.0
slot_width = 6.0
slot_offset_x = 40.0
slot_offset_y = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (plate_length - gusset_height, 0), (plate_length, plate_width / 2),
                     (plate_length - gusset_height, plate_width), (0, plate_width), close=True)
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (hole_offset_x, plate_width - hole_offset_y)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

solid_body = solid_body - Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness * 2)

part = solid_body
part.name = "plate_with_gusset"
export_step(part, "output.step")