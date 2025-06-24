from utils.helpers import filter_time, label
from datetime import datetime
from itertools import chain
import random
import pandas as pd
from localocpa.objects.log.util import misc as log_util
import ast


def object_clones(ocel,
                  tstart: datetime= None, tend: datetime= None,
                  ratio:float= None,
                  object_root:str = None):
    
    ocel_copy = log_util.copy_log(ocel) 
    ocel_copy_timefilter = log_util.copy_log(ocel) 

    step = 1
    if ratio is None:
        ratio = 0.1

    name_obj = object_root

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
        print("Filtering step", step, ". The number of process executions to be filtered: ", len(trace_sampled), " (ratio: ", 100*ratio, "%, total process executions: ", len(trace_id), ")")

    result_in = pd.DataFrame()
    target_events_all = []
    for id in trace_sampled:
        target_events = list(ocel_copy.process_executions[id])

        if len(target_events)>1:
            target_events_all = target_events_all + target_events
            trace = ocel_copy.log.log.loc[ocel_copy.log.log['event_id'].isin(target_events)].reset_index(drop = True)
            cut_idx = random.sample(range( 1, len(trace)), 1 )[0]
            trace['label'] = trace[name_obj].apply(lambda x: label(x, 'object_clones~' + object_root +':', post = False, list =False) )
            trace_pre = trace[:cut_idx]
            trace_post = trace[cut_idx:]
            trace_post[name_obj] = trace_post[name_obj].apply(lambda x: label(x, '_clone', post = True) )
            
            result_in = pd.concat([result_in, trace_pre, trace_post]).reset_index(drop=True)
        else:
            pass

    result_out = ocel_copy.log.log.loc[~ocel_copy.log.log['event_id'].isin(target_events_all)].reset_index(drop = True)
    result_out['label'] = ''

    result = pd.concat([result_in, result_out]).reset_index(drop=True)

    errored_ocel = log_util.copy_log_from_df(result ,ocel_copy.parameters)

    return errored_ocel