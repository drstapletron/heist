

__doc__ = '''Helpers for gallery+PyROOT.

Example:
  xtalhit_tag = heist.InputTag(
                'ROOT.vector(ROOT.gm2calo.CrystalHitArtRecord)', 
                'islandFitterDAQ', 'fitter', '')
  artreader = heist.ArtFileReader(filename='something.root')
  
  for evt in artreader.event_loop(nmax=30):
    print evt.get_label()
    xtalhit_recs = evt.get_record(xtalhit_tag)
    heist.magicdump(xtalhit_recs[0])

(NOTE: the heist InputTag object REQUIRES A TYPE STRING)

--------------------------------------------------------------

TODO:
  * implement regexes into ArtFileReader.list_records()
  * make things like 'vector<short>' print data 
    * override __str__ like type(trace).__str__ = my_special_function
  * think about ProductNotFound vs. empty collection (currently returns
    None in both cases)
  * import SOME things in ROOT namespace to heist namespace
    * examples: vector, string, gm2calo and other C++ namespaces of
      art records
    * PS: see this: heist.magicdump(heist.ROOT.module.cppyy.libPyROOT)
    * maybe try something like this
        for thing in dir(ROOT.module.cppyy.libPyROOT):
          if thing[0]!=thing[0].lower(): continue # skip ROOT, TObject, etc
          if thing in dir(__builtins__): continue # don't overwrite e.g. 'list'
          if thing in ('gInterpreter','gROOT','gSystem'): continue # skip these
          from ROOT.module.cppyy.libPyROOT import thing
      (though that last line won't work...)
  * improve magicdump iteration (see https://opensource.com/article/18/3/loop-\
    better-deeper-look-iteration-python)
    * ROOT.vector doesn't have __iter__, but it's iterable
    * use iter()?
    * `for i_item,item in enumerate(obj[:n_items_to_print])` breaks on 
      TObjectArrays, but only because of the slicing

--------------------------------------------------------------

NOTES: 
  * heist.ROOT.gallery has attributes which list the ValidHandle
    template types
  * heist.ROOT.gallery.__getattribute__ is a 'wrapper_descriptor'
    whereas most objects __getattribute__ is a 'method-wrapper'
  * check types/classes declared to CLING with
      heist.ROOT.gROOT.GetListOfClasses/Types().Print()

--------------------------------------------------------------


'''

import sys
import ROOT as ROOT

################################################################

autoload_headers = ['gallery/ValidHandle.h']

################################################################


def magicdump(obj, 
    maxlength=65, 
    exclude_hidden=True, 
    exclude=(), 
    detect_iterable=True, 
    show_N_iter=2
  ):
  '''Print some of an object's attributes (version 2017-05-05).
  
  Handles functions/methods better and truncates long lines.
  
  maxlength: truncate string representations to maxlength (default=65)
  exclude_hidden: exclude _things_ and __stuff__ (default=True)
  exclude: skip attribs with names in this list (default=())
  detect_iterable: descend into iterable objects (default=True)
  show_N_iter: how many elements of iterable to show (default=2)
  '''
  if detect_iterable and '__len__' in dir(obj):
    print 'object is an iterable type (%s)'%(type(obj),)
    print 'length =',len(obj)
    n_items_to_print = min(show_N_iter,len(obj))
    print 'first %d items: '%(n_items_to_print,)
    for i_item,item in enumerate(obj[:n_items_to_print]):
      print '-'*maxlength
      print 'item %d:'%(i_item,)
      magicdump(obj[i_item],
        maxlength=maxlength, exclude_hidden=exclude_hidden, exclude=exclude, 
        detect_iterable=False)
    print '-'*maxlength
    print '...plus %d more elements not shown...'%(len(obj)-n_items_to_print,)
    return
  print 'object type: %s\nsome attributes:'%(type(obj),)
  for attname in dir(obj):
    
    # don't print __stuff__ (unless exclude_hidden==False)
    if exclude_hidden==True and attname[0]=='_': continue
    
    # don't print excluded stuff
    if attname in exclude: continue
    
    att = obj.__getattribute__(attname) # fetch attribute
    str_rep = str(att) # make a string representation for attribute
    
    # if it's a function/method, print its docstring...
    #if str(type(att)) in ("<type 'instancemethod'>","<type 'builtin_function_or_method'>"):
    if 'method' in str(type(att)).lower() or 'function' in str(type(att)).lower():
      attname = attname+'()'
      if att.__doc__ != None: str_rep = att.__doc__
      else: str_rep = 'method (with no docstring)' # (...unless it doesn't have a docstring)
    
    # truncate at maxlength characters:
    if len(str_rep)>maxlength: str_rep = str_rep[:maxlength] + '...'
    
    # truncate after newline: 
    if '\n' in str_rep: str_rep = str_rep[:str_rep.index('\n')] + '...'
    
    print '  %s: %s'%(attname,str_rep)


