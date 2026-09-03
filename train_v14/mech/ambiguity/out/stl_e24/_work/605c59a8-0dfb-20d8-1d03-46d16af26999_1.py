from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 30.0
rib_width = 20.0
rib_length = 80.0
rib_draft_angle = 5.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_distance = 0.5

base_plate = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as rib_sk:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height, taper=rib_draft_angle)

rib = rib_bp.part
result = base_plate + rib

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset)
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")