# A Reinforcement Learning Framework for Event Log Anomaly Detection and Repair

This repository shows an extended version of the Pattern-based Anomaly Reconstruction (PBAR) method [1].

(We are preparing to submit a paper of this extended version to a conference.)

## Prepared Data1 - 5 artificial logs (Small, Medium, Large, Huge, Wide)
We used 5 types of process models including small, medium, large, huge, and wide refered from [2] to generate artificial logs.

## Prepared Data2 - 2 artificial logs (credit-card, mccloud) (named as Credit, Pub in our paper)
We used two process models (credit-card & Pub) refered from [3] to generate artificial logs.

## Prepared Data3 - 2 real-life logs (Road_Traffic, b17)
For the real life logs, we consider (1) the Road Traffic event log which collects events about a road traffic fine management process at a local police authority in Italy and (2) BPIC 2017 which is a benchmard dataset in Process Mining academia.

For all logs, we injected 5 types of anomaly patterns including "insert", "skip", "moved", "replace", and "rework" introduced in [4]. The statistics of datasets are summarised in Table 1 in our paper.

## How To Implement P-BEAR-RL:
- main.py: in terminal, if you run "python main.py --data 'Small' --num_epi 1000 --alpha 0", then you will get a repaired log of the 'Small' data in "~/output" folder.
- pattern_recognition.ipynb: this script will add a prediction of anomalous patterns (i.e., anomalous pattern recognition) to the repaired log in "~/output" folder. Therefore, run this script after you get a result from "main.py".
- see_performance.R : after implementing "pattern_recognition.ipynb", this Rscript summarizes performance (ACC and REC) and save the performance in "~/performance" folder. The entire performance can be see in our paper.

## How To Implement the baselines (Align_TR, Align.ED, DeepAlign):
- For Aligner.TR & Aligner.ED, run ".../alignment/1.implementation_Alignment.py" file, then you will get a repaired log in ".../alignment/result_trd" & "~/alignment/result_edit" folder, respectively.
- For DeepAlign, run ".../DeepAlign/1.implementation_DeepAlign.py" file, then you will get a repaired log in ".../DeepAlign/result" folder. The original code is refered from "https://github.com/tnolle/deepalign".
  
&#x1F53A; Be careful to correctly set your working directory in Python codes and Rscripts.

&#x1F53A; Before running the code, in the folders named as 'normaldata', 'encoded_normal' and 'encoded_anomaly', you may need to put full datasets downloadable in following repository: https://drive.google.com/file/d/1Y9ZxyqzBGjjiRtgRJfm-O4WWZFSYDG3Q/view?usp=sharing

## A detailed performance comparison by each anomalous pattern
![](additional_performance.png)


## References

[1] Ko, J., & Comuzzi, M. (2022). Pattern-based Reconstruction of Anomalous Traces in Business Process Event Logs. Proceedings of the 1st International Workshop on Computational Intelligence for Process Mining (CI4PM) and the 1st International Workshop on Pervasive Artificial Intelligence (PAI), co-located with the IEEE World Congress on Computational Intelligence (WCCI).

[2] Nolle, T., Luettgen, S., Seeliger, A., & Mühlhäuser, M. (2019). Binet: Multi-perspective business process anomaly classification. Information Systems, 101458.

[3] Ko, J., & Comuzzi, M. (2022). Keeping our rivers clean: Information-theoretic online anomaly detection for streaming business process events. Information Systems, 104, 101894.

[4] Ko, J., Lee, J., & Comuzzi, M. (2020). AIR-BAGEL: An Interactive Root cause-Based Anomaly Generator for Event Logs. In ICPM Doctoral Consortium/Tools (pp. 35-38).


 
