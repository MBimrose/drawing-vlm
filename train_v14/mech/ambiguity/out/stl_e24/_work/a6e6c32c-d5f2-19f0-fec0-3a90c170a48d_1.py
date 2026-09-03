from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
corner_radius = 6.0
chamfer_size = 0.7
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 10.0
rib_count = 4
hole_diameter = 3.0
cbore_diameter = 5.0
cbore_depth = 2.0
hole_offset_x = 20.0
hole_offset_y = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    y_pos = -plate_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(plate_length/2 + rib_thickness/2, y_pos, plate_thickness/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

shaft_hole = Pos(hole_offset_x, hole_offset_y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
cbore_hole = Pos(hole_offset_x, hole_offset_y, plate_thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
solid_body = solid_body - shaft_hole - cbore_hole

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")