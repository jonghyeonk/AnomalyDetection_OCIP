
from utils.helpers import filter_time, unlist
from datetime import datetime
import random
from localocpa.objects.log.util import misc as log_util


def false_memory(ocel, 
                  tstart: datetime= None, tend: datetime= None,
                  ratio:float= None,
                  related_objects:list = None):
    
    ocel_copy = log_util.copy_log(ocel) 
    ocel_copy_timefilter = log_util.copy_log(ocel) 

    step = 1
    if ratio is None:
        ratio = 0.1

    name_obj = related_objects[0]
    name_obj_related = related_objects[1]

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
    
    df1 = ocel_copy_timefilter.log.log[ocel_copy_timefilter.object_types]
    df1[name_obj] = df1[name_obj].apply(lambda x: unlist(x))
    df1[name_obj_related] = df1[name_obj_related].apply(lambda x: unlist(x))
    corr = df1.drop_duplicates().reset_index(drop=True)
    corr = corr.loc[(corr[name_obj] != '') & (corr[name_obj_related] != '') ]
    dict_replace = dict(corr.values)

    if ratio == None:
        obj_sampled = dict_replace
    else:
        keys = random.sample(list(dict_replace.keys()), round(len(dict_replace)* ratio))
        obj_sampled =  {k: dict_replace[k] for k in keys}  
        print("Filtering step", step, ". The number of object relations to be perturbed by false-memory: ", len(obj_sampled), " (ratio: ", 100*ratio, "%, total object relations: ", len(dict_replace), ")")

    result = ocel_copy.log.log.copy()
    result['label'] = ''
    for key, value in obj_sampled.items():
        loc1 = (result[name_obj].apply(lambda x: unlist(x)==key))
        loc2 = (result[name_obj_related].apply(lambda x: unlist(x)==value))

        false = random.sample(sorted(dict_replace.values()),1)[0]
        while false == value: # if it is not false by chance, resample it
            false = random.sample(sorted(dict_replace.values()),1)[0]

        result[name_obj_related].loc[loc1&loc2] = [[str(false)] for i in range(sum(loc1&loc2)) ]
        result['label'].loc[loc1&loc2] = 'false_memory:' + name_obj_related + ":" + str(value)

    errored_ocel = log_util.copy_log_from_df(result ,ocel_copy.parameters)
    return errored_ocel