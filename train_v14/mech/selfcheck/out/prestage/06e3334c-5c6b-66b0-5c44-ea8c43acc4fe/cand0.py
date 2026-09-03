from build123d import *
import math

triangle_side = 80.0
plate_thickness = 10.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 12.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(triangle_side, 3)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter/2, plate_thickness * 2)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

with BuildPart() as rib_p:
    with BuildSketch() as rs:
        RegularPolygon(triangle_side + 2*rib_width, 3)
    extrude(amount=rib_height)

rib_solid = rib_p.part
rib_solid = Pos(0, 0, plate_thickness) * rib_solid
rib_vertical_edges = rib_solid.edges().filter_by(Axis.Z)
rib_solid = fillet(rib_vertical_edges, fillet_radius)

part = solid_body + rib_solid
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")