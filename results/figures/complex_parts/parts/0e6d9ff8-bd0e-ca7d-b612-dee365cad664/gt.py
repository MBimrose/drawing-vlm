from build123d import *
leg_length = 60
leg_width = 20
thickness = 10
corner_radius = 2
pocket_width = 12
pocket_height = 12
pocket_depth = 6
head_hole_diameter = 6
head_countersink_angle = 82
countersink_diameter = 12
chamfer_size = 1
rib_thickness = 2
rib_width = 4
rib_length = 20
mount_hole_diameter = 4
with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)
result = p.part
yf = result.faces().sort_by(Axis.Y)[-1]
yc = yf.center()
result = result + Pos(yc.X, yc.Y + rib_thickness/2, yc.Z) * Box(rib_width, rib_thickness, rib_length)
xf = result.faces().sort_by(Axis.X)[-1]
xc = xf.center()
result = result + Pos(xc.X + rib_thickness/2, xc.Y, xc.Z) * Box(rib_thickness, rib_width, rib_length)
zf = result.faces().sort_by(Axis.Z)[-1]
pocket_center = leg_width / 2
result = result - Pos(pocket_center, pocket_center, zf.center().Z - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
hole_offset_from_end = 15
hole_center_x = -leg_length / 2 + hole_offset_from_end
yf = result.faces().sort_by(Axis.Y)[-1]
yc = yf.center()
result = result - Pos(yc.X + hole_center_x, yc.Y + thickness/2, yc.Z) * Rot(-90, 0, 0) * CounterSinkHole(head_hole_diameter/2, countersink_diameter/2, thickness)
xf = result.faces().sort_by(Axis.X)[-1]
xc = xf.center()
result = result - Pos(xc.X, xc.Y, xc.Z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, 200)
xf = result.faces().sort_by(Axis.X)[-1]
result = chamfer(xf.edges(), chamfer_size)
yf = result.faces().sort_by(Axis.Y)[-1]
result = chamfer(yf.edges(), chamfer_size)
part = result
part.name = "L_bracket_with_ribs"
export_step(part, OUTPUT_PATH)