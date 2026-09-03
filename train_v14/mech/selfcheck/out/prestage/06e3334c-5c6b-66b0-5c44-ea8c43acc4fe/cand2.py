from build123d import *
import math

plate_side = 55.0
plate_thickness = 10.0
rib_height = 3.0
rib_side = 30.0
hole_diameter = 12.0
chamfer_size = 1.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(plate_side, 3)
    extrude(amount=plate_thickness)
base = p.part

base = base - Cylinder(hole_diameter/2, plate_thickness * 2)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as p2:
    with BuildSketch() as s2:
        RegularPolygon(rib_side, 3)
    extrude(amount=rib_height)
rib = Pos(0, 0, plate_thickness) * p2.part

rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius)

part = base + rib
part.name = "triangular_plate_with_rib"
export_step(part, "output.step")