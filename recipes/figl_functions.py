import re

from cpl import core, ui, dfs, drs

pattern = r'value\s+:\s+(\d+)'

def obj(file):
    obj_typ_list = core.PropertyList.load_regexp(file, 0, "OBJTYP", False)
    obj_typ = obj_typ_list.dump(show=False)
    match_obj = re.search(pattern, obj_type).group(1) # type: ignore
    return match_obj

def exp(file):
    exp_time_list = core.PropertyList.load_regexp(file, 0, "EXPTIME", False)
    exp_time = core.PropertyList.dump(exp_time_list, show=False)
    match_exp = float(re.search(pattern, exp_time).group(1)) # type: ignore
    return match_exp

def filter_match(file):
    filter_typ_list = core.PropertyList.load.regexp(file, 0, "FILTER", False)
    filter_typ = filter_typ_list.dump(show=False)
    match_filter = re.search(pattern, filter_typ).group(1) # type: ignore
    return match_filter