#!/usr/bin/env python
# coding: utf-8

import random
from functools import partial
from ipywidgets import Output, DOMWidget
from typing_extensions import TypedDict
from traitlets import Unicode, Dict, Bunch
from IPython.display import SVG, display
from typing import List, Optional, Any, Union
from ._frontend import module_name, module_version


class Track(TypedDict):
    """
    Create a browser track config.
    See a description for options here:

    https://github.com/igvteam/igv.js/wiki/Tracks-2.0
    """
    name: str
    url: str
    indexURL: Optional[str]
    indexed: Optional[bool]
    format: Optional[str]
    order: Optional[int]
    color: Optional[str]
    height: Optional[int]
    autoHeight: Optional[bool]
    minHeight: Optional[int]
    maxHeight: Optional[int]


class Reference(TypedDict):
    """
    Create a browser reference config.
    See a description for options here:

    https://github.com/igvteam/igv.js/wiki/Reference-Genome
    """
    name: str
    fastaURL: str
    indexURL: Optional[str]
    indexed: Optional[bool]
    aliasURL: Optional[str]
    cytobandURL: Optional[str]
    tracks: Optional[List[Track]]


class IGV(DOMWidget):
    """
    A modest port of igv-jupyter to work with 
    both Jupyter Notebooks and Labs
    """
    # Select client side model object with which to sync state
    _model_name = Unicode('IGVModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    # Select appropriate client side view, i.e. which renders IGV
    _view_name = Unicode('IGVMainView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # Establish traitlets representing widget state
    id = Unicode().tag(sync=True)
    initialConfig = Dict().tag(sync=True)
    locus = Unicode().tag(sync=True)
    svg = Unicode().tag(sync=True)

    def __init__(
        self, 
        genome: Union[str, Reference], 
        locus: str = None,
        tracks: List[Track] = None
        ):
        """
        Initialises an IGV browser instance. Basic information is
        required. 
        
        - Genome can be either a str e.g. hg19, or a Reference 
        object, which can be created using IGVWidget.create_genome. 
        
        - Tracks must be Track objects, which can be created 
        using IGVWidget.create_track. 
        
        - Locus must be a gene name or string with format:
        chr:start-end
        """
        super().__init__()
        self.id = self._gen_id()

        if locus:
            self.locus = locus

        self.initialConfig = IGV._filter_none({
            "id": self.id, 
            "locus": self.locus, 
            "tracks": tracks, 
            "genome" if isinstance(genome, str) else "reference": genome
        })

    def _gen_id(
        self
        ) -> str:
        """
        Internal method for creating a random enough ID
        """
        return 'igv_' + str(random.randint(1, 10000000))

    @staticmethod
    def _filter_none(
        obj: Any
        ) -> dict:
        """
        Removes any top level keys from a dict with values
        of None. Returns a new dictionary.
        """
        if isinstance(obj, (list, tuple, set)):
            return type(obj)(IGV._filter_none(x) for x in obj if x is not None)
        elif isinstance(obj, dict):
            return type(obj)((IGV._filter_none(k), IGV._filter_none(v))
            for k, v in obj.items() if k is not None and v is not None)
        else:
            return obj

    def search_locus(
        self, 
        chr: str, 
        start: int, 
        end: int
        ):
        """
        Go to the specified locus if possible.

        It is also possible to perform this action with:
        self.locus = 'chr:start-end'
        """
        if not (end > start):
            print('Error: end param must be greater than start')
            return

        self.locus = '{0}:{1}-{2}'.format(chr, start, end)

    def zoom_in(
        self
        ):
        """
        Zoom in by a factor of 2
        """
        self.send({
            "type": "zoomIn"
        })

    def zoom_out(
        self
        ):
        """
        Zoom out by a factor of 2
        """
        self.send({
            "type": "zoomOut"
        })

    def create(
        self
        ):
        """
        Remove the igv.js Browser instance from the front end.
        The server Browser object should be disposed of after
        calling this method.
        """
        self.send({
            "type": "create"
        })

    def remove(
        self
        ):
        """
        Remove the igv.js Browser instance from the front end. 
        The server Browser object should be disposed of after 
        calling this method.
        """
        self.send({
            "type": "remove"
        })

    @staticmethod
    def create_track(
        name: str,
        url: str,
        index_url: str = None,
        indexed: bool = None,
        fmt: str = None,
        order: int = None,
        color: str = None,
        height: int = None,
        autoHeight: bool = None,
        minHeight: int = None,
        maxHeight: int = None,
        ) -> Track:
        """
        Returns an instance of Track, which can be
        used as an input to IGVBrowser initialisation or
        self.load_track

        See a description of options here:
        https://github.com/igvteam/igv.js/wiki/Tracks-2.0
        """
        return Track(
            name=name, url=url, indexURL=index_url, 
            indexed=indexed, format=fmt, order=order,
            color=color, height=height, autoHeight=autoHeight,
            minHeight=minHeight, maxHeight=maxHeight
        )

    def load_track(
        self, 
        track: Track
        ):
        """
        Request the browser instance to add the track.
        """
        self.send({
            "type": "loadTrack",
            **self._filter_none(track)
        })

    def remove_track(
        self, 
        name: str
        ):
        """
        Request the browser instance to the remove
        any track with this name. May remove
        multiple tracks.
        """
        self.send({
            "type": "removeTrack", 
            "name": name
        })

    @staticmethod
    def create_genome(
        name: str,
        fasta_url: str,
        indexed: bool = None,
        index_url: str = None,
        alias_url: str = None,
        cytoband_url: str = None, 
        tracks: List[Track] = None
        ) -> Reference:
        """
        Returns an instance of Reference, which can be
        used as an input to IGVBrowser initialisation or
        self.load_genome

        See a description of options here:
        https://github.com/igvteam/igv.js/wiki/Reference-Genome
        """
        return Reference(
            name=name, fastaURL=fasta_url, indexed=indexed, 
            indexURL=index_url, aliasURL=alias_url, 
            cytobandURL=cytoband_url, tracks=tracks
        )

    def load_genome(
        self, 
        genome: Reference
        ):
        """
        Request the browser instance to add the genome.
        """
        self.send({
            "type": "loadGenome",
            **self._filter_none(genome)
        })

    def _event_setter(
        self, 
        out: Output, 
        change: Bunch
        ):
        """
        Used by get_svg to react to the self.svg
        traitlet updating.
        """
        with out:
            display(SVG(change.new))
        self.unobserve(None, names=['svg'])

    def get_svg(
        self
        ):
        """
        Fetch the current IGV view as an SVG image and 
        display it in this cell
        """
        output_widget = Output()
        display(output_widget)

        setter = partial(self._event_setter, output_widget)
        self.observe(setter, names=['svg'])

        self.send({
            "elementId": self._gen_id(), 
            "type": "toSVG"
        })