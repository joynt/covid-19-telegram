import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

from data import current_world_df, get_df_data, NAME_NEW, NAME_OLD


def world(path: Path):
    cworld_df = current_world_df()
    get_df_data(cworld_df, 'confirmed', new_name='name')

    worldmap_df = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    worldmap_df.drop(worldmap_df.index[worldmap_df['name'] == 'Antarctica'], inplace=True)
    worldmap_df.drop(worldmap_df.index[worldmap_df['name'] == 'Fr. S. Antarctic Lands'], inplace=True)

    for nold, nnew in zip(NAME_OLD, NAME_NEW):
        idx = worldmap_df.index[worldmap_df['name'] == nold]
        worldmap_df.at[idx, 'name'] = nnew

    confirmed_world = get_df_data(cworld_df, 'confirmed', new_name='name')
    merged_world = worldmap_df.set_index('name').join(confirmed_world.set_index('name'))
    merged_world['log_value'] = np.log10(merged_world['confirmed'])

    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.axis('off')
    merged_world.plot(column='log_value', cmap='Reds', ax=ax, linewidth=0.8,
                      edgecolor='0.8', vmin=0, vmax=6, legend=False)

    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap='Reds', norm=colors.LogNorm(vmin=1, vmax=10 ** 6))
    # empty array for the data range
    sm._A = []
    # add the colorbar to the figure
    cbar = fig.colorbar(sm, fraction=0.025, pad=0)
    cbar.ax.set_yticklabels([1, 10, 100, 1000, 10000, 100000, 1000000])

    save = path / 'world.png'
    if save.exists():
        os.remove(str(save))

    plt.savefig(save, dpi=400, bbox_inches='tight')
    plt.close(fig)