# Copyright (c) 2025 Robert Bosch GmbH
# SPDX-License-Identifier: AGPL-3.0

# This source code is derived from OpenNerf
#   (https://github.com/opennerf/opennerf)
# Copyright (c) 2014 OpenNerf authors, licensed under the MIT license,
# cf. 3rd-party-licenses.txt file in the root directory of this source tree.

from typing import Dict
import sys
import numpy as np
import torch
from torch import Tensor
from jaxtyping import Float

from nerfstudio.cameras.rays import RaySamples
from nerfstudio.field_components.spatial_distortions import (
    SceneContraction,
    SpatialDistortion,
)
from nerfstudio.fields.base_field import Field

try:
    import tinycudann as tcnn
except ImportError:
    pass
except EnvironmentError as _exp:
    if "Unknown compute capability" not in _exp.args[0]:
        raise _exp
    print("Could not load tinycudann: " + str(_exp), file=sys.stderr)

from enum import Enum

class OpenNerfFieldHeadNames(Enum):
    """Possible field outputs"""
    HASHGRID = "hashgrid"
    OPENSEG = "openseg"
    CLIP = "clip"
    
class OpenNerfField(Field):
    def __init__(
        self,
        grid_layers,
        grid_sizes,
        grid_resolutions,
        num_hidden_clip_layers,
        spatial_distortion: SpatialDistortion = SceneContraction(),
    ):
        super().__init__()
        assert len(grid_layers) == len(grid_sizes) and len(grid_resolutions) == len(grid_layers)
        self.spatial_distortion = spatial_distortion
        self.clip_encs = torch.nn.ModuleList(
            [
                OpenNerfField._get_encoding(
                    grid_resolutions[i][0], grid_resolutions[i][1], grid_layers[i], indim=3, hash_size=grid_sizes[i]
                )
                for i in range(len(grid_layers))
            ]
        )
        tot_out_dims = sum([e.n_output_dims for e in self.clip_encs])
        
        self.openseg_net = tcnn.Network(
            n_input_dims=tot_out_dims,
            n_output_dims=768,
            network_config={
                "otype": "CutlassMLP",
                "activation": "ReLU",
                "output_activation": "None",
                "n_neurons": 256,
                "n_hidden_layers": num_hidden_clip_layers,
            },
        )
        
        # self.clip_net = tcnn.Network(
        #     n_input_dims=tot_out_dims,
        #     n_output_dims=1152, 
        #     network_config={
        #         "otype": "CutlassMLP",
        #         "activation": "ReLU",
        #         "output_activation": "None",
        #         "n_neurons": 256,
        #         "n_hidden_layers": num_hidden_clip_layers,
        #     },
        # )


        

    @staticmethod
    def _get_encoding(start_res, end_res, levels, indim=3, hash_size=19):
        growth = np.exp((np.log(end_res) - np.log(start_res)) / (levels - 1))
        
        enc = tcnn.Encoding(
            n_input_dims=indim,
            encoding_config={
                "otype": "HashGrid",
                "n_levels": levels,
                "n_features_per_level": 8,
                "log2_hashmap_size": hash_size,
                "base_resolution": start_res,
                "per_level_scale": growth,
            },
        )
        return enc

    def get_outputs(self, ray_samples: RaySamples, clip_scales=None) -> Dict[OpenNerfFieldHeadNames, Float[Tensor, "bs dim"]]:
        outputs = {}

        positions = ray_samples.frustums.get_positions().detach()
        positions = self.spatial_distortion(positions)
        positions = (positions + 2.0) / 4.0

        xs = [e(positions.view(-1, 3)) for e in self.clip_encs]
        x = torch.concat(xs, dim=-1)

        openseg_pass = self.openseg_net(x).view(*ray_samples.frustums.shape, -1)
        outputs[OpenNerfFieldHeadNames.OPENSEG] = openseg_pass
        
        # clip_pass = self.clip_net(x).view(*ray_samples.frustums.shape, -1)
        # outputs[OpenNerfFieldHeadNames.CLIP] = clip_pass
        outputs[OpenNerfFieldHeadNames.CLIP] = openseg_pass
        
        return outputs