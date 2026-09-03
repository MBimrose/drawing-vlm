from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
slot_length = 40.0
slot_width = 10.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 25.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.8
boss_diameter = 20.0
boss_height = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as slot_bp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=-plate_thickness)
solid_body = solid_body - slot_bp.part

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_slot_holes_and_boss"
export_step(part, "output.step")