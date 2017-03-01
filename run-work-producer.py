#!/usr/bin/python
# -*- coding: UTF-8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
# Tommaso Stella <tommaso.stella@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file has been created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import time
import os
import math
import json
import csv
#import copy
from StringIO import StringIO
from datetime import date, datetime, timedelta
from collections import defaultdict
#import types
import sys
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Release")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\project-files\\Win32\\Debug")
#sys.path.insert(0, "C:\\Users\\berg.ZALF-AD\\GitHub\\monica\\src\\python")
#sys.path.insert(0, "C:\\Program Files (x86)\\MONICA")
print sys.path
#sys.path.append('C:/Users/berg.ZALF-AD/GitHub/util/soil')
#from soil_conversion import *
#import monica_python
import zmq
print "pyzmq version: ", zmq.pyzmq_version(), " zmq version: ", zmq.zmq_version()

import monica_io
#print "path to monica_io: ", monica_io.__file__

#print "sys.path: ", sys.path
#print "sys.version: ", sys.version

USER = "berg2"
LOCAL_RUN = False

PATHS = {
    "stella": {
        "INCLUDE_FILE_BASE_PATH": "C:/Users/stella/Documents/GitHub",
        "LOCAL_ARCHIVE_PATH_TO_PROJECT": "Z:/projects/macsur-scaling-cc-nrw/",
        "ARCHIVE_PATH_TO_PROJECT": "/archiv-daten/md/projects/macsur-scaling-cc-nrw/"
    },
    "berg": {
        "INCLUDE_FILE_BASE_PATH": "C:/Users/berg.ZALF-AD.000/Documents/GitHub",
        "LOCAL_ARCHIVE_PATH_TO_PROJECT": "P:/macsur-scaling-cc-nrw/",
        "ARCHIVE_PATH_TO_PROJECT": "/archiv-daten/md/projects/macsur-scaling-cc-nrw/"
    },
    "berg2": {
        "INCLUDE_FILE_BASE_PATH": "C:/Users/berg.ZALF-AD/GitHub",
        "LOCAL_ARCHIVE_PATH_TO_PROJECT": "P:/macsur-scaling-cc-nrw/",
        "ARCHIVE_PATH_TO_PROJECT": "/archiv-daten/md/projects/macsur-scaling-cc-nrw/"
    }
}