import os
def grab_art_files(directory, prefix, suffix='.root'):
  '''Return list of files matching given conditions.
  
  TODO: this could be more powerful...
  '''
  filename_list = []
  for filename in os.listdir(directory):
    if filename[:len(prefix)]==prefix and filename[-len(suffix):]==suffix:
      filename_list += [ os.path.join(directory,filename) ]
  return tuple(filename_list)


# useful functions from Marc Paterno
def read_header(h):
        """Make the ROOT C++ jit compiler read the specified header."""
        return ROOT.gROOT.ProcessLine('#include "%s"' % h)
def provide_get_valid_handle(klass):
        """Make the ROOT C++ jit compiler instantiate the
           Event::getValidHandle member template for template
           parameter klass."""
        return ROOT.gROOT.ProcessLine('template gallery::ValidHandle<%(name)s> gallery::Event::getValidHandle<%(name)s>(art::InputTag const&) const;' % {'name' : klass})


# I"m not sure exactly what I really want to do with the next few functions...
loaded_headers = []
def _do_load_header(filename):
  global loaded_headers
  if filename in loaded_headers:
    #print 'skipping %s as it is already loaded...'%(filename,)
    return 0
  retval = read_header(filename)
  if retval==0: loaded_headers += [ filename ]
  else: 
    print 'FAILED to load header %s...?'%(filename,)
    print 'read_header returned',retval
  return retval

loaded_handle_Ttypes = []
def _do_declare_Ttype(Ttype):
  global loaded_handle_Ttypes
  if Ttype in loaded_handle_Ttypes:
    #print 'skipping %s as it is already declared...'%(Ttype,)
    return 0
  retval = provide_get_valid_handle(Ttype)
  if retval==0: loaded_handle_Ttypes += [ Ttype ]
  else: 
    print 'FAILED to declare ValidHandle Template type...?'%(Ttype,)
    print 'provide_get_valid_handle returned',retval
  return retval

def init_env(
    handle_Ttypes=[], 
    headers=[]
):
  global autoload_headers
  
  # first ensure that the autoload_headers have been loaded
  for header in autoload_headers+headers:
    _do_load_header(header)
  
  # ...then declare ValidHandle<T> types
  if len(handle_Ttypes)>0:
    for Ttype in handle_Ttypes:
      _do_declare_Ttype(Ttype)

init_env()




