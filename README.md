# Gatsiva Visualization with Plotly Example

This is a simple demo of visualizing data from the [Gatsiva Public API](https://gatsiva.com) with the the Dash interactive Python framework developed by [Plotly](https://plot.ly/).

API access is **currently limited to beta testers and collaborators**. For more information on how to utilize the Gatsiva API or to request access, please visit the [Gatsiva Website](https://gatsiva.com).

![Visualization Screenshot](https://github.com/gatsiva/dash-returns-example/raw/master/images/screenshot.png "Screenshot")

## Running Locally

To run this visualization, make sure you have a Python environment installed locally. Then install the dependencies as follows:

```
pip install -r requirements.txt
pip install plotly --upgrade
```
Once the requirements have been installed, run the environment via:

`python app.py`

## Running with Docker

This repository contains a Docker configuration to support building an image to run the visualization. To build the image, make sure you are in the project directory and execute the following command. Be sure to replace `<your_image_name>` with whatever you wish to name your image.

```
docker build -t <your_image_name> .
```

When completed, simply run the following command

```
docker run <your_image_name>
```

## Viewing the Visualization

Once the Python process has been started, you will see the following log entries in your console:

```
* Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 192-469-391
```

You may now point your browser at http://127.0.0.1:8050 to view the visualization.

## Notes

- This visualization utilizes the beta version of the Gatsiva Public API. To use a different version, simply modify the URL in the `app.py` code.
