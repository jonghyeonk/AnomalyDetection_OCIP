from localocpa.algo.discovery.ocpn.versions import inductive
from localocpa.objects.log.ocel import OCEL
from localocpa.objects.log.variants.obj import ObjectCentricEventLog
import localocpa.objects.log.converter.factory as convert_factory
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

INDUCTIVE = "inductive"

VERSIONS = {INDUCTIVE: inductive.apply}

def discover_alpha(log):
    return alpha_miner.apply(log)
def discover_inductive(log):
    return inductive_miner.apply(log)


def apply(ocel, variant=INDUCTIVE,discovery_algorithm= 'a', parameters=None):
    if type(ocel) == OCEL:
        return VERSIONS[variant](ocel.log.log, discovery_algorithm=discovery_algorithm, parameters=parameters)
    if type(ocel) == ObjectCentricEventLog:
        df, _ = convert_factory.apply(ocel, variant='json_to_mdl')
        return VERSIONS[variant](df, parameters=parameters)
    else:
        return VERSIONS[variant](ocel, parameters=parameters)
