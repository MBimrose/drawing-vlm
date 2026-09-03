from build123d import *

outer_size = 80.0
wall_thickness = 5.0
opening_width = 40.0
opening_height = 30.0
chamfer_size = 1.5
mount_hole_diameter = 3.0
mount_hole_offset = 32.0

solid_body = Box(outer_size, outer_size, outer_size)
inner = Box(outer_size - 2*wall_thickness, outer_size - 2*wall_thickness, outer_size - 2*wall_thickness)
solid_body = solid_body - inner

opening = Box(opening_width, wall_thickness, opening_height)
opening = Pos(0, outer_size/2 - wall_thickness/2, 0) * opening
solid_body = solid_body - opening

hole_r = mount_hole_diameter / 2
for x, y in [(-mount_hole_offset, 0), (mount_hole_offset, 0), (0, -mount_hole_offset), (0, mount_hole_offset)]:
    hole = Cylinder(hole_r, wall_thickness + 1)
    hole = Pos(x, y, outer_size/2 - wall_thickness/2) * hole
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_opening"
export_step(part, "output.step")