class ArtFileReader(object):
  '''Tracks art files, does ROOT initialization, and provides an event loop.
  
  
  '''
  def __init__(self, filename=None):
    '''Set filename(s) (and nothing else?)'''
    self.filename_list = []
    self.evt = None               # heist Event
    self.i_evt = None             # index (from 0) of this event in full loop
    self.i_loop = None            # loop counter (=i_evt if no filtering)
    
    self.evt_initialized = False
    self.in_loop = False
    
    if filename!=None: self.add_filenames(filename)
      
  def add_filenames(self, filename):
    '''Set self.filename_list.'''
    if type(filename)==str:
      self.filename_list += [ filename ]
    elif hasattr(filename, '__iter__'):
      for f in filename: self.filename_list += [ f ]
    else: 
      raise ValueError('filename should be a string (or collection of strings)')
  
  def initialize_event(self):
    '''Initialize heist.Event (which initializes and stores a gallery::Event).'''
    filename_vector = ROOT.vector(ROOT.string)()
    for name in self.filename_list:
      filename_vector.push_back(name)
    self.evt = Event(filename_vector)
    if self.evt.gallery_event!=0 and self.evt.gallery_event!=None:
      self.evt_initialized = True
    return self.evt
  
  def event_loop(self, evt_list=(), nmax=None):
    '''Like generate_event_loop() but filters by evt_list.
    
    ONLY yield when event index is in evt_list (yields ALL
      when evt_list is empty (default))
    
    NOTE: evt_list is ZERO-INDEXED! (e.g. 100 events will have 
      indices 0 through 99)
    
    Might work...
    '''
    #if not self.product_getters_setup:
    #  print 'event_loop: automatically setting up product getters...'
    #  self.setup_product_getters()
    if not self.evt_initialized:
      print 'event_loop: automatically initializing heist.Event...'
      self.initialize_event()
    no_filter = len(evt_list)==0
    self.i_evt = self.i_loop = 0
    self.in_loop = True
    while (not self.evt.at_end()):
      if no_filter or (self.i_loop in evt_list): 
        yield self.evt
        self.i_evt += 1
      self.i_loop += 1
      if nmax!=None and self.i_evt >= nmax:
        print 'Reached maximum %d events!'%(nmax,)
        break
      self.evt.next()
    self.in_loop = False
  
  def list_records(self, pattern=None, regex=None):
    '''Return a list of type_modlabel_instname_procID for TTrees in file.
    
    Specify pattern to return only things with pattern as substring (case-
      insensitive).
    
    Specify regex to match by regular expression (UNIMPLEMENTED).
    '''
    retval = []
    if pattern==None and regex==None:
      for b in self.evt.gallery_event.getTTree().GetListOfBranches():
        retval += [ b.GetName().rstrip('.') ]
    elif pattern!=None and regex==None:
      for b in self.evt.gallery_event.getTTree().GetListOfBranches():
        if pattern in b.GetName().lower(): retval += [ b.GetName().rstrip('.') ]
    elif pattern==None and regex!=None:
      raise NotImplementedError('DO ALL THE REGEXES!!!1!')
    else: raise ValueError('Do not specify "pattern" AND "regex"!')
    return retval
  
  def ls(self, pattern=None, regex=None):
    '''Prints records from list_records, but more like ls.'''
    for record in self.list_records(pattern=pattern,regex=regex):
      print '  '+record


class Event(object):
  '''Like gallery::Event, but manages instantiating/caching product getters.
  
  Try to NOT create the product getters until Event.get() is called.  That 
    way I can open, loop over a few events, then ask what other records 
    exist in the file, create a new heist.InputTag, and say Event.get()
    *after* the event has been created.
  
  It also makes sense to move a few things here from ArtFileReader.
  '''
  def __init__(self, filenames):
    self.filenames = filenames
    self.gallery_event = ROOT.gallery.Event(filenames)
    self.product_getters = {}
  
  def at_end(self): return self.gallery_event.atEnd()
  def next(self): return self.gallery_event.next()
  
  def get_record(self, input_tag):
    '''Call getValidHandle<C++Type>(InputTag) and return data products.
    
    Checks for an existing product getter by looking for the string
      input_tag.dtype_string in product_getters.keys().  If not found, then it
      will instantiate it with gallery.Event.getValidHandle(input_tag.dtype)
      and add it to product_getters with input_tag.dtype_string as the key.
    '''
    
    # check for InputTag, else assume we got a quicktag
    if type(input_tag)==str:
      input_tag = InputTag(quicktag=input_tag)
    
    # check for product getter, and make one if not found
    if input_tag.dtype_string not in self.product_getters.keys():
      try: 
        self.product_getters[input_tag.dtype_string] \
          = self.gallery_event.getValidHandle(input_tag.dtype)
      except: 
        exc_info = sys.exc_info()
        print 'Got exception with\n  type: %s\n  value: %s\n  traceback: %s\n'%(
          exc_info
        )
        raise RuntimeError(
          'Could not instantiate product getter for type "%s"!'%(
            input_tag.dtype_string
          )
        )
    
    # try to get the data product
    retval = None
    try: 
      retval = self.product_getters[input_tag.dtype_string](input_tag.input_tag).product()
    except:
      exc_info = sys.exc_info()
      if 'ProductNotFound' not in str(exc_info[1]):
        print 'Got exception with\n  type: %s\n  value: %s\n  traceback: %s\n'%(
          exc_info
        )
    
    # handle emtpy vectors as well as ProductNotFound by simply doing
    #   if records==None: continue
    if retval!=None and hasattr(retval,'__len__') and len(retval)==0: 
      retval = None
    
    return retval
  
  def get_ID(self):
    '''Returns (Run,SubRun,EventNumber).'''
    evt_id = self.gallery_event.eventAuxiliary().id() # art event ID object
    return (evt_id.run(),evt_id.subRun(),evt_id.event())
  
  def get_run_ID(self):
    '''Returns run number from art event ID.'''
    return self.gallery_event.eventAuxiliary().id().run()
  
  def get_subrun_ID(self):
    '''Returns SubRun number from art event ID.'''
    return self.gallery_event.eventAuxiliary().id().subRun()
  
  def get_event_ID(self):
    '''Returns Event ID number from art event ID.'''
    return self.gallery_event.eventAuxiliary().id().event()
  
  def get_label(self, short=False):
    '''Returns RunNN SubRunNN EventNN.'''
    format_str = 'Run%d SubRun%d Event%d' if not short else 'r%ds%de%d'
    return format_str%self.get_ID()



