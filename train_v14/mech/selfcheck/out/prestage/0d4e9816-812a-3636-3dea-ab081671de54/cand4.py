from build123d import *
import math

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 10.0
hole_diameter = 4.5
hole_csk_diameter = 8.6
hole_csk_angle = 90
hole_spacing = 50.0
rib_height = 4.0
rib_thickness = 3.0
rib_length = plate_length - 20.0
chamfer_size = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)

slot = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

csk_radius = hole_csk_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_csk_angle / 2))
bore_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    bore = Pos(x, 0, 0) * Cylinder(bore_radius, plate_thickness)
    csk = Pos(x, 0, -plate_thickness/2 + csk_height/2) * Cone(csk_radius, 0, csk_height)
    solid_body = solid_body - bore - csk

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_thickness, rib_height)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")