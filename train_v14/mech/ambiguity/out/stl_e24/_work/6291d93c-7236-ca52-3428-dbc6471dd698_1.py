from build123d import *
import math

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
rib_height = 1.5
rib_offset = 2.0
slot_width = 6.0
slot_length = 10.0
slot_offset_x = 12.0
slot_offset_y = 12.0
hole_diameter = 4.0
hole_csk_diameter = 8.0
hole_csk_angle = 90.0
hole_depth = base_thickness + rib_height
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_size = 1.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_length - 2*rib_offset, base_width - 2*rib_offset, rib_height)
base = base + rib

slot = Pos(slot_offset_x, base_width/2 - slot_length/2, 0) * Box(slot_width, slot_length, base_thickness)
base = base - slot

csk_radius = hole_csk_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_csk_angle / 2))
shaft = Pos(hole_offset_x, hole_offset_y, base_thickness + rib_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
csk = Pos(hole_offset_x, hole_offset_y, base_thickness + rib_height - csk_height/2) * Cone(0, csk_radius, csk_height)
base = base - shaft - csk

top_face = base.faces().sort_by(Axis.Z)[-1]
base = chamfer(top_face.edges(), chamfer_size)

part = base
part.name = "base_plate_with_rib"
export_step(part, "output.step")