from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
slot_width = 10.0
slot_height = 20.0
hole_diameter = 4.0
hole_spacing = 20.0
chamfer_size = 0.5

outer = Box(outer_width, outer_height, length)
inner = Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, length - 2*wall_thickness)
solid_body = outer - inner

slot = Pos(0, outer_height/2 - wall_thickness/2, 0) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot

for i in range(3):
    y_pos = (i - 1) * hole_spacing
    hole = Pos(outer_width/2, y_pos, -length/2 + 10) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 200)
    solid_body = solid_body - hole

x_edges = solid_body.edges().filter_by(Axis.X)
solid_body = chamfer(x_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_slot_and_holes"
export_step(part, "output.step")