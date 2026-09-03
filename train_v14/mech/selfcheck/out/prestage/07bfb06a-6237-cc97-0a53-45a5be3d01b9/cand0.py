from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
corner_fillet_radius = 2.0
cutout_width = 30.0
cutout_height = 20.0
slot_length = 20.0
slot_width = 5.0
slot_offset_x = -plate_width/2 + 10.0
slot_offset_y = 0.0
hole_diameter = 4.0
hole_offset_x = 0.0
hole_offset_y = 0.0
rib_thickness = 4.0
rib_height = 10.0
rib_offset = 5.0

base = Box(plate_width, plate_height, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_fillet_radius)

cutout = Box(cutout_width, cutout_height, plate_thickness)
base = base - cutout

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = slot_bp.part
base = base - Pos(slot_offset_x, slot_offset_y, -plate_thickness/2) * slot_solid

hole = Cylinder(hole_diameter/2, plate_thickness)
base = base - Pos(hole_offset_x, hole_offset_y, 0) * hole

rib1 = Pos(-plate_width/2 + rib_offset, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(plate_width/2 - rib_offset, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
base = base + rib1 + rib2

part = base
part.name = "plate_with_cutouts_and_ribs"
export_step(part, "output.step")