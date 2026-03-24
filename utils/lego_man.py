from cil.processors import Slicer
from utils.metrics import calculate_cnr, calculate_snr, calculate_L2Norm_error
from utils.masks import create_ring_mask
import matplotlib.pyplot as plt
import numpy as np




def get_masks():
    shape = [579,579] # shape of equi recon slice

    center = (shape[0]/2-14, shape[1]/2+8)
    lead_mask = create_ring_mask(shape, center, radius=190, thickness=26)

    x_range = 277
    y_range = 302
    head_mask = create_ring_mask(shape, (y_range, x_range), radius=51, thickness=6)
    head_mask2 = create_ring_mask(shape, (y_range+2, x_range+1), radius=26, thickness=9)
    head_mask3 = create_ring_mask(shape, (y_range+2, x_range+1), radius=37, thickness=7)
    # get pixels in either mask region:
    total_head_mask = head_mask | head_mask2 | head_mask3

    air_in_head_mask = create_ring_mask(shape, (y_range+2, x_range+1), radius=10, thickness=10)
    inner_head_mask = create_ring_mask(shape, (y_range+2, x_range+1), radius=20, thickness=3)

    true_indices = np.where(inner_head_mask==True)
    num_in_air = np.sum(air_in_head_mask)
    diff = np.sum(inner_head_mask)- num_in_air
    # remove these:
    x = true_indices[0][-diff:]
    y = true_indices[1][-diff:]
    for i,j in zip(x,y):
        inner_head_mask[i,j] = False

    # want background mask to have same num of pixels as lead mask
    rad = shape[1]/2-20 
    thickness = rad - np.sqrt(rad**2 - np.sum(lead_mask)/np.pi)
    inner_rad = shape[1]/2-20 - 55
    outer_rad = np.sqrt(inner_rad**2 + np.sum(lead_mask)/np.pi)
    thickness = outer_rad - inner_rad
    background_mask = create_ring_mask(shape, center, radius=outer_rad, thickness=thickness)
    true_indices = np.where(background_mask==True)
    num_in_lead = np.sum(lead_mask)
    diff = np.sum(background_mask)- num_in_lead
    # remove these:
    x = true_indices[0][-diff:]
    y = true_indices[1][-diff:]
    for i,j in zip(x,y):
        background_mask[i,j] = False

    masks_dict = {
        'lead_mask': lead_mask,
        'total_head_mask': total_head_mask,
        'air_in_head_mask': air_in_head_mask,
        'inner_head_mask': inner_head_mask,
        'background_mask': background_mask
    }
    return masks_dict

def get_sharpness_slicers():
    # left is air (outside lego head), right is lego head:
    slicer_0 = Slicer(roi={'horizontal_x':(200, 240), 'horizontal_y':(290,291)})
    slicer_1 = Slicer(roi={'horizontal_x':(200, 240), 'horizontal_y':(310,311)})
    slicer_2 = Slicer(roi={'horizontal_x':(220, 260), 'horizontal_y':(350,351)})
    slicer_3 = Slicer(roi={'horizontal_x':(240, 280), 'horizontal_y':(250,251)})
    # right is air outside lego head, left is lego head:
    slicer_4 = Slicer(roi={'horizontal_x':(322, 362), 'horizontal_y':(290,291)})
    slicer_5 = Slicer(roi={'horizontal_x':(322, 362), 'horizontal_y':(310,311)})
    slicer_6 = Slicer(roi={'horizontal_x':(295, 335), 'horizontal_y':(352,353)})
    slicer_7 = Slicer(roi={'horizontal_x':(325, 350),  'horizontal_y':(301,302)})

    # right is lego head, left is air inside lego head:
    slicer_8 = Slicer(roi={'horizontal_x':(275, 301), 'horizontal_y':(301,302)})
    # right is air inside lego man head, left is lego head:
    slicer_9 = Slicer(roi={'horizontal_x':(250, 275), 'horizontal_y':(301,302)})
    return [slicer_0, slicer_1, slicer_2, slicer_3, slicer_4, slicer_5, slicer_6, slicer_7, slicer_8, slicer_9]



