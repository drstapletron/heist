# heist

Fermilab provides the art event-processing framework for HEP experiments.  Read-only access to art files is provided by a library they call 'gallery'.  This library can be used from Python, but the interface exposed by PyROOT is not very user-friendly.

The 'heist' module wraps around this interface to provide easy access to the data in an art file.  It also provides some facility for interactive inspection of this data.

See demo.py in Marc Paterno's gallery demos: <https://github.com/marcpaterno/gallery-demo>

This module has been developed using software for the Muon g-2 collaboration at Fermilab, but *nothing in this module depends on g-2 software*, and it should work equally well for any files produced using the art event-processing framework.


Prerequisites:

  * environment set up so that ROOT can find your data products
  * gallery set up
  * pyROOT and ROOT using the same version of Python



Example:
```
import heist

record_tag = heist.InputTag(
  'ROOT.vector(ROOT.namespace.recordtype)', 
  'modlabel', 'instname', 'procID'
)

artreader = heist.ArtFileReader(filename='something.root')

for event in artreader.event_loop():
  records = event.get_record(record_tag)
  heist.magicdump(records)
```

# Interactive Inspection

Run your script with `python -i` and then, after the event loop, you can do some interesing things like this:
```
>>> for record_name in artreader.list_records(): print record_name
... 
gm2calo::CaloCalibrationConstants_energyCalibratorSim_calibrator_caloSimChain
gm2calo::ClusterArtRecords_hitClusterSim_cluster_caloSimChain
gm2calo::CrystalHitArtRecords_energyCalibratorSim_calibrator_caloSimChain
gm2calo::CrystalHitArtRecords_gainCorrectorSim_corrector_caloSimChain
gm2calo::CrystalHitArtRecords_islandFitterSim_fitter_caloSimChain
gm2calo::IslandArtRecords_islandChopper_chopper_caloSimChain
gm2truth::LookupArtRecords_filler_caloFill_caloSimChain
```

Even when the event loop has finished, you can inspect the contents of the file in other ways.  You can get records using the 'friendly name' (TTree name) and inspect them using a special function included with heist:
```
>>> clusters = event.get_record('gm2calo::ClusterArtRecords_hitClusterSim_cluster_caloSimChain')
>>> print clusters
<ROOT.vector<gm2calo::ClusterArtRecord> object at 0xc5e43c0>
>>> len(clusters)
8
>>> heist.magicdump(clusters[0])
object type: <class 'ROOT.gm2calo.ClusterArtRecord'>
some attributes:
  caloNum: 6
  crystalHits: <ROOT.art::PtrVector<gm2calo::CrystalHitArtRecord> object at 0xc6...
  energy: 1724.7158544
  fillNum: 3
  islandNum: 0
  time: 42466.1282103
  type: 0
  x: 7.5
  y: 0.624433923059
```

