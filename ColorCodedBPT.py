from astropy.io import fits
import matplotlib.pyplot as plt
import matplotlib.colors as mpc
import numpy as np

plt.style.use('./dark.mplstyle')

def clean_flux(data_):
    flux = data_
    return flux

data_Halpha = clean_flux(fits.open('./NGC1275_3_Halpha_mask.fits')[0].data)
data_NII = clean_flux(fits.open('./NGC1275_3_NII6583_mask.fits')[0].data)
data_SN3_continuum = fits.open('./NGC1275_3_continuum_mask.fits')[0].data

NII_Halpha = np.log10(data_NII/data_Halpha)
Eq_width = (data_Halpha/data_SN3_continuum)

Seyferts = []
Liners = []
SF = []
y_pos = 0
x_pos = 0
x_dim = data_Halpha.shape[0]
y_dim = data_Halpha.shape[1]
empty_map = np.zeros_like(data_Halpha)
#empty_map[:] = np.nan
for nii_halpha, eq_width in zip(NII_Halpha.flatten(), Eq_width.flatten()):
    point = (nii_halpha, eq_width, x_pos, y_pos)
    if nii_halpha < -0.4:
        SF.append(point)
        empty_map[x_pos, y_pos] = 3
    else:
        if eq_width > 6:
            Seyferts.append(point)
            empty_map[x_pos, y_pos] = 1
        else:
            Liners.append(point)
            empty_map[x_pos, y_pos] = 2
    y_pos += 1
    if y_pos >= y_dim:
        y_pos = 0
        x_pos += 1

fig = plt.figure(figsize=(16,8))
#plt.scatter(NII_Halpha.flatten(), Eq_width.flatten(), alpha=0.3)
plt.scatter([val[0] for val in Seyferts], [val[1] for val in Seyferts], color='C0', alpha=0.3, label='Seyferts')
plt.scatter([val[0] for val in Liners], [val[1] for val in Liners], color='C1', alpha=0.3, label='LINERs')
plt.scatter([val[0] for val in SF], [val[1] for val in SF], color='C2', alpha=0.3, label='Star-Forming')
#plt.legend()
plt.vlines(-0.4, 0.1, 1000, color = 'white', linewidth = 1)
plt.hlines(6, -0.4, 1, color = 'white', linewidth = 1)
plt.hlines(0.5, -1, 1,linestyle = 'dashed', color = 'white', linewidth = 1)
x_graph = np.linspace(-1, 1, 100 )
plt.plot(x_graph, np.exp(-2.35*x_graph + np.log(0.5)), linestyle = 'dashed', color = 'white', linewidth = 1)


plt.text(-0.8, 300, 'SF', fontsize = 15, fontweight='bold')
plt.text(0.1, 300, "Seyferts", fontsize = 15, fontweight='bold')
plt.text(0.34, .6, "LINERs", fontsize = 15, fontweight='bold')
plt.text(-0.33, 0.12, "Passive galaxies", fontsize = 15, fontweight='bold')
plt.ylabel('W$_{H\\alpha} [\\AA]$', fontsize = 13, weight = 'bold')
plt.xlabel('Log([NII]/H$\\alpha)$', fontsize = 13, weight = 'bold')

plt.yscale('log')
plt.ylim(.1, 1000)
plt.xlim(-1, 1)
plt.savefig('ColorCodedBPT.png')
plt.clf()

#plt.style.use('./light.mplstyle')

cmap_ = mpc.ListedColormap(['C0', 'C1', 'white', 'C2'])
plt.imshow(empty_map, origin='lower', cmap=cmap_)
plt.savefig('ColorCodedMap.png')
