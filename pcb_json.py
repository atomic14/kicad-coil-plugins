import json
import pandas as pd
import matplotlib.pyplot as plt


def create_track(points):
    return [{"x": x, "y": y} for x, y in points]


def dump_json(
    filename,
    stator_radius,
    stator_hole_radius,
    track_width,
    pad_diam,
    pad_drill,
    via_diam,
    via_drill,
    vias,
    pads,
    silk,
    tracks_f,
    tracks_b,
):
    # dump out the results to json
    json_result = {
        "parameters": {
            "trackWidth": track_width,
            "statorHoleRadius": stator_hole_radius,
            "statorRadius": stator_radius,
            "viaDiameter": via_diam,
            "viaDrillDiameter": via_drill,
            "padDiameter": pad_diam,
            "padDrillDiameter": pad_drill,
        },
        "vias": vias,
        "pads": pads,
        "silk": silk,
        "tracks": {
            "f": [create_track(points) for points in tracks_f],
            "b": [create_track(points) for points in tracks_b],
        },
    }
    json.dump(json_result, open(filename, "w"))
    return json_result


def plot_json(json_result):
    stator_radius = json_result["parameters"]["statorRadius"]
    stator_hole_radius = json_result["parameters"]["statorHoleRadius"]
    pad_diam = json_result["parameters"]["padDiameter"]
    pad_drill = json_result["parameters"]["padDrillDiameter"]
    # track_width = json_result["parameters"]["trackWidth"]
    via_dim = json_result["parameters"]["viaDiameter"]
    via_drill = json_result["parameters"]["viaDrillDiameter"]
    # plot the back tracks
    ax = None
    for track in json_result["tracks"]["b"]:
        df = pd.DataFrame(track, columns=["x", "y"])
        ax = df.plot.line(x="x", y="y", color="blue", ax=ax)
        ax.axis("equal")

    # plot the front tracks
    for track in json_result["tracks"]["f"]:
        df = pd.DataFrame(track, columns=["x", "y"])
        ax = df.plot.line(x="x", y="y", color="red", ax=ax)
        ax.axis("equal")

    # hide the legend
    ax.legend().set_visible(False)
    # make the plot bigger
    ax.figure.set_size_inches(10, 10)

    # plot the vias
    for via in json_result["vias"]:
        ax.add_patch(
            plt.Circle(
                (via["x"], via["y"]),
                radius=via_dim / 2,
                fill=True,
                color="black",
            )
        )
        ax.add_patch(
            plt.Circle(
                (via["x"], via["y"]),
                radius=via_drill / 2,
                fill=True,
                color="white",
            )
        )

    # plot the edge cuts
    ax.add_patch(
        plt.Circle(
            (0, 0),
            radius=stator_radius,
            fill=False,
            color="yellow",
        )
    )
    ax.add_patch(
        plt.Circle(
            (0, 0),
            radius=stator_hole_radius,
            fill=False,
            color="yellow",
        )
    )

    # plot the pads
    for pad in json_result["pads"]:
        ax.add_patch(
            plt.Circle(
                (pad["x"], pad["y"]),
                radius=pad_diam / 2,
                fill=True,
                color="yellow",
            )
        )
        ax.add_patch(
            plt.Circle(
                (pad["x"], pad["y"]),
                radius=pad_drill / 2,
                fill=True,
                color="white",
            )
        )

    # plot the silk
    for silk in json_result["silk"]:
        ax.text(
            silk["x"],
            silk["y"],
            silk["text"],
            horizontalalignment="center",
            verticalalignment="center",
            color="black",
            fontsize=50,
        )
