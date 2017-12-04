# heist

Fermi National Accelerator Laboratory (FNAL) provides the art event-processing framework for HEP experiments.  Read-only access to art files is provided by a library they call 'gallery'.  This library can be used from Python, but the interface exposed by PyROOT is not very user-friendly.

The 'heist' module wraps around this interface to provide easy access to the data in an art file.  It also provides some facility for interactive inspection of this data.

See demo.py in Marc Paterno's gallery demos: <https://github.com/marcpaterno/gallery-demo>
