from build123d import *

plate_width = 60.0
plate_depth = 60.0
plate_thickness = 8.0
chamfer_size = 2.0
hole_diameter = 10.0
slot_length = 30.0
slot_width = 10.0
rib_height = 4.0
rib_width = 6.0
rib_offset = 5.0

solid = Box(plate_width, plate_depth, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)
solid = solid - Cylinder(hole_diameter/2, plate_thickness)
solid = solid - Box(slot_length, slot_width, plate_thickness)
rib = Box(rib_width, rib_width, rib_height)
solid = solid + Pos(plate_width/2 + rib_width/2, 0, 0) * rib
solid = solid + Pos(-plate_width/2 - rib_width/2, 0, 0) * rib

part = solid
part.name = "plate_with_ribs"
export_step(part, "output.step")