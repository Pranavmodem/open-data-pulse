"""Every source the pipeline runs, in README order."""

from pipeline.sources import ai, data_eng, tech, world

SOURCES = ai.SOURCES + data_eng.SOURCES + tech.SOURCES + world.SOURCES