def calculate_metrics(recon_full_equi, comparison_list):
    masks = get_masks()
    lead_mask = masks['lead_mask']
    total_head_mask = masks['total_head_mask']
    air_in_head_mask = masks['air_in_head_mask']
    inner_head_mask = masks['inner_head_mask']
    background_mask = masks['background_mask']
    
    data_list = [recon_full_equi, *comparison_list]
    l2n_values = [calculate_L2Norm_error(recon_full_equi, data) for data in comparison_list]

    snr_lead = []
    for data in data_list:
        snr = calculate_snr(data, lead_mask)
        snr_lead.append(snr)
    roi_mask = total_head_mask
    snr_leg = []
    for  data in data_list:
        snr = calculate_snr(data, roi_mask)
        snr_leg.append(snr)

    cnr_values = []
    # calculate CNR for each:
    for data in data_list:
        cnr = calculate_cnr(data, roi_mask=lead_mask, background_mask=background_mask)
        cnr_values.append(cnr)

    cnr_values_inner = []
    for data in data_list:
        cnr = calculate_cnr(data, roi_mask=inner_head_mask, background_mask=air_in_head_mask)
        cnr_values_inner.append(cnr)
    return l2n_values, snr_lead, snr_leg, cnr_values, cnr_values_inner

def make_bar_plots(l2n_values, snr_lead, snr_leg, cnr_values,cnr_values_inner, data_labels, orientation='horizontal'):

    # Create 3 subplots for SNR, L2 error, and CNR
    if orientation == 'horizontal':
        fig, axes = plt.subplots(1, 3, figsize=(19, 5))
    else:
        fig, axes = plt.subplots(3, 1, figsize=(7, 15))
    # colours match show1D:
    colors = ['#377eb8', '#ff7f00', '#4daf4a',
                    '#f781bf', '#a65628', '#984ea3',
                    '#999999', '#e41a1c', '#dede00']
    x = np.arange(2)

    # Subplot 1: SNR
    ax = axes[0]
    # make flexible as there could be more bars
    num_bars = len(snr_lead)
    width = 1/(3)
    offsets = np.linspace(-width, width, num_bars)
    for i, offset in enumerate(offsets):
        if len(colors) < len(offsets):
            color = None
        else:
            color = colors[i]
        ax.bar(x + offset, [snr_lead[i], snr_leg[i]], width=width/num_bars, label=data_labels[i], color=color)
    
    ax.set_xticks(x)
    ax.set_xticklabels(['Lead ROI', 'Lego Head ROI'])
    ax.set_xlabel('Region')
    ax.set_ylabel('SNR')
    ax.set_title('SNR')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)
    m = np.max(snr_lead + snr_leg)
    for i, snr_values in enumerate([snr_lead, snr_leg]):
        for j, snr_val in enumerate(snr_values):
            offset = offsets[j]
            # if even plus value is double:
            if j % 2 == 0:
                plus_val = m*0.05
            else:
                plus_val = m*0.01
            ax.text(x[i] + offset, snr_val + plus_val, f'{snr_val:.3f}', ha='center', va='bottom', fontsize=9)

    # Subplot 2: L2 Norm Error
    ax = axes[1]
    if len(colors) < len(l2n_values):
        colors_1 = None
        colors=None
    else:
        colors_1 = colors[1:]
    ax.bar(range(len(l2n_values)), l2n_values, color=colors_1)
    ax.set_xticklabels([],ha='right')
    ax.set_ylabel('L2 Norm Error')
    ax.set_title(f'L2 Norm Error vs {data_labels[0]}')
    for i, val in enumerate(l2n_values):
        ax.text(i, val -0.01, f'{val:.4f}', ha='center', va='bottom', fontsize=9)

    # Subplot 3: CNR
    ax = axes[2]
    # ax.bar(range(num_bars), cnr_values, color=colors)
    # ax.set_xticklabels([], ha='right')
    # ax.set_ylabel('CNR')
    # ax.set_title(f'CNR (Lead ROI vs Background ROI)')

    # for i, val in enumerate(cnr_values):
    #     ax.text(i, val - 0.01, f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    for i, offset in enumerate(offsets):
        if colors is None or len(colors) < len(offsets):
            color = None
        else:
            color = colors[i]
        ax.bar(x + offset, [cnr_values[i], cnr_values_inner[i]], width=width/num_bars, label=data_labels[i], color=color)
    
    ax.set_xticks(x)
    ax.set_xticklabels(['Lead ROI', 'Lego Head ROI'])
    ax.set_xlabel('Region')
    ax.set_ylabel('CNR')
    ax.set_title('CNR')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)
    m = np.max(cnr_values)
    for i, cnr_vals in enumerate([cnr_values, cnr_values_inner]):
        for j, cnr_value in enumerate(cnr_vals):
            offset = offsets[j]
            if j % 2 == 0:
                plus_val = m*0.05
            else:
                plus_val = 0.01
            ax.text(x[i] + offset, cnr_value + plus_val, f'{cnr_value:.3f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()

