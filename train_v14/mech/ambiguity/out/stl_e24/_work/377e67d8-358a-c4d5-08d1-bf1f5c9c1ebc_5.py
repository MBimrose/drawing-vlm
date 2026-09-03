from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
hole_diameter = 6.0
hole_offset = 10.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
rib_width = 5.0
rib_height = 5.0
chamfer_size = 0.5

solid = Box(plate_length, plate_width, plate_thickness)
solid = solid + Box(rib_width, plate_width - 2 * hole_offset, rib_height)
solid = solid - Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]

for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    solid = solid - Pos(x, y, -plate_thickness/2 + counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "plate_with_rib_slot_holes"
export_step(part, "output.step")