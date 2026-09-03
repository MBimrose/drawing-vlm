from build123d import *

trough_length = 90.0
trough_width = 40.0
trough_height = 30.0
wall_thickness = 3.0
groove_width = 12.0
groove_depth = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_x = 20.0

outer = Pos(0, 0, trough_height/2) * Box(trough_length, trough_width, trough_height)
inner = Pos(0, 0, wall_thickness + (trough_height - wall_thickness)/2) * Box(trough_length - 2*wall_thickness, trough_width - 2*wall_thickness, trough_height - wall_thickness)
base = outer - inner

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-groove_width/2, 0), (0, -groove_depth))
            l2 = Line(l1@1, (groove_width/2, 0))
            l3 = Line(l2@1, (-groove_width/2, 0))
        make_face()
    extrude(amount=trough_length)
groove = gp.part
groove = Pos(0, 0, trough_height - wall_thickness) * groove
base = base - groove

bottom_face = base.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
base = fillet(bottom_edges, fillet_radius)

hole = Pos(hole_offset_x - trough_length/2, -trough_width/2, trough_height) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, trough_width)
base = base - hole

part = base
part.name = "trough"
export_step(part, "output.step")