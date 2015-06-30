#!/usr/bin/env python
# encoding=utf8

import sys
import splunklib.client as client
import json
import custom_validators
import math

from collections import OrderedDict
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators

def map_score (value, bounds):
    """ Current approach checks if the value is within the bounds. If it is a score of 0 is return otherwise a score of 1.
    A probabilty density function might be used to provide a continuous score instead of a discret score.
    """
    if bounds[0] <= value <= bounds[1]:
        return 0
    else:
        return 1

@Configuration()
class CompareToBaselineCommand(StreamingCommand):
    """ Compare given values using statistical functions to identify an outlier. The 4 different outlier detection methods from the FindOutlier package in R are available.
    extreme Studentized deviation (ESD), Hampel, standard boxplot rule (SBR) and asymmetric standard boxplot rule (ASBR). For further information please check http://www.r-bloggers.com/finding-outliers-in-numerical-data/
    ##Syntax
    .. code-block::
        comparetobaseline config_name=<string> variable=<fieldname>
    ##Description:

    ##Example
    ..code-block::
        index=_internal sourcetype=splunkd_ui_access| bucket span=1d _time | stats avg(date_hour) as avg_hour min(date_hour) as min_hour max(date_hour) as max_hour by user _time | comparetobaseline config_name="usage_hours" variable="user"
    This example provides scores for the avg_hour, min_hour and max_hour columns using the key value entries stored under config_name usage_hours
    :code:`_internal index sourcetype=splunkd_ui_access`.
    """
    config_name = Option(
        doc='''
        **Syntax:** **config_name=***<string>*
        **Description:** Name to be referenced for storing the basic statistics in the kvstore''',
        require=True)

    variable = Option(
        doc='''
        **Syntax:** **variable=***<fieldname>*
        **Description:** variable/column used to aggregate by and calculate the statistical metrics''',
        require=True, validate=validators.Fieldname())

    threshold = Option(
        doc='''
        **Syntax:** **threshold=***<float>*
        **Description:** Provide a custom threshold to make the outlier detection more or less senstive. The default for ESD and Hampel is 3 and the default for SBR and ASBR is 1.5''',
        require=False, validate=custom_validators.Float())

    method = Option(
        doc='''
        **Syntax:** **method=***<OutlierMethod>*
        **Description:** Define the method used to detect outliers. Currently available methods are extreme Studentized deviation (ESD), Hampel, standard boxplot rule (SBR) and asymmetric standard boxplot rule (ASBR). For further information please check http://www.r-bloggers.com/finding-outliers-in-numerical-data/''',
        require=False, validate=custom_validators.OutlierMethod(), default="Hampel")

    debug = Option(
        doc='''
        **Syntax:** **debug=***<boolean>*
        **Description:** show the upper and lower bounds and key value store entry as columns if true. Defaults to false''',
        require=False, validate=validators.Boolean(), default=False)

    collections_data_endpoint = 'storage/collections/data/'
    collection_name = 'hyperbaseline_kv'

    def stream(self, records):
        app_service = client.Service(token=self.input_header["sessionKey"])
        for record in records:
            new_record = OrderedDict()
            for fieldname in record:
                new_record[fieldname] = record[fieldname]
                if fieldname.startswith("_") or fieldname==self.variable:
                    continue
                else:
                    key = self.config_name+"#"+record[self.variable]+"#"+fieldname
                    try:
                        request2 = app_service.request(
                            self.collections_data_endpoint + self.collection_name + "/" + key,
                            method = 'get',
                            headers = [('content-type', 'application/json')],
                            owner = 'nobody',
                            app = 'SA-hyperbaseline'
                        )
                        response_json = json.loads(str(request2["body"]))
                    except:
                        # if no key value store entry is found continue
                        continue
                    if response_json:
                        if self.method == "ESD":
                            # set default threshold if option is empty
                            t = self.threshold or 3
                            #extreme Studentized deviation bounds are [mean - t * SD, mean + t * SD]
                            lower_bound = response_json["mean"] - t * response_json["stdev"]
                            upper_bound = response_json["mean"] + t * response_json["stdev"]
                        elif self.method == "Hampel":
                            # set default threshold if option is empty
                            t = self.threshold or 3
                            # Hampel bounds are [median - t * MAD, median + t * MAD]
                            lower_bound = response_json["median"] - t * response_json["mad"]
                            upper_bound = response_json["median"] + t * response_json["mad"]
                        elif self.method == "SBR":
                            # set default threshold if option is empty
                            c = self.threshold or 1.5
                            # standard boxplot rule bounds are [Q1 - c * IQD, Q3 + c * IQD]
                            # calculate the IQD (inter quartile distance)
                            iqd = response_json["pct75"] - response_json["pct25"]
                            lower_bound = response_json["pct25"] - c * iqd
                            upper_bound = response_json["pct75"] + c * iqd
                        elif self.method == "ASBR":
                            # set default threshold if option is empty
                            c = self.threshold or 1.5
                            a = -4
                            b = 3
                            mc = float(response_json["medcouple"])
                            # asymmetric standard boxplot rule bounds for positive MC are [Q1 – c * exp(a * MC) * IQD, Q3 + c * exp(b * MC) * IQD ]
                            # asymmetric standard boxplot rule bounds for negative MC are [Q1 – c * exp(-b * MC) * IQD, Q3 + c * exp(-a * MC) * IQD ]
                            # calculate the IQD (inter quartile distance)
                            iqd = response_json["pct75"] - response_json["pct25"]
                            if mc >= 0:
                                lower_adjustment_factor = c * math.exp(a * mc) * iqd
                                upper_adjustment_factor = c * math.exp(b * mc) * iqd
                            else:
                                lower_adjustment_factor = c * math.exp(-b * mc) * iqd
                                upper_adjustment_factor = c * math.exp(-a * mc) * iqd
                            lower_bound = response_json["pct25"] - lower_adjustment_factor
                            upper_bound = response_json["pct75"] + upper_adjustment_factor

                        # combine lower and upper bound into a list
                        bounds = [lower_bound, upper_bound]
                        # score the value according to the calculated bounds
                        new_record[fieldname+":score"] = map_score(float(new_record[fieldname]), bounds)
                        # add the bounds and retrieved values if debug is true
                        if self.debug:
                            new_record[fieldname+":bounds"] = bounds
                            new_record[fieldname+":stats"] = response_json
            yield new_record

dispatch(CompareToBaselineCommand, sys.argv, sys.stdin, sys.stdout, __name__)