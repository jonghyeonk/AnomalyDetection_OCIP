
from utils.helpers import filter_time, get_unique, unlist
from datetime import datetime
from itertools import chain
import random
import pandas as pd
from localocpa.objects.log.util import misc as log_util


def dissociative_object(ocel, 
                  tstart: datetime= None, tend: datetime= None,
                  ratio:float= None,
                  object_root:str = None, relevant_attributes:list = None):
    
    ocel_copy = log_util.copy_log(ocel) 
    ocel_copy_timefilter = log_util.copy_log(ocel) 

    step = 1
    if ratio is None:
        ratio = 0.1

    if relevant_attributes is None:
        raise ValueError("Error: relevant event attributes are not given (set the parameter 'relevant_attributes')")

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
    
    df1 = ocel_copy_timefilter.log.log
    df1[name_obj+'_validation'] = df1[name_obj].apply(lambda x: x[0] if len(x)>0 else '' )
    df1 = df1.loc[df1[name_obj+'_validation'] != ''].reset_index(drop=True)
    df1 = df1[[name_obj+'_validation']+ relevant_attributes]

    table_obj = df1.groupby(name_obj+'_validation').apply(lambda x: get_unique(x)).reset_index(drop=True)
    table_obj['variant'] = table_obj.loc[:, table_obj.columns != name_obj+'_validation'].apply(lambda x: str(list(x)), axis=1)
    table_obj_div = table_obj.groupby('variant')[name_obj+'_validation'].apply(lambda x: list(x))

    table_obj_over1 = table_obj_div[table_obj_div.apply(lambda x: len(x)>1)]
    variant_obj_list = list(chain(*table_obj_over1))

    # source_obj_list = []
    target_obj_list = []
    dict_replace = dict()
    for obj_id in variant_obj_list:
        if obj_id not in target_obj_list:
            var_id = table_obj.loc[table_obj[name_obj+'_validation'] == obj_id, 'variant'].reset_index(drop= True)[0]
            obj_ids = table_obj_over1[var_id].copy()
            obj_ids.remove(obj_id)
            target_obj = random.sample(obj_ids, 1)
            target_obj_list.append(target_obj)
            dict_replace[obj_id] = target_obj[0]
        else:
            pass

    if ratio == None:
        obj_sampled = dict_replace
    else:
        keys = random.sample(list(dict_replace.keys()), round(len(dict_replace)* ratio))
        obj_sampled =  {k: dict_replace[k] for k in keys}  
        print("Filtering step", step, ". The number of objects to be filtered: ", len(obj_sampled), " (ratio: ", 100*ratio, "%, total objects: ", len(dict_replace), ")")


    result = ocel_copy.log.log.copy()
    result['label'] = ''
    for key, value in obj_sampled.items():
        loc = (result[object_root].apply(lambda x: unlist(x)==key))
        result[object_root].loc[loc] = [[str(value)] for i in range(sum(loc)) ]
        result['label'].loc[loc] = 'dissociative_object~' + object_root + ':' + str(key)

    errored_ocel = log_util.copy_log_from_df(result ,ocel_copy.parameters)

    return errored_ocel