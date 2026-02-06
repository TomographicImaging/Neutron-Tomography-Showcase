import numpy as np

from cil.plugins.astra import FBP as FBP_ASTRA
import numba

def get_weights_for_FBP(data):
    # Get the angles from the golden ratio dataset
    angles = data.geometry.angles.copy()

    angle_max = np.max(angles)
    angle_min = np.min(angles)
    angle_range = angle_max - angle_min


    # Create array of angle indices in order of angle values
    sorted_indices = np.argsort(angles)
    ordered_angles = angles[sorted_indices]

    num_angles = len(ordered_angles)
    weights = []

    for i in range(num_angles):
        prev_idx = (i - 1) % num_angles
        next_idx = (i + 1) % num_angles

        prev_angle = ordered_angles[prev_idx]
        next_angle = ordered_angles[next_idx]
        
        weights.append((next_angle-prev_angle) % angle_range / 2.0)

    # Reorder weights back to original projection order
    original_order_weights = np.zeros(num_angles)
    for i, idx in enumerate(sorted_indices):
        original_order_weights[idx] = weights[i]

    print("Total of weights: ", np.sum(original_order_weights))
    print(f"Weights shape: {original_order_weights.shape}")
    print(f"Min weight: {original_order_weights.min():.4f}, Max weight: {original_order_weights.max():.4f}")
    print(f"Mean weight: {original_order_weights.mean():.4f}")


    # Normalize weights:
    original_order_weights = original_order_weights /np.mean(original_order_weights)

    return original_order_weights

def run_weighted_fbp(data, weights):
    # Apply weights to the data
    data_weighted = data.copy()
    for angle_idx in range(data.geometry.angles.size):
        try:
            data_weighted.array[angle_idx, :, :] *= weights[angle_idx]
        except:
            data_weighted.array[angle_idx, :] *= weights[angle_idx]

    # Reorder and reconstruct with weighted data
    data_weighted.reorder('astra')
    recon = FBP_ASTRA(data_weighted.geometry.get_ImageGeometry(), data_weighted.geometry)(data_weighted)
    return recon


def run_weighted_fbp_no_numba(data, weights):
    if 'vertical' in data.dimension_labels:
        v_size = data.get_dimension_size('vertical')

    if 'horizontal' in data.dimension_labels:
        h_size = data.get_dimension_size('horizontal')

    data_weighted = data.copy()
    #data_weighted_flat = data_weighted.ravel()
    proj_size = v_size*h_size
    num_proj = int(data.array.size / proj_size)


    out_reshaped = data_weighted.array.reshape(num_proj, proj_size)
    weight = np.asarray(weight)
    weight =  weights[:, np.newaxis]  # shape: (num_proj, 1) 
    np.multiply(out_reshaped, weight, out=out_reshaped)

    return out_reshaped

    # for i in num_proj:
    #     data_weighted_flat[i*proj_size+]




@numba.njit(parallel=True)
def numba_loop(weights, num_proj, proj_size, out):
    out_flat = out.ravel()
    for i in numba.prange(num_proj):
        for ij in range(proj_size):
            out_flat[i*proj_size+ij] *= (weights[i])



# @numba.njit(parallel=True)
# def numba_loop(flux, target, num_proj, proj_size, out):
#     out_flat = out.ravel()
#     flux_flat = flux.ravel()
#     for i in numba.prange(num_proj):
#         for ij in range(proj_size):
#             out_flat[i*proj_size+ij] *= (target/flux_flat[i])
