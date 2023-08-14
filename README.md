# Google Summer of Code 2023

### Multi-Channel Imaging Support - caMicroscope

This project aims to add support for Multi-Channel Imaging in caMicroscope, a platform used for visualizing and analyzing medical imaging data. Currently, the platform only supports datasets with a spatial representation for up to three channels. This project aims to create a function that can take in numerical data in CSV format with an arbitrary number of channels and select three fields to assign to red, green, and blue channels to generate an image. This project will allow Researchers and Deep Learning partitioners to make sense of higher-dimensional data and improve their analysis of medical imaging data.

## Run Docker Image

### Build the image

```bash
docker build -t multichannel .
```

### Run the image
```bash
docker run -p 5000:5000 multichannel:latest
```

or

### Pull the Docker Image

Image: [Multi-channel-image](https://hub.docker.com/repository/docker/jaintarun75/multi-channel-image/general)

```bash
docker pull jaintarun75/multi-channel-image:v1
```

### Run the image
```bash
docker run -p 5000:5000 jaintarun75/multi-channel-image:v1
```

### Technologies

Python || OpenCV || Image processing || Flask(py+js) || OpenSeaDragon || DZI

### Authors

- Mentor: [Birmingham Ryan](https://github.com/birm)
- Contributor: [Tarun R Jain](https://github.com/lucifertrj/)

