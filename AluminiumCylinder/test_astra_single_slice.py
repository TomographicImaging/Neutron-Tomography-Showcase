#%%

from cil.plugins.astra import FBP as FBP_ASTRA
from data_io.read_and_write import read_processed_data
from cil.framework import ImageGeometry
#%%
data = read_processed_data(exposure_time=60, num_angles=840)
# %%
print(data.geometry)

#%%
data.reorder('astra')

# make a single slice image geometry

ig = data.geometry.get_ImageGeometry()
centre_ig = ig.get_slice(vertical='centre')

#%%
print(centre_ig)

# %%
recon = FBP_ASTRA(centre_ig, data.geometry)(data)
# %%
custom_ig_slice = ImageGeometry(voxel_num_x=centre_ig.voxel_num_x, voxel_num_y=centre_ig.voxel_num_y,
                                voxel_num_z=1, voxel_size_x=centre_ig.voxel_size_x, voxel_size_y=ig.voxel_size_y, 
                                voxel_size_z=centre_ig.voxel_size_x)
recon = FBP_ASTRA(custom_ig_slice, data.geometry)(data)

#%%





# %%
from cil.utilities.display import show2D
show2D(recon, cmap='gray')
# %%
data_no_offset = data.copy()
data_no_offset.geometry.set_centre_of_rotation(data.geometry.get_centre_of_rotation()['offset'][0])
# %%
ig_centre_no_offset = ig.get_slice(vertical='centre')
print(ig_centre_no_offset)
# %%

# DOES NOT WORK CAUSE IT DOESNT KNOW THE POSITION OF THE SLICE ON Z
ig = data.geometry.get_ImageGeometry()
off_centre_ig = ig.get_slice(vertical=8)
custom_ig_slice = ImageGeometry(voxel_num_x=off_centre_ig.voxel_num_x, voxel_num_y=off_centre_ig.voxel_num_y,
                                voxel_num_z=1, voxel_size_x=off_centre_ig.voxel_size_x, voxel_size_y=off_centre_ig.voxel_size_y, 
                                voxel_size_z=off_centre_ig.voxel_size_x)
print(off_centre_ig)        
# %%
recon_off = FBP_ASTRA(custom_ig_slice, data.geometry)(data)
# %%
show2D(recon_off)
# %%
# OPEN ISSUE _ SHOULD BE ABLE TO SLICE ON CENTRE SLICE PARALLEL TILTED
recon_2D = FBP_ASTRA(custom_ig_slice, data_no_offset.get_slice(vertical='centre').geometry)(data_no_offset.get_slice(vertical='centre'))
# %%
show2D(recon_2D)
# %%
print(custom_ig_slice)
print(data_no_offset.get_slice(vertical='centre').geometry)
# %%
# IT WORKS SO SHOULD BE ABLE TO LET ALL IG BE 3D