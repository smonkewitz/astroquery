# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import json
import os
from astropy.utils.data import download_file
from astropy.io import ascii
import astropy.units as u

__all__ = ['ExoplanetArchive']

EXOPLANETS_CSV_URL = ('http://exoplanetarchive.ipac.caltech.edu/cgi-bin/'
                      'nstedAPI/nph-nstedAPI?table=exoplanets')
TIME_ATTRS = {'rowupdate': 'iso'}
BOOL_ATTRS = ('pl_kepflag', 'pl_ttvflag', 'pl_k2flag', 'st_massblend',
              'st_optmagblend', 'st_radblend', 'st_teffblend')


class ExoplanetArchiveClass(object):
    def __init__(self):
        self._param_units = None
        self._table = None

    @property
    def param_units(self):
        if self._param_units is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            units_file = open(os.path.join(module_dir, 'data',
                                           'exoplanet_nexsci_units.json'))
            self._param_units = json.load(units_file)

        return self._param_units

    def get_table(self, cache=True, show_progress=True):
        """
        Download (and optionally cache) the `NExScI Exoplanet Archive Confirmed
        Planets table <http://exoplanetarchive.ipac.caltech.edu/index.html>`_.
        Parameters
        ----------
        cache : bool (optional)
            Cache exoplanet table to local astropy cache? Default is `True`.
        show_progress : bool (optional)
            Show progress of exoplanet table download (if no cached copy is
            available). Default is `True`.
        Returns
        -------
        table : `~astropy.table.Table`
            Table of exoplanet properties.
        """
        if self._table is None:
            table_path = download_file(EXOPLANETS_CSV_URL, cache=cache,
                                       show_progress=show_progress)
            exoplanets_table = ascii.read(table_path)

            # Group by the host name
            exoplanets_table.group_by('pl_hostname')

            # Store column of lowercase names for indexing:
            lowercase_names = [' '.join([host_name.lower(), letter])
                               for host_name, letter in
                               zip(exoplanets_table['pl_hostname'].data,
                                   exoplanets_table['pl_letter'].data)]
            exoplanets_table['NAME_LOWERCASE'] = lowercase_names
            exoplanets_table.add_index('NAME_LOWERCASE')

            # Assign units to columns where possible
            for col in exoplanets_table.colnames:
                if col in self.param_units:
                    exoplanets_table[col].unit = u.Unit(self.param_units[col])

            self._table = exoplanets_table

        return self._table

    def query_planet(self, planet_name):
        """
        Get table of exoplanet properties.

        Parameters
        ----------
        planet_name : str
            Name of planet

        Return
        ------
        table : `~astropy.table.Table`
            Table of one exoplanet's properties.
        """
        exoplanet_table = self.get_table()
        return exoplanet_table.loc[planet_name.strip().lower()]

ExoplanetArchive = ExoplanetArchiveClass()
