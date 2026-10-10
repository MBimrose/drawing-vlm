from build123d import *

# ------------------------------------------------------------------
# Dimensions (mm)
# ------------------------------------------------------------------
plate_size = 80.0          # square flange, 80 x 80
plate_thickness = 15.0     # flange thickness

boss_diameter = 52.5       # central boss outer diameter
boss_height = 60.0         # boss height above the flange

bore_diameter = 30.0       # central through bore

# Four asymmetric through holes (drill size -> finished ream size)
hole_bl = (9.2, 11.0)      # bottom-left   (drill, ream)
hole_br = (9.3, 11.0)      # bottom-right
hole_tl = (9.2, 11.0)      # top-left
hole_tr = (8.4, 10.0)      # top-right

# Hole centre positions measured from the part centre
hole_x = 28.3              # 11.7 in from each side edge
hole_y = 28.3

# Edge breaks
corner_chamfer = 5.0       # C5 on the four outer vertical corners
hole_chamfer = 1.2         # C1.2 on the hole rims (top and bottom)
boss_chamfer = 1.2         # C1.2 on the boss top rim

# ------------------------------------------------------------------
# Build
# ------------------------------------------------------------------
with BuildPart() as p:
    # Square flange plate
    with BuildSketch(Plane.XY):
        Rectangle(plate_size, plate_size)
    extrude(amount=plate_thickness)

    # Central cylindrical boss
    with BuildSketch(Plane.XY.offset(plate_thickness)):
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

    # Central through bore
    with BuildSketch(Plane.XY):
        Circle(bore_diameter / 2)
    extrude(amount=plate_thickness + boss_height + 20, mode=Mode.SUBTRACT)

    # Four asymmetric through holes (drilled undersize, then reamed)
    hole_pts = [
        (-hole_x, -hole_y, hole_bl),
        (hole_x, -hole_y, hole_br),
        (-hole_x, hole_y, hole_tl),
        (hole_x, hole_y, hole_tr),
    ]
    for hx, hy, (drill_d, ream_d) in hole_pts:
        with Locations((hx, hy, 0)):
            Cylinder(drill_d / 2, plate_thickness + 20, mode=Mode.SUBTRACT)
        with Locations((hx, hy, 0)):
            Cylinder(ream_d / 2, plate_thickness + 20, mode=Mode.SUBTRACT)

    # C5 chamfer on the four outer vertical corners
    corner_edges = p.part.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2] + \
                   p.part.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
    chamfer(corner_edges, corner_chamfer)

    # C1.2 chamfer on the hole rims (top and bottom of each hole)
    hole_rim_edges = [e for e in p.part.edges()
                      if abs(e.center().Z) < 1e-6 or abs(e.center().Z - plate_thickness) < 1e-6]
    chamfer(hole_rim_edges, hole_chamfer)

    # C1.2 chamfer on the boss top rim
    boss_top_edges = p.part.edges().sort_by(Axis.Z)[-1:]
    chamfer(boss_top_edges, boss_chamfer)

part = p.part
export_step(part, "output.step")