class InputTag(object):
  '''Like art InputTag, but remembers type as well...
  
  dtype is something like 'ROOT.vector(ROOT.gm2reconeast.BSTCorrectionArtRecord)'
  or 'ROOT.art.Wrapper(something)'
  
  You MUST specify parameters using exactly ONE of the following:
    1) data product type (dtype) AND module label (label)
    2) string representing TTree name (quicktag)
  '''
  def __init__(self, 
      dtype=None, label=None, instance='', process='', 
      quicktag=None
    ):
    
    if dtype==None and label==None: # using quicktag_string
      if quicktag==None or instance!='' or process!='': 
        raise ValueError('Invalid arguments for InputTag constructor!')
      dtype,label,instance,process = self.convert_quicktag(quicktag)
    elif quicktag==None: # using dtype and label
      if dtype==None or label==None:
        raise ValueError('Invalid arguments for InputTag constructor!')
    else:
      raise ValueError('Invalid arguments for InputTag construction!')
    
    # save dtype string, then try to turn it into a type
    self.dtype_string = dtype
    try: 
      self.dtype = eval(self.dtype_string)
    except: 
      raise ValueError('Could not resolve '+self.dtype_string+' to a valid type!')
    
    # Does this step have to occur before creating gallery::Event?
    _do_declare_Ttype(self.dtype.__cppname__)
    
    # make an art input tag
    self.input_tag = ROOT.art.InputTag(label,instance,process)
    
  def convert_quicktag(self, spec_str):
    '''Convert a string to an InputTag.
    
    For example, this
      ANameSpace::BArtRecords_CModLabel_DInstName_EProcID
    returns an InputTag instantiated with
      type='vector(ANameSpace.BArtRecord)'
      module label=CModLabel
      instance name='DInstName'
      process ID='EProcID'
    
    NOTES: 
      * assumes any type ending in 's' is really a vector
      * CANNOT handle art.Assns (yet)
      * and maybe not Ptrs or any other templated types?
    '''
    typestr,modlabel,instname,procID = spec_str.split('_')
    typestr = typestr.replace('::','.') # translating C++ to Python... :-(
    typestr = 'ROOT.' + typestr
    if typestr[-1]=='s': # convert hoomon-friendly name to 'collection' (vector)
      typestr = 'ROOT.vector(' + typestr.rstrip('s') + ')'
    return (typestr,modlabel,instname,procID)
  
  def label(self):
    '''Passthrough to InputTag.label()'''
    return self.input_tag.label()
  
  def instance(self):
    '''Passthrough to InputTag.instance()'''
    return self.input_tag.instance()
  
  def process(self):
    '''Passthrough to InputTag.process()'''
    return self.input_tag.process()
  
  def __str__(self):
    return self.dtype.__cppname__+'_'+self.label()+'_'+self.instance()+'_'+self.process()







