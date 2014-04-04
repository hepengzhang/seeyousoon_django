'''
Created on Mar 30, 2014

@author: Hepeng
'''

import math

def boundsOfCenter(centerLat, centerLong, radius=500):
    boundsLat = boundsOfLat(centerLat, radius)
    boundsLong = boundsOfLong(centerLong, radius)
    return (boundsLat[0], boundsLat[1], boundsLong[0], boundsLong[1])

def boundsOfLat(centerLat, radius=500):
    dlat = 111132.954 - 559.822 * math.cos(math.radians(2 * centerLat)) + 1.175 * math.cos(math.radians(4 * centerLat))
    mag = radius / dlat
    return (centerLat - mag, centerLat + mag)

def boundsOfLong(centerLong, radius=500):
    dlong = 111412.84 * math.cos(math.radians(centerLong)) - 93.5 * math.cos(math.radians(3 * centerLong))
    mag = radius / dlong
    return (centerLong - mag, centerLong + mag)