from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 30.0
rib_width = 20.0
rib_length = 80.0
rib_draft_angle = 5.0
slot_length = 60.0
slot_width = 10.0
slot_offset = 5.0
hole_diameter = 5.0
hole_edge_distance = 10.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

with BuildPart() as p_rib:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s_rib:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height, taper=rib_draft_angle)
rib = p_rib.part

result = base + rib

slot = Pos(0, slot_offset, plate_thickness + rib_height/2) * Box(slot_length, slot_width, rib_height)
result = result - slot

hole_positions = [
    (-plate_length/2 + hole_edge_distance, -plate_width/2 + hole_edge_distance),
    ( plate_length/2 - hole_edge_distance, -plate_width/2 + hole_edge_distance),
    (-plate_length/2 + hole_edge_distance,  plate_width/2 - hole_edge_distance),
    ( plate_length/2 - hole_edge_distance,  plate_width/2 - hole_edge_distance)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")