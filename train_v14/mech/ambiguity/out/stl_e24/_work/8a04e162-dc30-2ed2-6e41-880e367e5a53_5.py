from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
corner_fillet_radius = 2.0
slot_length = 15.0
slot_width = 3.0
slot_spacing = 20.0
num_slots = 3
slot_chamfer = 0.5
mount_hole_diameter = 6.0
rib_height = 4.0
rib_thickness = 2.0
rib_offset = 5.0

solid = Box(bracket_length, bracket_width, bracket_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_fillet_radius)
solid = solid - Cylinder(mount_hole_diameter/2, bracket_thickness)

slot_y = bracket_width/2 - slot_width/2 - 5
for i in range(num_slots):
    x = (i - (num_slots-1)/2) * slot_spacing
    solid = solid - Pos(x, slot_y, 0) * Box(slot_length, slot_width, bracket_thickness)

solid = chamfer(solid.edges().filter_by(Axis.Z), slot_chamfer)

rib = Pos(0, -bracket_width/2 - rib_height/2, 0) * Box(bracket_length - 2*rib_offset, rib_height, rib_thickness)
solid = solid + rib

part = solid
part.name = "bracket"
export_step(part, "output.step")