def main():
    "main"

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    #port = 6666 if len(sys.argv) == 1 else sys.argv[1]
    config = {
        "port": 6666,
        "start": 1,
        "end": 8157
    }
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            k,v = arg.split("=")
            if k in config:
                config[k] = int(v) 

    if LOCAL_RUN:
        socket.connect("tcp://localhost:" + str(config["port"]))
    else:
        socket.connect("tcp://cluster2:" + str(config["port"]))

    with open("sim.json") as _:
        sim = json.load(_)

    with open("site.json") as _:
        site = json.load(_)

    with open("crop.json") as _:
        crop = json.load(_)

    with open("sims.json") as _:
        sims = json.load(_)

    sim["include-file-base-path"] = PATHS[USER]["INCLUDE_FILE_BASE_PATH"]

    period_gcms = [
        {"grcp": "0", "period": "0", "gcm-rcp": "0_0"},
        {"grcp": "1", "period": "2", "gcm-rcp": "GFDL-CM3_45"},
        {"grcp": "2", "period": "2", "gcm-rcp": "GFDL-CM3_85"},
        {"grcp": "3", "period": "2", "gcm-rcp": "GISS-E2-R_45"},
        {"grcp": "4", "period": "2", "gcm-rcp": "GISS-E2-R_85"},
        {"grcp": "5", "period": "2", "gcm-rcp": "HadGEM2-ES_26"},
        {"grcp": "6", "period": "2", "gcm-rcp": "HadGEM2-ES_45"},
        {"grcp": "7", "period": "2", "gcm-rcp": "HadGEM2-ES_85"},
        {"grcp": "8", "period": "2", "gcm-rcp": "MIROC5_45"},
        {"grcp": "9", "period": "2", "gcm-rcp": "MIROC5_85"},
        {"grcp": "10", "period": "2", "gcm-rcp": "MPI-ESM-MR_26"},
        {"grcp": "11", "period": "2", "gcm-rcp": "MPI-ESM-MR_45"},
        {"grcp": "12", "period": "2", "gcm-rcp": "MPI-ESM-MR_85"},
        {"grcp": "1", "period": "3", "gcm-rcp": "GFDL-CM3_45"},
        {"grcp": "2", "period": "3", "gcm-rcp": "GFDL-CM3_85"},
        {"grcp": "3", "period": "3", "gcm-rcp": "GISS-E2-R_45"},
        {"grcp": "4", "period": "3", "gcm-rcp": "GISS-E2-R_85"},
        {"grcp": "5", "period": "3", "gcm-rcp": "HadGEM2-ES_26"},
        {"grcp": "6", "period": "3", "gcm-rcp": "HadGEM2-ES_45"},
        {"grcp": "7", "period": "3", "gcm-rcp": "HadGEM2-ES_85"},
        {"grcp": "8", "period": "3", "gcm-rcp": "MIROC5_45"},
        {"grcp": "9", "period": "3", "gcm-rcp": "MIROC5_85"},
        {"grcp": "10", "period": "3", "gcm-rcp": "MPI-ESM-MR_26"},
        {"grcp": "11", "period": "3", "gcm-rcp": "MPI-ESM-MR_45"},
        {"grcp": "12", "period": "3", "gcm-rcp": "MPI-ESM-MR_85"},
    ]

    start_year = {
        "0": "1980",
        "2": "2040",
        "3": "2070"
    }

    def read_latitude(filename):
        ""
        defs = defaultdict(list)
        lats = {}
        with open(filename) as _:
            reader = csv.reader(_)
            reader.next()
            for row in reader:
                res = int(row[1])
                if res < 25:
                    continue
                row_col = (int(row[2]), int(row[3]))
                lat = float(row[13])
                lats[row_col] = lat
                defs[res].append(lat)

            for res, vals in defs.iteritems():
                lats[(res, -1)] = sum(vals) / len(vals)

            return lats
        
    latitudes = read_latitude(PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "Soil_data/add_x_y_lon_lat_ele_centred.csv")


    def read_lookup_file(filename): 
        ""
        lll = []
        with open(filename) as _:
            reader = csv.reader(_)
            reader.next()
            for row in reader:
                lll.append({
                    25: (int(row[0]), int(row[1])),
                    50: (int(row[2]), int(row[3])),
                    100: (int(row[4]), int(row[5]))
                  })
            return lll

    lookup = read_lookup_file(PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "/unit_description/MCSUR_NRW_CC_cell_lookup.csv")


    def read_soil_properties(filename):
        ""
        soil = defaultdict(list)
        with open(filename) as _:
            reader = csv.reader(_)
            reader.next()
            for row in reader:
                row_col = (int(row[3]), int(row[2]))
                #skip horizons with no properties defined
                if float(row[45]) <= 0.00001:
                    continue
                #avoid BD to be too low (soilT crashes)
                bulk_d = max(600.0, float(row[32]) * 1000)
                soil[row_col].append({
                    "depth": float(row[15]),
                    "thickness": float(row[16]),
                    "pwp": float(row[44]),
                    "fc": float(row[45]),
                    "sat": float(row[46]),
                    "corg": float(row[34]),
                    "bulk-density": bulk_d,
                    "sand": float(row[29]) / 100.0,
                    "clay": float(row[27]) / 100.0,
                    "ph": float(row[36]),
                    "sceleton": float(row[31]) / 100.0
                })
            return soil

    soil = {
        25: read_soil_properties(PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "Soil_data/climate_change_NRW_soil_r25.csv"),
        50: read_soil_properties(PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "Soil_data/climate_change_NRW_soil_r50.csv"),
        100: read_soil_properties(PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "Soil_data/climate_change_NRW_soil_r100.csv")
    }


    def update_soil(soil_res, row, col, crop_id):
        "update function"

        crop["cropRotation"][2] = crop_id

        soil_layers = soil[soil_res][(row, col)]

        site["Latitude"] = latitudes[(row, col)] if (row, col) in latitudes else latitudes[(soil_res, -1)]

        layers = []
        profile_depth = 0
        for iii, layer in enumerate(soil_layers):
            lll = {
                "SoilOrganicCarbon": [layer["corg"], "%"],
                "SoilBulkDensity": [layer["bulk-density"], "kg m-3"],
                "FieldCapacity": [layer["fc"], "m3 m-3"],
                "PermanentWiltingPoint": [layer["pwp"], "m3 m-3"],
                "PoreVolume": [layer["sat"], "m3 m-3"],
                "SoilMoisturePercentFC": [80.0 if crop_id == "M" else 50.0, "% [0-100]"],
                "Sand": layer["sand"],
                "Clay": layer["clay"],
                "Sceleton": layer["sceleton"],
                "pH": layer["ph"],
                "Thickness": layer["thickness"]
            }
            profile_depth = layer["depth"]

            #!!!! danger, this is changing in memory sims events structure and events can only then be assigned to env
            sims["output"][crop_id][1][6][1][1] = int(min(math.ceil(profile_depth * 10), 20))

            layers.append(lll)

        site["SiteParameters"]["SoilProfileParameters"] = layers
        return profile_depth
        #print site["SiteParameters"]["SoilProfileParameters"]


    #assert len(row_cols) == len(pheno["GM"].keys()) == len(pheno["WW"].keys())
    #print "# of rowsCols = ", len(row_cols)

    climate_to_soil = [
        {"step": 1, "climate": 25, "soil": 25},
        {"step": 1, "climate": 25, "soil": 50},
        {"step": 1, "climate": 25, "soil": 100},
        {"step": 2, "climate": 50, "soil": 25},
        {"step": 2, "climate": 100, "soil": 25},
        {"step": 3, "climate": 50, "soil": 50},
        {"step": 3, "climate": 100, "soil": 100}
    ]


    production_situations = {
        "PLP": {"water-response": False, "nitrogen-response": False},
        "PLW": {"water-response": True, "nitrogen-response": False},
        "PLN": {"water-response": True, "nitrogen-response": True}
    }

    i = 1
    start_store = time.clock()
    #start = config["start"] - 1
    #end = config["end"] - 1
    #row_cols_ = row_cols[start:end+1]
    #print "running from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]

    for c2s in climate_to_soil:

        step = c2s["step"]
        climate_resolution = c2s["climate"]
        soil_resolution = c2s["soil"]

        climate_to_soils = defaultdict(set)
        for mmm in lookup:
            climate_to_soils[mmm[climate_resolution]].add(mmm[soil_resolution])

        print "step: ", step, " ", len(climate_to_soils), " runs in climate_res: ", climate_resolution, " and soil_res: ", soil_resolution

        for climate_coord, soil_coords in climate_to_soils.iteritems():

            for row, col in soil_coords:

                for crop_id in ["W", "M"]:
                    rootdepth_soillimited = update_soil(soil_resolution, row, col, crop_id)
                    env = monica_io.create_env_json_from_json_config({
                        "crop": crop,
                        "site": site,
                        "sim": sim,
                        "climate": ""
                    })

                    env["csvViaHeaderOptions"] = sim["climate.csv-options"]
                    env["events"] = sims["output"][crop_id]
                    for workstep in env["cropRotation"][0]["worksteps"]:
                        if workstep["type"] == "Seed":
                            current_rootdepth = float(workstep["crop"]["cropParams"]["cultivar"]["CropSpecificMaxRootingDepth"])
                            workstep["crop"]["cropParams"]["cultivar"]["CropSpecificMaxRootingDepth"] = min(current_rootdepth, rootdepth_soillimited)
                            break
                    
                    for production_id, switches in production_situations.iteritems():

                        env["params"]["simulationParameters"]["WaterDeficitResponseOn"] = switches["water-response"]
                        env["params"]["simulationParameters"]["NitrogenResponseOn"] = switches["nitrogen-response"]

                        for period_gcm in period_gcms:

                            grcp = period_gcm["grcp"]
                            period = period_gcm["period"]
                            gcm = period_gcm["gcm-rcp"]

                            #if period != "0":
                            #    continue
                            #if climate_resolution != 25:
                            #    continue
                            #if soil_resolution != 25:
                            #    continue
                            #if crop_id != "W":
                            #    continue

                            if period != "0":
                                climate_filename = "daily_mean_P{}_GRCP_{}_RES{}_C0{}R{}.csv".format(period, grcp, climate_resolution, col, row)
                            else:
                                climate_filename = "daily_mean_P{}_RES{}_C0{}R{}.csv".format(period, climate_resolution, col, row)
                                
                            if LOCAL_RUN:
                                env["pathToClimateCSV"] = PATHS[USER]["LOCAL_ARCHIVE_PATH_TO_PROJECT"] + "Climate_data/NRW_weather_climate_change_v3/res_" + str(climate_resolution) + "/period_" + period + "/GRCP_" + grcp + "/" + climate_filename
                            else:
                                env["pathToClimateCSV"] = PATHS[USER]["ARCHIVE_PATH_TO_PROJECT"] + "Climate_data/NRW_weather_climate_change_v3/res_" + str(climate_resolution) + "/period_" + period + "/GRCP_" + grcp + "/" + climate_filename

                            #initialize nitrate/ammonium in soil layers at start of simulation 
                            #for i in range(3):
                            #    env["cropRotation"][0]["worksteps"][i]["date"] = start_year[period] + "-01-01"

                            env["customId"] = crop_id \
                                                + "|" + str(climate_resolution) \
                                                + "|(" + str(climate_coord[0]) + "/" + str(climate_coord[1]) + ")" \
                                                + "|" + str(soil_resolution) \
                                                + "|(" + str(row) + "/" + str(col) + ")" \
                                                + "|" + period \
                                                + "|" + grcp \
                                                + "|" + gcm \
                                                + "|" + production_id

                            #with open("envs/env-"+str(i)+".json", "w") as _:
                            #    _.write(json.dumps(env))

                            socket.send_json(env)
                            print "sent env ", i, " customId: ", env["customId"]
                            #exit()
                            i += 1


    stop_store = time.clock()

    print "sending ", (i-1), " envs took ", (stop_store - start_store), " seconds"
    #print "ran from ", start, "/", row_cols[start], " to ", end, "/", row_cols[end]
    return


main()