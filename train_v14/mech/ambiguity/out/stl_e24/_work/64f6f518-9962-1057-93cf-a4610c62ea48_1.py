from build123d import *

lever_length = 80.0
lever_thickness = 8.0
lever_width = 30.0
pivot_radius = 5.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_spacing = 15.0
num_holes = 3
chamfer_dist = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(pivot_radius)
    with BuildSketch(Plane.XY.offset(lever_width)) as s2:
        Rectangle(lever_length, lever_thickness)
    loft()

solid_body = p.part

slot_box = Pos(lever_length/2 - slot_length/2, 0, 0) * Box(slot_length, slot_width, lever_thickness)
solid_body = solid_body - slot_box

for i in range(num_holes):
    x_pos = -lever_length/2 + hole_spacing + i * hole_spacing
    hole = Pos(x_pos, lever_thickness/2, lever_width/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, lever_thickness)
    solid_body = solid_body - hole

pivot_hole = Pos(0, 0, lever_width/2) * Cylinder(pivot_radius * 0.6, lever_width)
solid_body = solid_body - pivot_hole

part = solid_body
part.name = "lever"
export_step(part, "output.step")