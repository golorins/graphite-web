# -*- coding: utf-8 -*-
# SIA Custom metric functions

import re

from graphite.functions.params import Param, ParamTypes
from graphite.util import epoch, epoch_to_dt, timestamp, deltaseconds
from graphite.render.glyph import format_units
from graphite.render.datalib import TimeSeries


def lowestMin(requestContext, seriesList, n):
  """
  Takes one metric or a wildcard seriesList followed by an integer N.

  Out of all metrics passed, draws only the N metrics with the lowest minimum
  value in the time period specified.

  Example:

  .. code-block:: none

    &target=lowestMin(server*.instance*.threads.busy,5)

  Draws the top 5 servers who have had the least busy threads during the time
  period specified.

  """
  result_list = sorted( seriesList, key=lambda s: min(s) )[:n]

  return sorted(result_list, key=lambda s: min(s))

lowestMin.group = 'CustomSIA'
lowestMin.params = [
  Param('seriesList', ParamTypes.seriesList, required=True),
  Param('n', ParamTypes.integer, required=True),
]



def constantSeries(requestContext, value, seconds=10 ):
  """
  Takes a value and an optional step in seconds (default 10)

  Return a timeseries with constant values from start to end every step seconds.
  If the string 'null' is passed as value the series returned contains None
  Usefull companion for the fallbackSeries function
  
  Example:

  .. code-block:: none

    &target=constantSeries(123.456)
    &target=constantSeries(0, 30)
    &target=constantSeries('null', 60)

  """
  name = "constantSeries(%s)" % str(value)
  start = int(epoch( requestContext['startTime'] ) )
  end = int(epoch( requestContext['endTime'] ) )

  if value == "null":
    value=None
  values = []
  for k in (range(start, end, seconds)):
    values.append(value)
  
  series = TimeSeries(str(value), start, end, seconds, values)
  series.pathExpression = name
  return [series]

constantSeries.group = 'CustomSIA'
constantSeries.params = [
  Param('value', ParamTypes.float, required=True),
  Param('seconds', ParamTypes.integer, required=True),
]



def aliasByNode(requestContext, seriesList, *nodes):
  """
  Takes a seriesList and applies an alias derived from one or more "node"
  portion/s of the target name. Node indices are 0 indexed.
  Strings passed in nodes list are used for the corresponding position in the target name 

  .. code-block:: none

    &target=aliasByNode(ganglia.*.cpu.load5,1)
    &target=aliasByNode(ganglia.*.cpu.load5,"server",1)

  """
  if isinstance(nodes, int):
    nodes=[nodes]
  for series in seriesList:
    metric_pieces = re.search('(?:.*\()?(?P<name>[-\w*\.]+)(?:,|\)?.*)?',series.name).groups()[0].split('.')
    series.name = ".".join( metric_pieces[n] if isinstance(n,int) else n  for n in nodes)    
  return seriesList

aliasByNode.group = 'CustomSIA'
aliasByNode.params = [
  Param('seriesList', ParamTypes.seriesList, required=True),
  Param('nodes', ParamTypes.nodeOrTag, required=True, multiple=True),
]




SeriesFunctions = {
  # Combine functions
  'lowestMin': lowestMin,
  'constantSeries': constantSeries,
  'aliasByNode': aliasByNode,
}

