import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def create_pin(radius, angle, name):
    return {
        "x": radius * np.cos(np.deg2rad(angle)),
        "y": radius * np.sin(np.deg2rad(angle)),
        "name": name,
    }


def create_pad(point, width, height, layer):
    return {
        "x": point[0],
        "y": point[1],
        "width": width,
        "height": height,
        "layer": layer,
    }


def create_silk(point, text, layer="f", size=5, angle=0):
    return {
        "x": point[0],
        "y": point[1],
        "text": text,
        "layer": layer,
        "size": size,
        "angle": angle,
    }


def create_via(point):
    return {"x": point[0], "y": point[1]}


def create_track(points):
    return [{"x": x, "y": y} for x, y in points]


def create_mounting_hole(point, diameter):
    return {
        "x": point[0],
        "y": point[1],
        "diameter": diameter,
    }


def create_track_json(points):
    return [{"x": x, "y": y} for x, y in points]


def dump_json(
    filename,
    stator_radius,
    stator_hole_radius,
    track_width,
    pin_diam,
    pin_drill,
    via_diam,
    via_drill,
    vias,
    pins,
    pads,
    silk,
    tracks_f,
    tracks_in1,
    tracks_in2,
    tracks_b,
    mounting_holes,
):
    # dump out the results to json
    json_result = {
        "parameters": {
            "trackWidth": track_width,
            "statorHoleRadius": stator_hole_radius,
            "statorRadius": stator_radius,
            "viaDiameter": via_diam,
            "viaDrillDiameter": via_drill,
            "pinDiameter": pin_diam,
            "pinDrillDiameter": pin_drill,
        },
        "vias": vias,
        "pins": pins,
        "pads": pads,
        "silk": silk,
        "tracks": {
            "f": [create_track_json(points) for points in tracks_f],
            "in1": [create_track_json(points) for points in tracks_in1],
            "in2": [create_track_json(points) for points in tracks_in2],
            "b": [create_track_json(points) for points in tracks_b],
        },
        "mountingHoles": mounting_holes,
    }
    json.dump(json_result, open(filename, "w"))
    return json_result


def plot_json(json_result):
    stator_radius = json_result["parameters"]["statorRadius"]
    stator_hole_radius = json_result["parameters"]["statorHoleRadius"]
    pin_diam = json_result["parameters"]["pinDiameter"]
    pin_drill = json_result["parameters"]["pinDrillDiameter"]
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
    ax.figure.set_size_inches(11, 11)

    # set the axis range
    ax.set_xlim(-stator_radius - 1, stator_radius + 1)
    ax.set_ylim(-stator_radius - 1, stator_radius + 1)

    # plot the pads
    for pad in json_result["pads"]:
        color = "red"
        if pad["layer"] == "b":
            color = "blue"
        ax.add_patch(
            plt.Rectangle(
                (pad["x"] - pad["width"] / 2, pad["y"] - pad["height"] / 2),
                pad["width"],
                pad["height"],
                fill=True,
                color=color,
            )
        )

    # plot the pins
    for pin in json_result["pins"]:
        ax.add_patch(
            plt.Circle(
                (pin["x"], pin["y"]),
                radius=pin_diam / 2,
                fill=True,
                color="orange",
            )
        )
        ax.add_patch(
            plt.Circle(
                (pin["x"], pin["y"]),
                radius=pin_drill / 2,
                fill=True,
                color="white",
            )
        )

    # plot the silk
    for silk in json_result["silk"]:
        color = "cyan"
        if silk["layer"] == "b":
            color = "magenta"
        ax.text(
            silk["x"],
            silk["y"],
            silk["text"],
            horizontalalignment="center",
            verticalalignment="center",
            color=color,
            fontsize=silk["size"] * 10,
        )

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

    # plot the mounting holes
    for hole in json_result["mountingHoles"]:
        ax.add_patch(
            plt.Circle(
                (hole["x"], hole["y"]),
                radius=hole["diameter"] / 2,
                fill=False,
                color="orange",
            )
        )

    # plot the edge cuts
    ax.add_patch(
        plt.Circle(
            (0, 0),
            radius=stator_radius,
            fill=False,
            color="orange",
        )
    )
    ax.add_patch(
        plt.Circle(
            (0, 0),
            radius=stator_hole_radius,
            fill=False,
            color="orange",
        )
    )
    # save to file
    ax.figure.savefig("coils.png")
