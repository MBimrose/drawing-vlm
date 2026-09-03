from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 4.0
hole_diameter = 5.0
hole_offset = 12.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
slot_width = 5.0
slot_length = 20.0
slot_offset_from_edge = 15.0
rib_width = 5.0
rib_length = 30.0
rib_height = 3.0
boss_diameter = 20.0
boss_height = 4.0
chamfer_distance = 0.5

solid = Box(plate_length, plate_width, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_fillet_radius)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
    solid = solid - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

slot_center_x = -plate_length/2 + slot_offset_from_edge
solid = solid - Pos(slot_center_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)

solid = solid + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid = solid + Pos(0, 0, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_distance)

part = solid
part.name = "plate_with_features"
export_step(part, "output.step")