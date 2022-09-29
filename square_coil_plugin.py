import pcbnew
import numpy as np

VIA_DIAM = 0.8
VIA_DRILL = 0.4
TRACK_THICKNESS = 0.2
TRACK_SPACING = 0.2
SEGMENT_LENGTH = 2 * 2*np.pi/360.0
STATOR_RADIUS = 24
STATOR_HOLE_RADIUS = 4
INNER_RADIUS = 1
# each coil is in the middle of the stator radius
OUTER_RADIUS = (0.5 * STATOR_RADIUS * np.pi) / 6 - 2 * TRACK_SPACING


def spiral(angle, distance, coil_inner_radius, coil_outer_radius, track_width, track_spacing, direction=1, flip=False):
    thickness = track_width + track_spacing
    number_turns = (coil_outer_radius - coil_inner_radius)//thickness
    # create a starting point in the center
    yield distance * np.cos(angle), distance * np.sin(angle)
    for theta in np.arange(0, number_turns * 2*np.pi, 0.1):
        radius_x = coil_inner_radius + thickness * theta/(2*np.pi)
        radius_y =  coil_inner_radius + thickness * theta/(2*np.pi)
        # if direction == -1:
        #     x = radius_x * np.cos(direction * (theta + np.pi))
        #     y = radius_y * np.sin(direction * (theta + np.pi))
        # else:
        alpha = theta - np.pi/2 * np.round(theta/(np.pi/2))
        x = radius_x * np.cos(theta)/np.cos(alpha)
        y = radius_y * np.sin(theta)/np.cos(alpha)

        # x = radius_x * np.cos(direction * (theta))
        # y = radius_y * np.sin(direction * (theta))            
        # rotate by angle
        x, y = x*np.cos(angle) - y*np.sin(angle), x*np.sin(angle) + y*np.cos(angle)
        # translate by distance
        x, y = x + distance * np.cos(angle), y + distance * np.sin(angle)
        yield x, y


def create_tracks(board, group, coords, layer):
    last_x = None
    last_y = None
    for x, y in coords:
        track = pcbnew.PCB_TRACK(board)
        if last_x is not None:
            track.SetStart(pcbnew.wxPointMM(float(last_x), float(last_y)))
            track.SetEnd(pcbnew.wxPointMM(float(x), float(y)))
            track.SetWidth(int(TRACK_THICKNESS * 1e6))
            track.SetLayer(layer)
            board.Add(track)
            group.AddItem(track)
        last_x = x
        last_y = y


def create_coil(board, name, angle, stator_radius, coil_inner_radiue, coil_outer_radius, track_thickness, track_spacing, flip=False):
    group = pcbnew.PCB_GROUP(board)
    board.Add(group)

    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(name)
    x = stator_radius/2 * np.cos(angle)
    y = stator_radius/2 * np.sin(angle)
    txt.SetPosition(pcbnew.wxPointMM(float(x), float(y)))
    txt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
    txt.SetTextSize(pcbnew.wxSize(5000000, 5000000))
    txt.SetLayer(pcbnew.F_SilkS)
    board.Add(txt)

    coords = spiral(angle, stator_radius/2, coil_inner_radiue, coil_outer_radius, track_thickness, track_spacing, 1, flip)
    create_tracks(board, group, coords, pcbnew.F_Cu)

    coords = spiral(angle, stator_radius/2, coil_inner_radiue, coil_outer_radius, track_thickness, track_spacing, -1, flip)
    create_tracks(board, group, coords, pcbnew.B_Cu)

    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.wxPointMM(float(stator_radius/2 * np.cos(angle)), float(stator_radius/2 * np.sin(angle))))
    via.SetWidth(int(VIA_DIAM * 1e6))
    via.SetDrill(int(VIA_DRILL * 1e6))
    board.Add(via)
    group.AddItem(via)


class SquareCoilPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Create square coil"
        self.category = "Coils"
        self.description = "Creates a square coil"
        # self.show_toolbar_button = False # Optional, defaults to False
        # self.icon_file_name = os.path.join(os.path.dirname(__file__), 'simple_plugin.png') # Optional, defaults to ""

    def Run(self):
        board = pcbnew.GetBoard()
        # create the center hole
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetStart(pcbnew.wxPointMM(STATOR_HOLE_RADIUS, 0))
        arc.SetCenter(pcbnew.wxPointMM(0, 0))
        arc.SetArcAngleAndEnd(0, False)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
        board.Add(arc)
        # create six coils equally spaced around the origin
        coil_angle = 2*np.pi/6

        # coil A
        create_coil(board, "A", 0 * coil_angle, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, False)
        create_coil(board, "A", 0 * coil_angle + np.pi, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, True)

        # coil B
        create_coil(board, "B", 1 * coil_angle, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, False)
        create_coil(board, "B", 1 * coil_angle + np.pi, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, True)

        # coil C
        create_coil(board, "C", 2 * coil_angle, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, False)
        create_coil(board, "C", 2 * coil_angle + np.pi, STATOR_RADIUS, INNER_RADIUS, OUTER_RADIUS, TRACK_THICKNESS, TRACK_SPACING, True)


SquareCoilPlugin().register()  # Instantiate and register to Pcbnew
