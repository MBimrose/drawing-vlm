from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
edge_fillet_radius = 1.0
recess_radius = 15.0
recess_depth = 2.0
hole_diameter = 5.5
hole_circle_radius = 25.0
hole_count = 6
rib_width = 6.0
rib_height = 4.0
rib_offset = 10.0
slot_width = 8.0
slot_length = 30.0
slot_depth = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

solid_body = solid_body - Pos(0, 0, -plate_thickness/2 + recess_depth/2) * Cylinder(recess_radius, recess_depth)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2*rib_offset, rib_height)
rib2 = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

slot1 = Pos(0, 0, -plate_thickness/2 + slot_depth/2) * Box(slot_width, slot_length, slot_depth)
slot2 = Pos(0, 0, -plate_thickness/2 + slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot1 - slot2

part = solid_body
part.name = "plate_with_recess_holes_ribs_slots"
export_step(part, "output.step")