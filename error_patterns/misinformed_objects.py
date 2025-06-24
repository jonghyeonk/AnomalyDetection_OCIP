from utils.helpers import filter_time, unlist, label, inconsistency_categorical, inconsistency_numeric
from datetime import datetime
import random
from localocpa.objects.log.util import misc as log_util
from scipy.stats import pearsonr
from itertools import chain
import pandas as pd


def misinformed_objects(ocel,
                  tstart: datetime= None, tend: datetime= None,
                  ratio:float= None,
                  related_attributes:list = None,
                  level:str = 'event'):
    
    ocel_copy = log_util.copy_log(ocel) 
    ocel_copy_timefilter = log_util.copy_log(ocel) 
    step = 1
    if ratio is None:
        ratio = 0.1

    name_attr = related_attributes[0]
    name_attr_related = related_attributes[1]

    df1 = ocel_copy.log.log[[name_attr, name_attr_related]]
    df1 = df1.dropna()
    df1 = df1.reset_index(drop = True)

    rs = pearsonr(df1[name_attr], df1[name_attr_related])
    print("Correlation analysis between", str(related_attributes), ":", rs)
    if rs.pvalue > 0.05:
        raise ValueError("Error: the two attributes are not correlated (p-value is higher than 0.05)")

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
            valid_idx = (trace[[name_attr,name_attr_related]].isna().apply(sum, 1) == 0)

            if trace[name_attr_related].dtype == float:
                if trace[name_attr].dtype == object:
                    error = inconsistency_categorical(trace, valid_idx, df1, name_attr, name_attr_related, level =level ,confidence = 0.999)
                    trace['label'] = trace[name_attr_related].apply(lambda x: label(x, 'misinformed_objects~' + name_attr_related +':', post = False, list =False) )
                    trace.loc[valid_idx, [name_attr_related]] = error
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)
                else:
                    error = inconsistency_numeric(trace, valid_idx, df1, name_attr, name_attr_related, level =level ,confidence = 0.999)
                    trace['label'] = trace[name_attr_related].apply(lambda x: label(x, 'misinformed_objects~' + name_attr_related +':', post = False, list =False) )
                    trace.loc[valid_idx, [name_attr_related]] = error
                    result_in = pd.concat([result_in, trace]).reset_index(drop=True)
            else:
                trace['label'] = trace[name_attr_related].apply(lambda x: label(x, 'misinformed_objects~' + name_attr_related +':', post = False, list =False) )
                df1[name_attr_related].unique()
                list_label = df1[name_attr].unique().tolist()
                trace['label'] = trace[name_attr_related].apply(lambda x: label(x, 'misinformed_objects~' + name_attr_related +':', post = False, list =False) )

                if level == 'event':
                    error = trace.loc[valid_idx, name_attr_related].apply(lambda x: random.sample( [label for label in list_label if label!=x], 1)[0], 1).tolist()
                    trace.loc[valid_idx, [name_attr_related]] = error
                if level == 'case':
                    val = random.sample(  trace.loc[valid_idx, name_attr_related].tolist(), 1)[0]
                    trace[valid_idx, name_attr_related] = random.sample( [label for label in list_label if label!=val], 1)[0]

            result_in = pd.concat([result_in, trace]).reset_index(drop=True)
        else:
            pass

    result_out = ocel_copy.log.log.loc[~ocel_copy.log.log['event_id'].isin(target_events_all)].reset_index(drop = True)
    result_out['label'] = ''

    result = pd.concat([result_in, result_out]).reset_index(drop=True)

    errored_ocel = log_util.copy_log_from_df(result ,ocel_copy.parameters)


    return errored_ocel