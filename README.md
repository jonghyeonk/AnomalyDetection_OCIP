# Object-Centric Event-Data Imperfection Patterns

This repository contains the official implementation and datasets for the paper: "Object-Centric Event-Data Imperfection Patterns" (under review). 

We propose and implement several automated detection techniques for Object-Centric Event Data (OCED) imperfection patterns.

## ✨ Implemented Detection Patterns (how-to run it? just implement "test_anomaly_detection.ipynb" file)

We provide the datasets and implementation for detecting the following OCED imperfection patterns:

* Object Clones: Detected using a context-based similarity approach.
* Dissociative Objects: Detected via control-flow anomaly scores (Statistical Leverage).
* Misinformed Objects: Detected using linear regression analysis.
* Transmogrifying Objects: Detected using an IQR-based outlier detection method.
* Lost Relative & Cuckoo's Egg: Detected by comparing object relationships between different logs.
* Lost Memory: Detected using a regression model to predict missing object IDs.
* False Memory: Detected via control-flow anomaly scores (Statistical Leverage).

---

## ⚙️ Implementation Environments

* Python 3.9
* All other required Python libraries are listed in the `requirements.txt` file.
