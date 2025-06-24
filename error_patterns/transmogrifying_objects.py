
from utils.helpers import filter_time, unlist, label
from datetime import datetime
import random
from localocpa.objects.log.util import misc as log_util
import pandas as pd
import numpy as np
from itertools import chain
from sklearn.linear_model import LinearRegression


def transmogrifying_objects(ocel, 
                            tstart: datetime= None, tend: datetime= None,
                            ratio:float= None,
                            temporal_attribute:str = None,
                            constant_attribute:str = None):
    

    if (temporal_attribute == None) & (constant_attribute == None):
        raise ValueError("Error: constant_attribute & constant_attribute are not given")

    ocel_copy = log_util.copy_log(ocel) 
    ocel_copy_timefilter = log_util.copy_log(ocel) 

    step = 1

    if ratio is None:
        ratio = 0.1

    if (tstart == None) & (tend == None):
        data = ocel_copy_timefilter.log.log
    else:
        data = filter_time(ocel_copy_timefilter, tstart, tend)
        data = data.reset_index(drop=True)
        if data.empty:
            raise ValueError("Error: no matched events in the time interval")
        else:
            print("Filtering step", step, ". The number of process executions in the time interval (", tstart, ",", tend ,"): ", len(data))
        step += 1

    ocel_copy_timefilter= log_util.copy_log_from_df(data ,ocel_copy_timefilter.parameters)

    trace_id = list(chain(*ocel_copy_timefilter.variants_dict.values()))

    if ratio == None:
        trace_sampled = trace_id
    else:
        trace_sampled = random.sample(trace_id, round(len(trace_id)* ratio))
        print("Filtering step", step, ". The number of process executions to be filtered: ", len(trace_sampled),
               " (ratio: ", 100*ratio, "%, total process executions: ", len(trace_id), ")")

    ocel_copy.log.log['UNIX'] = ocel_copy.log.log[ocel_copy.parameters['time_name']].astype('int64')

    result_in = pd.DataFrame()
    target_events_all = []
    for id in trace_sampled:
        target_events = list(ocel_copy.process_executions[id])
        if len(target_events)>1:
            target_events_all = target_events_all + target_events
            trace = ocel_copy.log.log.loc[ocel_copy.log.log['event_id'].isin(target_events)].reset_index(drop = True)

            if temporal_attribute != None:
                valid_idx = (trace[[temporal_attribute]].isna().apply(sum, 1) == 0)
                if sum(valid_idx) > 2:
                    x = trace[valid_idx, ['UNIX']]
                    y = trace[valid_idx, [temporal_attribute]] 
                    model = LinearRegression()
                    model.fit(x, y)
                    valid_idx2 = valid_idx[valid_idx].index
                    target_idx = random.sample(list(valid_idx2), 1)[0]
                    error = model.predict(trace.iloc[target_idx]['UNIX'] - 3.154e+7)
                    
                    trace['label'] = trace[temporal_attribute].apply(lambda x: label(x, 'transmogrifying_objects(temporal)~' + temporal_attribute +':', post = False, list =False) )
                    trace.loc[target_idx, constant_attribute] = error
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)
                else:
                    trace['label'] = ''
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)

            if constant_attribute != None:
                valid_idx = (trace[[constant_attribute]].isna().apply(sum, 1) == 0)
                if sum(valid_idx) > 2:
                    valid_idx2 = valid_idx[valid_idx].index
                    target_idx = random.sample(list(valid_idx2), 1)[0]
                    
                    values = trace.loc[valid_idx, [constant_attribute]] 
                    mean = np.mean(values)
                    sd = np.std(values)
                    if sd.values[0] == 0:
                        error = mean * 10
                    else:
                        error = mean + sd*3.3
                    trace['label'] = trace[constant_attribute].apply(lambda x: label(x, 'transmogrifying_objects(constant)~' + constant_attribute +':', post = False, list =False) )
                    trace.loc[target_idx, constant_attribute] = error
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)
                else:
                    trace['label'] = ''
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)

    result_out = ocel_copy.log.log.loc[~ocel_copy.log.log['event_id'].isin(target_events_all)].reset_index(drop = True)
    result_out['label'] = ''

    result = pd.concat([result_in, result_out]).reset_index(drop=True)

    errored_ocel = log_util.copy_log_from_df(result ,ocel_copy.parameters)


    return errored_ocel