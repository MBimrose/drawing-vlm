from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
slot_width = 20.0
slot_length = 30.0
hole_diameter = 10.0
hole_offset = 10.0
rib_width = 5.0
rib_height = 3.0
chamfer_distance = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=bracket_thickness * 2)
slot_solid = Pos(0, 0, -bracket_thickness) * sp.part
base = base - slot_solid

hole_positions = [(-bracket_length/2 + hole_offset, 0), (bracket_length/2 - hole_offset, 0)]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

rib = Pos(0, 0, -bracket_thickness/2 + rib_height/2) * Box(bracket_length, rib_width, rib_height)
base = base + rib

pocket1 = Pos(-bracket_length/2 + 15, 0, -bracket_thickness/2 + 1.0) * Box(10, 5, 2.0)
pocket2 = Pos(bracket_length/2 - 15, 0, -bracket_thickness/2 + 1.0) * Box(10, 5, 2.0)
base = base - pocket1 - pocket2

part = base
part.name = "bracket"
export_step(part, "output.step")