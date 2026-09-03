from build123d import *
import math

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
boss_diameter = 10.0
boss_height = 4.0
hole_diameter = 4.0
countersink_diameter = 6.0
countersink_angle = 82.0
hole_spacing = 18.0
hole_offset_from_end = 18.0
chamfer_size = 0.5
notch_width = 10.0
notch_depth = 8.0
notch_offset = 12.0
pocket_width = 12.0
pocket_depth = 6.0

solid_body = Box(jaw_length, jaw_width, jaw_thickness)
solid_body = solid_body + Pos(0, 0, jaw_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

notch_x = -jaw_length/2 + notch_offset
notch_y = -jaw_width/2 + notch_depth/2
solid_body = solid_body - Pos(notch_x, notch_y, 0) * Box(notch_width, notch_depth, jaw_thickness)

pocket_x = jaw_length/2 - pocket_depth/2
pocket_y = jaw_width/2 - pocket_width/2
solid_body = solid_body - Pos(pocket_x, pocket_y, 0) * Box(pocket_depth, pocket_width, jaw_thickness)

for i in range(3):
    hx = -jaw_length/2 + hole_offset_from_end + i * hole_spacing
    solid_body = solid_body - Pos(hx, 0, jaw_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, jaw_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "jaw_with_boss_and_holes"
export_step(part, "output.step")