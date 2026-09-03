from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
corner_radius = 6.0
chamfer_size = 0.7
hole_diameter = 3.0
hole_cbore_diameter = 5.0
hole_cbore_depth = 2.0
hole_offset_x = 20.0
hole_offset_y = 20.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 10.0
rib_count = 4

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

shaft = Pos(hole_offset_x, hole_offset_y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
cbore = Pos(hole_offset_x, hole_offset_y, plate_thickness - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
solid_body = solid_body - shaft - cbore

for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(plate_width/2 + rib_thickness/2, y_pos, plate_thickness/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_ribs"
export_step(part, "output.step")