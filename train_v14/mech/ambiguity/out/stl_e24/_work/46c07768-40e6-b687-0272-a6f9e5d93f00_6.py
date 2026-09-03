from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
slot_width = 20.0
slot_height = 30.0
slot_radius = slot_width / 2.0
hole_diameter = 10.0
hole_spacing = 60.0
counterbore_diameter = 16.0
counterbore_depth = 2.0
rib_width = 5.0
rib_height = 3.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_height, slot_width)
    extrude(amount=plate_thickness + 2)
slot_solid = Pos(0, 0, -plate_thickness / 2) * slot_bp.part
base = base - slot_solid

for x in [-hole_spacing / 2, hole_spacing / 2]:
    base = base - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness + 2)
    base = base - Pos(x, 0, plate_thickness / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

rib = Pos(0, 0, -plate_thickness / 2 + rib_height / 2) * Box(plate_length, rib_width, rib_height)
base = base + rib

part = base
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")