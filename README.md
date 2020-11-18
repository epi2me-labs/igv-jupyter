# igv-jupyterlab

igv-jupyterlab is an extension for Jupyter Lab and traditional Jupyter Notebooks which wraps igv.js.

This extension is a simple re-write of the official igv-jupyter. 

It is not yet 100% feature complete, so please leave any requests in the issues section.


## Installation

You can install using `pip`:

```bash
pip install igv_jupyterlab
```

Or if you use jupyterlab:

```bash
pip install igv_jupyterlab
jupyter labextension install @jupyter-widgets/jupyterlab-manager @epi2melabs/igv-jupyterlab
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] igv_jupyterlab
```

## Usage

This extension provides a python wrapper which allows you render igv.js 
in a cell and call its API from the notebook.

### Initialization

To insert an IGV instance into a cell: 

```python
from igv_jupyterlab import IGV

# At minimum, IGV requires a single argument, genome.

# For supported genomes, a simple name may be supplied.
IGV(genome="hg19")

# For all other genomes, we must construct a configuration object.
# A helper method supplied to make this easier.
genome = IGV.create_genome(
    name="Human (GRCh38/hg38)",
    fasta_url="https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa",
    index_url="https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/hg38/hg38.fa.fai",
    cytoband_url="https://s3.amazonaws.com/igv.broadinstitute.org/annotations/hg38/cytoBandIdeo.txt",
)

igv = IGV(genome=genome)

display(igv)
```

Supported genomes are [listed here](https://s3.amazonaws.com/igv.org.genomes/genomes.json).
Reference configuration is described in the [igv.js documentation](https://github.com/igvteam/igv.js/wiki/Reference-Genome).

```python
# It is also easy to change the genome to something else
some_other_genome = igv.create_genome(...)

igv.load_genome(some_other_genome)
```

### Tracks

To load a track pass a track configuration object to load_track().  Track configuration
objects are described in the [igv.js documentation](https://github.com/igvteam/igv.js/wiki/Tracks-2.0).

#### Remote URL

```python
track = IGV.create_track(
    name="Segmented CN",
    url="https://data.broadinstitute.org/igvdata/test/igv-web/segmented_data_080520.seg.gz",
    format="seg",
    indexed=False
)

igv.load_track(track)
```

#### Local File

Tracks can be loaded from local files using the Jupyter web server by prepending "files" to the path.
The path is relative to the notebook file.  

```python
track = IGV.create_track(
    name="Local VCF",
    url="files/data/example.vcf",
    format="vcf",
    type="variant",
    indexed=False
)

igv.load_track(track)
```

#### Remove a track

```python

# It is easy to remove a track by name
igv.remove_track("HG00103")
```

### Navigation

Zoom in by a factor of 2

```python
igv.zoom_in()
```

Zoom out by a factor of 2

```python
igv.zoom_out()
```

Jump to a specific locus

```python
igv.locus = 'chr1:3000-4000'

# A helper method is available to avoid having to perform string formatting
igv.search_locus('chr1', 3000, 4000)
```

Jump to a specific gene. This uses the IGV search web service, which currently supports a limited number of genomes:  hg38, hg19, and mm10.
To configure a custom search service see the [igv.js documentation](https://github.com/igvteam/igv.js/wiki/Browser-Configuration-2.0#search-object-details)

```python
igv.locus = 'myc'
```

### SVG output

Displaying the current IGV view as an SVG is simple - and only requires one call now!  

```python
igv.get_svg()
```

## Development Installation

```bash
# First install the python package. This will also build the JS packages.
pip install -e ".[test, examples]"
```

When developing your extensions, you need to manually enable your extensions with the
notebook / lab frontend. For lab, this is done by the command:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
jupyter labextension install .
```

For classic notebook, you can run:

```
jupyter nbextension install --sys-prefix --symlink --overwrite --py igv_jupyterlab
jupyter nbextension enable --sys-prefix --py igv_jupyterlab
```

Note that the `--symlink` flag doesn't work on Windows, so you will here have to run
the `install` command every time that you rebuild your extension. For certain installations
you might also need another flag instead of `--sys-prefix`, but we won't cover the meaning
of those flags here.

### How to see your changes
#### Typescript:
To continuously monitor the project for changes and automatically trigger a rebuild, start Jupyter in watch mode:
```bash
jupyter lab --watch
```
And in a separate session, begin watching the source directory for changes:
```bash
npm run watch
```

After a change wait for the build to finish and then refresh your browser and the changes should take effect.

#### Python:
If you make a change to the python code then you will need to restart the notebook kernel to have it take effect.
