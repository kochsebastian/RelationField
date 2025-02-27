<span align="center">
<h1> RelationField: Relate Anything in Radiance Fields</h1>

<a href="https://kochsebastian.com">Sebastian Koch</a>,
<a href="https://scholar.google.com/citations?user=dfjN3YAAAAAJ">Johanna Wald</a>,
<a href="https://scholar.google.com/citations?user=k4m1c6EAAAAJ">Mirco Colosi</a>,
<a href="https://scholar.google.com/citations?user=U3KSTwkAAAAJ">Narunas Vaskevicius</a>,
<a href="https://phermosilla.github.io">Pedro Hermosilla</a>,
<a href="https://federicotombari.github.io">Federico Tombari</a>
<a href="https://scholar.google.com/citations?user=FuY-lbcAAAAJ">Timo Ropinski</a>

<!-- <h3>venue</h3> -->

<a href="https://arxiv.org/abs/">Paper</a> |
<a href="http://relationfield.github.io">Project Page</a>

</span>

![RelationField Teaser](https://relationfield.github.io/static/images/teaser.png)

## Installation

#### Install NerfStudio

```
conda create --name relationfield -y python=3.10
conda activate relationfield
python -m pip install --upgrade pip
```

### Install cuda, torch, etc

```
conda install nvidia/label/cuda-11.8.0::cuda
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
python -m pip install ninja git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch
```

### Install SAM

```
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### Install RelationField

```
git clone https://github.com/boschresearch/relationfield
cd relationfield
python -m pip install -e .
```

## Data preparation and Foundation Models

The datasets and saved NeRF models require significant disk space.
Let's link them to some (remote) larger storage:

```
ln -s path/to/large_disk/data data
ln -s path/to/large_disk/models models
ln -s path/to/large_disk/outputs outputs
```

Download the OpenSeg feature extractor model from [here](https://drive.google.com/file/d/1DgyH-1124Mo8p6IUJ-ikAiwVZDDfteak/view?usp=sharing) and unzip it into `./models`.
Download the SAM from [here](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) and unzip it into `./models`.

### Replica Dataset

Download the Replica dataset pre-processed by [NICE-SLAM](https://pengsongyou.github.io/nice-slam) and transform it into [nerfstudio](https://docs.nerf.studio) format using these steps:

```
cd data
wget https://cvg-data.inf.ethz.ch/nice-slam/data/Replica.zip
unzip Replica.zip
cd ..
python datasets/replica_preprocess.py --data <root-replica-folder> --output <nerfstudio-output>
```


### SCANNET++ Dataset

Follow the ScanNet++ data download [here](https://kaldir.vc.in.tum.de/scannetpp/) to download the entire ScanNet++ dataset or a handful of subscenes and transform it into [nerfstudio](https://docs.nerf.studio) format using these steps:

```
python datasets/scannetpp_preprocess.py
```

### RIO10 Dataset

Download the RIO10 dataset from [here](https://github.com/WaldJohannaU/RIO10?tab=readme-ov-file) and transform it into [nerfstudio](https://docs.nerf.studio) format using these steps:

```
python datasets/rio_preprocess.py
```

### Preprocess GPT Captions

To caption the preprocessed dataset with GPT run:

```
export OPEN_API_KEY=YOUR_API_KEY
python datasets/preprocess_dataset_gpt.py --data_dir [PATH]
```

In case a one of the captioning steps fails you can manually correct it and run (this happens very rarely):

```
python datasets/preprocess_dataset_gpt.py --data_dir [PATH] --redo img_id1.png,...,img_idk.png
```

## Running RelationField

This repository creates a new Nerfstudio method named "relationfield". To train with it, run the command:

```
ns-train relationfield --data [PATH]
```

To view the optimized NeRF, you can launch the viewer separately:

```
ns-viewer --load-config outputs/path_to/config.yml
```

Interact with the viewer to visualize relationships:


https://github.com/user-attachments/assets/65688512-a4f7-4127-812a-8eadf54e579a



### Utilizing depth data
RelationField support depth supervision for improved and faster convergence of the NeRF geometry. To activate make sure that depth data is available for your data and run:
```
export NERFACTO_DEPTH=True
ns-train relationfield --data [PATH]
```

## Running RelationField with Gaussian Splatting geometry!
Although RelationField's relation field is optimized using NeRF geometry, it can be
used to relate gaussians in 3D!
```
ns-train relationfield-gauss --data [PATH] --pipeline.relationfield-ckpt outputs/path_to/config.yml
```
## Troubleshooting
**Note:** RelationField requires ~32GB of memory during training.  If your system has lower computational resources, consider reducing the number of training rays.

In `relationfield/relationfield/relationfield_config.py`, you can adjust the following parameters (lines 42-46):

```python
train_num_rays_per_batch=4096,
eval_num_rays_per_batch=4096, 
pixel_sampler=RelationFieldPixelSamplerConfig(
    num_rays_per_image=256,  # 4096/256 = 16 images per batch
),

```

## Acknowledgement
Large parts of the code base are inspied and build on top of [OpenNerf](https://github.com/opennerf/opennerf) and [GARField](https://github.com/chungmin99/garfield).

## Citation

If you use this work or find it helpful, please consider citing: (bibtex)

```
@article{koch2024relationfield,
 author = {Koch, Sebastian and Wald, Johanna and Colosi, Mirco and Vaskevicius, Narunas and Hermosilla, Pedro and Tombari, Federico and Ropinski, Timo}},
 title = {RelationField: Relate Anything in Radiance Fields},
 journal = {arXiv preprint arXiv:2412.13652},
 year = {2024},
}
```
