import pcbnew
import json


def create_tracks(board, group, net, layer, thickness, coords):
    last_x = None
    last_y = None
    for coord in coords:
        x = coord['x']
        y = coord['y']
        track = pcbnew.PCB_TRACK(board)
        if last_x is not None:
            track.SetStart(pcbnew.wxPointMM(float(last_x), float(last_y)))
            track.SetEnd(pcbnew.wxPointMM(float(x), float(y)))
            track.SetWidth(int(thickness * 1e6))
            track.SetLayer(layer)
            track.SetNetCode(net.GetNetCode())
            board.Add(track)
            group.AddItem(track)
        last_x = x
        last_y = y


class CoilPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Create coil 3"
        self.category = "Coils"
        self.description = "Creates a coil"
        # self.show_toolbar_button = False # Optional, defaults to False
        # self.icon_file_name = os.path.join(os.path.dirname(__file__), 'simple_plugin.png') # Optional, defaults to ""

    def Run(self):
        board = pcbnew.GetBoard()
        # load up the JSON with the coil parameters
        coil_data = json.load(open("/Users/chrisgreening/Work/projects/pcb_motor/kicad-coil-plugins/coil.json"))
        # parameters
        track_width = coil_data['parameters']['trackWidth']
        stator_hole_radius = coil_data['parameters']['statorHoleRadius']
        via_diameter = coil_data['parameters']['viaDiameter']
        via_drill_diameter = coil_data['parameters']['viaDrillDiameter']

        # put everything in a group to make it easier to manage
        pcb_group = pcbnew.PCB_GROUP(board)
        board.Add(pcb_group)

        # create the center hole
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetStart(pcbnew.wxPointMM(stator_hole_radius, 0))
        arc.SetCenter(pcbnew.wxPointMM(0, 0))
        arc.SetArcAngleAndEnd(0, False)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(int(0.1 * pcbnew.IU_PER_MM))
        board.Add(arc)
        pcb_group.AddItem(arc)

        # create tracks
        for track in coil_data["tracks"]:
            # find the matching net for the track
            net = board.FindNet(track['net'])
            if net is None:
                raise "Net not found: {}".format(track['net'])
            create_tracks(board, pcb_group, net, pcbnew.F_Cu, track_width, track["f"])
            create_tracks(board, pcb_group, net, pcbnew.B_Cu, track_width, track["b"])

        # create the vias
        for via in coil_data['vias']:
            pcb_via = pcbnew.PCB_VIA(board)
            pcb_via.SetPosition(pcbnew.wxPointMM(float(via['x']), float(via['y'])))
            pcb_via.SetWidth(int(via_diameter * 1e6))
            pcb_via.SetDrill(int(via_drill_diameter * 1e6))
            board.Add(pcb_via)
            pcb_group.AddItem(pcb_via)

        # create any silk screen
        for text in coil_data["silk"]:
            pcb_txt = pcbnew.PCB_TEXT(board)
            pcb_txt.SetText(text["text"])
            pcb_txt.SetPosition(pcbnew.wxPointMM(text["x"], text["y"]))
            pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)
            pcb_txt.SetTextSize(pcbnew.wxSize(5000000, 5000000))
            pcb_txt.SetLayer(pcbnew.F_SilkS)
            board.Add(pcb_txt)
            pcb_group.AddItem(pcb_txt)

CoilPlugin().register() # Instantiate and register to Pcbnew])
