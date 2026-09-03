from build123d import *

vertical_height = 70.0
horizontal_length = 80.0
leg_width = 20.0
thickness = 8.0
gusset_height = 30.0
gusset_thickness = 3.0
hole_diameter = 5.0
chamfer_size = 1.0

vertical = Pos(leg_width/2, vertical_height/2, thickness/2) * Box(leg_width, vertical_height, thickness)
horizontal = Pos(horizontal_length/2, leg_width/2, thickness/2) * Box(horizontal_length, leg_width, thickness)
base = vertical + horizontal

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((leg_width, leg_width), (leg_width + gusset_height, leg_width), (leg_width, leg_width + gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)
gusset = g.part

result = base + gusset

result = result - Pos(leg_width/2, vertical_height/2, thickness/2) * Cylinder(hole_diameter/2, thickness)
result = result - Pos(horizontal_length/2, leg_width/2, thickness/2) * Cylinder(hole_diameter/2, thickness)

result = chamfer(result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1], chamfer_size)
result = chamfer(result.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:1], chamfer_size)

part = result
part.name = "L_Bracket"
export_step(part, "output.step")