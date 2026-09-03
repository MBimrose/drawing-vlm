from build123d import *
import math

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
rib_width = 12.0
rib_height = 6.0
rib_thickness = 4.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 10.0
hole_diameter = 4.5
hole_head_diameter = 8.6
hole_head_angle = 90
hole_spacing = 50.0
chamfer_size = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
rib = Pos(0, -base_width/2 + rib_width/2 + 5, rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid = base + rib

slot = Pos(0, slot_offset_y, base_thickness/2) * Box(slot_length, slot_width, base_thickness)
solid = solid - slot

csk_radius = hole_head_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_head_angle / 2))
bore_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    bore = Pos(x, 0, base_thickness/2) * Cylinder(bore_radius, base_thickness)
    csk = Pos(x, 0, csk_height/2) * Cone(csk_radius, 0, csk_height)
    solid = solid - (bore + csk)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "WallMountBracket"
export_step(part, "output.step")