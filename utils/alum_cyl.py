from cil.processors import Slicer
from matplotlib import pyplot as plt

A = (245, 246)
B = (623, 624)
C = (987, 988)

def get_sharpness_slicers():

    sharpness_slicer_A_1 = Slicer(roi={'horizontal_x': (185, 230), 'horizontal_y': (305,306), 'vertical': A})
    sharpness_slicer_A_2 = Slicer(roi={'horizontal_x': (290, 335), 'horizontal_y': (161,162), 'vertical': A})
    sharpness_slicer_A_3 = Slicer(roi={'horizontal_x': (340, 385), 'horizontal_y': (422, 423), 'vertical': A})

    sharpness_slicer_B_1 = Slicer(roi={'horizontal_x': (165, 210), 'horizontal_y': (305,306), 'vertical': B})
    sharpness_slicer_B_2 = Slicer(roi={'horizontal_x': (275, 320), 'horizontal_y': (160,161), 'vertical': B})
    sharpness_slicer_B_3 = Slicer(roi={'horizontal_x': (310, 355), 'horizontal_y': (420, 421), 'vertical': B})

    sharpness_slicer_C_1 = Slicer(roi={'horizontal_x': (320, 360), 'horizontal_y': (410,411), 'vertical': C})
    sharpness_slicer_C_2 = Slicer(roi={'horizontal_x': (395, 440), 'horizontal_y': (260,261), 'vertical': C})


    return [sharpness_slicer_A_1, sharpness_slicer_A_2, sharpness_slicer_A_3, sharpness_slicer_B_1, sharpness_slicer_B_2, sharpness_slicer_B_3, sharpness_slicer_C_1, sharpness_slicer_C_2]


def crop_rod_B(rec):
    """Crop four rods from a reconstruction slice B."""
    rod3 = Slicer(roi={'horizontal_x': (280, 350), 'horizontal_y': (135, 200)})(rec)
    rod4 = Slicer(roi={'horizontal_x': (165, 235), 'horizontal_y': (285, 350)})(rec)
    rod1 = Slicer(roi={'horizontal_x': (315, 385), 'horizontal_y': (395, 460)})(rec)
    rod2 = Slicer(roi={'horizontal_x': (425, 495), 'horizontal_y': (247, 312)})(rec)
    return [rod1, rod2, rod3, rod4]


def apply_plot_settings():
    # used for bar charts
    plt.legend()
    plt.tight_layout()
    plt.minorticks_on()
    plt.tick_params(axis='x', which='minor', bottom=False)
    plt.grid(axis='y', which='major', linestyle='-', alpha=0.5)
    plt.grid(axis='y', which='minor', linestyle='--', alpha=0.25)

def get_slice_b_outer_rois(sliced_recon_dict):
    labels = sliced_recon_dict.keys()


    labels_slice_B_rods = ["Slice B " + label for label in labels]

    slice_B_data = {}

    for i, data_label in enumerate(labels):
        rec = sliced_recon_dict[data_label][1]
        rods = crop_rod_B(rec)
        current_labels = [f"{labels_slice_B_rods[i]} Rod 1", "Rod 2", "Rod 3", "Rod 4"]

        slice_B_data[data_label] = {"rods": rods, "labels": current_labels}

    return slice_B_data