from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 12.0
leg_width = 12.0
inner_fillet_radius = 2.0
through_hole_diameter = 6.0
through_hole_offset_x = 30.0
through_hole_offset_y = 6.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0
mount_hole_count = 3
mount_hole_start_y = 15.0

vertical = Pos(leg_width/2, vertical_leg_length/2, leg_thickness/2) * Box(leg_width, vertical_leg_length, leg_thickness)
horizontal = Pos(horizontal_leg_length/2, leg_width/2, leg_thickness/2) * Box(horizontal_leg_length, leg_width, leg_thickness)
result = vertical + horizontal

inner_edges = [e for e in result.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3]
result = fillet(inner_edges, inner_fillet_radius)

result = result - Pos(through_hole_offset_x, through_hole_offset_y, leg_thickness/2) * Cylinder(through_hole_diameter/2, leg_thickness)

for i in range(mount_hole_count):
    y = mount_hole_start_y + i * mount_hole_spacing
    result = result - Pos(leg_width/2, y, leg_thickness/2) * Cylinder(mount_hole_diameter/2, leg_thickness)

part = result
part.name = "L_bracket"
export_step(part, "output.step")