from build123d import *
import math

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
rib_height = 4.0
rib_width = 6.0
rib_length = plate_length - 20.0
slot_length = 30.0
slot_width = 6.0
hole_diameter = 4.5
hole_spacing = 50.0
countersink_diameter = 8.6
countersink_angle = 90.0
chamfer_size = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, plate_width/2 - rib_width/2, 0) * Box(rib_length, rib_width, rib_height)
solid_body = base + rib

slot = Box(slot_length, slot_width, plate_thickness + 2)
solid_body = solid_body - slot

csk_radius = countersink_diameter / 2
csk_height = csk_radius / math.tan(math.radians(countersink_angle / 2))
hole_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    cyl = Pos(x, 0, 0) * Cylinder(hole_radius, plate_thickness + 2)
    cone = Pos(x, 0, -plate_thickness/2 + csk_height/2) * Cone(csk_radius, 0, csk_height)
    solid_body = solid_body - (cyl + cone)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_rib_slot_and_holes"
export_step(part, "output.step")