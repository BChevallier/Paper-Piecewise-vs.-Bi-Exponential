# raw_data-overview
## GeneralData.csv Overview

This file contains physiological and performance data for study participants. Each row represents an individual, with columns detailing demographic, anthropometric, and exercise-related variables.

### Columns Description

| Column Name    | Brief Description                        | Unit (to be filled) |
| -------------- | ---------------------------------------- | ------------------- |
| ID             | Participant identifier                   | -                   |
| sex            | Biological sex (male/female)             | -                   |
| age            | Age of participant                       | *y*                 |
| body_mass      | Body mass                                | *kg*                |
| group          | Experimental/training group              | -                   |
| o2_intercept   | Oxygen intercept value                   | *mL[O2]/min*        |
| o2_slope       | Oxygen slope value                       | *mL[O2]/min*        |
| o2_intercept_y | Y-intercept of oxygen variable           | *mL[O2]/min*        |
| o2_slope_y     | Slope of oxygen variable                 | *mL[O2]/min*        |
| tt4_d          | Distance run in 4min-timetrial           | *m*                 |
| t_100          | Time needed to sprint 100m               | *s*                 |
| mss            | Max sprint speed                         | *m/s*               |
| cmj            | Countermovement jump height              | *cm*                |
| D              | D-Prime (critical-speed-Model)           | *m*                 |
| asr            | Anaerobic speed reserve                  | *m/s*               |
| srr            | Speed reserve ratio                      | -                   |
| vo2_max_abs    | Absolute VO2 max                         | *L[O2]/min*         |
| re_14          | Running economy at 14 (context-specific) | *mL[O2]/kg/km*      |
| mas            | Maximal aerobic speed                    | *m/s*               |
| v_3            | Speed at 3 mmol lactat                   | *m/s*               |
| cs             | Critical speed                           | *m/s*               |


---


## TimeTrial.csv Overview

This file contains time-series data for each participant during a 4 min time-trial.  
Each column (after the first) corresponds to a participant, and each row represents a time point.

### Columns Description

| Column Name | Brief Description                               | Unit        |
| ----------- | ----------------------------------------------- | ----------- |
| time        | Time stamp for the measurement (e.g., mm:ss)    | *min:sec*   |
| SP2206      | Measurement for participant SP2206 at this time | *L[O2]/min* |
| HS2601      | Measurement for participant HS2601 at this time | *L[O2]/min* |
| FF1107      | Measurement for participant FF1107 at this time | *L[O2]/min* |
| ...         | ...                                             | ...         |
