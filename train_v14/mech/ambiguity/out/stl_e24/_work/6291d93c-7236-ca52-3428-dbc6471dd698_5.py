from build123d import *
import math

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
rib_height = 3.0
rib_offset = 2.0
hole_diameter = 4.0
countersink_diameter = 8.0
countersink_angle = 90.0
hole_offset_x = 10.0
hole_offset_y = 10.0
notch_width = 6.0
notch_depth = 8.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

notch = Pos(plate_length/2 - notch_width/2 - 5, plate_width/2 - notch_depth/2, -plate_thickness/2) * Box(notch_width, notch_depth, plate_thickness)
base = base - notch

rib = Pos(0, 0, plate_thickness/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_height)
base = base + rib

csk_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
shaft = Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)
csk_cone = Pos(hole_offset_x, hole_offset_y, plate_thickness/2 - csk_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_depth)
base = base - shaft - csk_cone

part = base
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")