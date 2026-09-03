from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
central_hole_diameter = 10.0
corner_hole_diameter = 5.0
corner_hole_offset = 15.0
slot_width = 20.0
slot_depth = 6.0
rib_width = 6.0
rib_height = 5.0
rib_spacing = 40.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)

base = base - Cylinder(central_hole_diameter/2, plate_thickness)

corner_positions = [
    (corner_hole_offset, corner_hole_offset),
    (-corner_hole_offset, corner_hole_offset),
    (-corner_hole_offset, -corner_hole_offset),
    (corner_hole_offset, -corner_hole_offset),
]
for x, y in corner_positions:
    base = base - Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)

slot = Pos(0, plate_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, plate_thickness)
base = base - slot

with BuildPart() as rib_bp:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_line:
            Polyline((-rib_width/2, 0), (rib_width/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=plate_thickness/2)
rib = rib_bp.part

for x in [-rib_spacing/2, rib_spacing/2]:
    base = base + Pos(x, 0, plate_thickness/2) * rib

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_distance)

part = base
part.name = "plate_with_ribs"
export_step(part, "output.step")