from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
end_radius = arm_width / 2.0
slot_width = 6.0
slot_length = 12.0
slot_offset = 4.0
hole_diameter = 7.5
hole_offset = 30.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 3.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_width, arm_length, arm_thickness)
rounded_end = Pos(0, arm_length/2, arm_thickness/2) * Cylinder(end_radius, arm_thickness)
arm_body = base + rounded_end

vertical_edges = arm_body.edges().filter_by(Axis.Z)
arm_body = fillet(vertical_edges, fillet_radius)

slot_center_y = arm_length/2 - slot_offset - slot_width/2
slot_cut = Pos(0, slot_center_y, arm_thickness/2) * Box(slot_length, slot_width, arm_thickness)
arm_body = arm_body - slot_cut

hole_center_y = hole_offset
hole_cut = Pos(0, hole_center_y, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)
arm_body = arm_body - hole_cut

rib = Pos(0, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
arm_body = arm_body + rib

part = arm_body
part.name = "arm_with_rib"
export_step(part, "output.step")