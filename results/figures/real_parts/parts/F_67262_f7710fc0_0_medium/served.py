from build123d import *

# ---- dimensions from drawing ----
leaf_length = 80.0      # overall length of plate
leaf_width = 32.0       # overall width of plate
leaf_thickness = 8.0    # plate thickness (derived: 56 - 24 - 24)

boss_radius = 8.0       # ø16 boss
boss_height = 24.0      # boss projection beyond each face

boss1_x = -leaf_length / 2 + leaf_width / 2   # -16
boss2_x = leaf_length / 2 - leaf_width / 2    # +16

with BuildPart() as p:
    # obround plate, centred on origin
    with BuildSketch() as s:
        SlotOverall(leaf_length, leaf_width)
    extrude(amount=leaf_thickness)

    # boss on +Z face (top)
    with Locations((boss1_x, 0, leaf_thickness)):
        Cylinder(boss_radius, boss_height, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # boss on -Z face (bottom)
    with Locations((boss2_x, 0, 0)):
        Cylinder(boss_radius, boss_height, align=(Align.CENTER, Align.CENTER, Align.MAX))

part = p.part
part.name = "leaf_with_bosses"
export_step(part, "output.step")