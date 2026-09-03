from build123d import *

plate_width = 50.0
plate_height = 50.0
plate_thickness = 8.0
hole_diameter = 12.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter/2, plate_thickness * 2)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_hole_and_chamfer"
export_step(part, "output.step")