

__doc__ = '''Helpers for gallery+python.

Ideal use case:
  1) import heist
  2) open an art file
  3) tell the art file which records I want
  4) event loop

There are things that will need to be initialized between steps 1 and 2

2017-07-06: modified some more while working on kicker data...
2017-08-27: added 'magicdump' method
2017-08-29: started some heavier modification...
2017-10-01: mostly cleanup (some debugging)
2017-11-29: magicdump autodetects iterables


NOTES: 

  * heist.ROOT.gallery has attributes which list the ValidHandle
    template types
  * heist.ROOT.gallery.__getattribute__ is a 'wrapper_descriptor'
    whereas most objects __getattribute__ is a 'method-wrapper'
  * check types/classes declared to CLING with
      heist.ROOT.gROOT.GetListOfClasses/Types().Print()

TODO:
  * make InputTags with a member function of ArtFileReader (before
      the event loop, so the reader has time to initialize the
      data product getter template types)
  * ArtRecordSpec (deprecate in favor of InputTag by itself (and
      some other way of telling the artfilereader which records
      to access within the event loop)
  * ArtRecordSpec (if not deprecated): handle process ID, and make
      the named arguments to the constructor shorter), and make
      it understand a simple string like ns::type_modlabel__procID
      
'''

#import sys
import ROOT as ROOT

################################################################

autoload_headers = ['gallery/ValidHandle.h']

################################################################

#def magicdump(obj, maxlength=65, exclude_hidden=True, exclude=()):
#  '''Print some of an object's attributes (version 2017-05-05).
#  
#  Handles functions/methods better and truncates long lines.
#  
#  maxlength=65: truncate string representations to maxlength
#  exclude_hidden=True: include _things_ and __stuff__
#  exclude=(): skip attribs with names in this list
#  '''
#  print 'object type: %s\nsome attributes:'%(type(obj),)
#  for attname in dir(obj):
#    
#    # don't print __stuff__ (unless exclude_hidden==False)
#    if exclude_hidden==True and attname[0]=='_': continue
#    
#    # don't print excluded stuff
#    if attname in exclude: continue
#    
#    att = obj.__getattribute__(attname) # fetch attribute
#    str_rep = str(att) # make a string representation for attribute
#    
#    # if it's a function/method, print its docstring...
#    #if str(type(att)) in ("<type 'instancemethod'>","<type 'builtin_function_or_method'>"):
#    if 'method' in str(type(att)).lower() or 'function' in str(type(att)).lower():
#      attname = attname+'()'
#      if att.__doc__ != None: str_rep = att.__doc__
#      else: str_rep = 'method (with no docstring)' # (...unless it doesn't have a docstring)
#    
#    # truncate at maxlength characters:
#    if len(str_rep)>maxlength: str_rep = str_rep[:maxlength] + '...'
#    
#    # truncate after newline: 
#    if '\n' in str_rep: str_rep = str_rep[:str_rep.index('\n')] + '...'
#    
#    print '  %s: %s'%(attname,str_rep)

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
    print 'skipping %s as it is already loaded...'%(filename,)
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
    print 'skipping %s as it is already declared...'%(Ttype,)
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
  #global testvar
  #print testvar
  global autoload_headers
  #global loaded_headers
  #global loaded_handle_Ttypes
  # first ensure that the autoload_headers have been loaded
  for header in autoload_headers+headers:
    #if header not in loaded_headers:
    #  retval = read_header(header)
    #  #print 'read_header() returned',retval
    #  if retval==0: # TODO: check success condition
    #    loaded_headers += [ header ]
    _do_load_header(header)
  
  if len(handle_Ttypes)>0:
    for Ttype in handle_Ttypes:
      #if Ttype not in loaded_handle_Ttypes:
      #  retval = provide_get_valid_handle(Ttype)
      #  print 'provide_get_valid_handle() returned',retval
      #  if retval==retval: # TODO: impose a success condition
      #    loaded_handle_Ttypes += [ Ttype ]
      _do_declare_Ttype(Ttype)

init_env()




class ArtFileReader(object):
  '''Tracks art files, does ROOT initialization, and provides an event loop.
  
  
  '''
  def __init__(self, filename=None):
    '''Set filename(s) (and nothing else?)'''
    self.filename_list = []
    self.evt = None               # gallery Event
    self.i_evt = None             # index (from 0) of this event in full loop
    self.i_loop = None            # loop counter (=i_evt if no filtering)
    self.art_record_specs = []
    self.product_getters = {}
    
    self.gallery_evt_initialized = False
    self.product_getters_setup = False
    self.in_loop = False
    
    if filename!=None: self.add_filenames(filename)
    
  def full_event_id(self):
    '''Returns (Run,SubRun,EventNumber).'''
    evt_id = self.evt.eventAuxiliary().id() # art event ID object
    return (evt_id.run(),evt_id.subRun(),evt_id.event())
  
  def run(self):
    '''Returns run number from art event ID.'''
    return self.evt.eventAuxiliary().id().run()
  
  def subrun(self):
    '''Returns SubRun number from art event ID.'''
    return self.evt.eventAuxiliary().id().subRun()
  
  def event_id(self):
    '''Returns Event ID number from art event ID.'''
    return self.evt.eventAuxiliary().id().event()
  
  def event_label(self, short=False):
    '''Returns RunNN SubRunNN EventNN.'''
    format_str = 'Run%d SubRun%d Event%d' if not short else 'r%ds%de%d'
    return format_str%self.full_event_id()
  
  def add_filenames(self, filename):
    '''Set self.filename_list.'''
    if type(filename)==str:
      self.filename_list += [ filename ]
    elif hasattr(filename, '__iter__'):
      for f in filename: self.filename_list += [ f ]
    else: 
      raise ValueError('filename should be a string (or collection of strings)')
  
  def declare_validhandle_type(self, type_str):
    '''Declare the templated type gallery::ValidHandle<type_str> in gROOT.
    
    '''
    pass
  
  def add_record_spec(self, record_spec):
    '''Add ArtRecordSpec to data members.
    
    Must be called *BEFORE* setup_product_getters().
    '''
    if record_spec not in self.art_record_specs:
      _do_declare_Ttype(record_spec.cpp_type_string())
      self.art_record_specs += [ record_spec ]
  
  
  def setup_validhandle_templates(self, record_specs=None):
    '''
    
    must be done BEFORE call to evt.getValidHandle()
    '''
    if record_specs!=None:
      self.art_record_specs = []
      for key in record_specs.keys():
        rs = record_specs[key]
        self.art_record_specs += [ rs ]
    else: assert len(self.art_record_specs)>0 # did you forget to make record specs?
    for rspec in self.art_record_specs:
      self._setup_validhandle_template(rspec)
  def _setup_validhandle_template(self, record_spec):
    '''
    must be done BEFORE call to evt.getValidHandle()
    '''
    # make a string like 'std::vector<gm2truth::IBMSTruthArtRecord>'
    cpp_type_string = record_spec.cpp_type_string()
    print 'provide_get_valid_handle(\'%s\')'%(cpp_type_string,)
    #retval = provide_get_valid_handle(cpp_type_string)
    provide_get_valid_handle(cpp_type_string)
    #self.art_record_specs += [ record_spec ]
    #return retval
  
  
  def initialize_gallery_event(self):
    '''Return first gallery event from files.'''
    filename_vector = ROOT.vector(ROOT.string)()
    for name in self.filename_list:
      filename_vector.push_back(name)
    self.evt = ROOT.gallery.Event(filename_vector)
    if self.evt!=0 and self.evt!=None:
      self.gallery_evt_initialized = True
    return self.evt
  
  #def get_first_event(self):
  #  '''DEPRECATED (renamed to initialize_gallery_event)'''
  #  return initialize_gallery_event(self)
  
  
  def setup_product_getters(self):
    '''
    must be done AFTER call to evt.getValidHandle()
    (also after ArtFile.art_record_specs has been populated)
    '''
    #if self.evt==None: 
    if not self.gallery_evt_initialized:
      print 'setup_product_getters: automatically initializing gallery event'
      self.initialize_gallery_event()
    for rs in self.art_record_specs:
      self.product_getters[rs] = self.evt.getValidHandle(
                                        eval(rs.validhandle_type_string()))
    self.product_getters_setup = True
  
  def get_record(self, record_spec):
    getter = self.product_getters[record_spec]
    retval = None
    try:
      retval = getter(record_spec.input_tag).product()
    except:
      import sys
      print 'Got exception with\n  type: %s\n  value: %s\n  traceback: %s\n'%(
        sys.exc_info()
      )
    #retval = retval.product()
    return retval
  
  
  def event_loop(self, evt_list=(), nmax=None):
    '''Like generate_event_loop() but filters by evt_list.
    
    ONLY yield when event index is in evt_list (yields ALL
      when evt_list is empty (default))
    
    NOTE: evt_list is ZERO-INDEXED! (e.g. 100 events will have 
      indices 0 through 99)
    
    Might work...
    '''
    if not self.product_getters_setup:
      print 'event_loop: automatically setting up product getters...'
      self.setup_product_getters()
    no_filter = len(evt_list)==0
    self.i_evt = self.i_loop = 0
    self.in_loop = True
    while (not self.evt.atEnd()):
      if no_filter or (self.i_loop in evt_list): 
        yield self.evt
        self.i_evt += 1
      self.i_loop += 1
      if nmax!=None and self.i_evt >= nmax:
        print 'Reached maximum %d events!'%(nmax,)
        break
      self.evt.next()
    self.in_loop = False
  
  get_first_event = initialize_gallery_event
  heist_event_loop = event_loop
  generate_event_loop = event_loop


ArtFile = ArtFileReader # TODO: remove to deprecate 'ArtFile'


def cpp_type_string(record_type, record_namespace, vector=True):
  '''Compose a C++ type string which specifies an ArtRecord type.
  
  Example:
    std::vector<gm2truth::IBMSTruthArtRecord>
  '''
  retval = record_type
  if record_namespace != '':
    retval = record_namespace + '::' + retval
  if vector == True:
    retval = 'std::vector<' + retval + '>'
  return retval

def validhandle_type_string(record_type, record_namespace, vector=True):
  '''Compose a Python type string which specifies ValidHandle type.
  
  Example:
    ROOT.vector(ROOT.gm2truth.IBMSTruthArtRecord)
  '''
  retval = record_type
  if record_namespace != '':
    retval = record_namespace + '.' + retval
  retval = 'ROOT.' + retval
  if vector == True: retval = 'ROOT.vector(' + retval + ')'
  return retval


class ArtRecordSpec(object):
  '''TODO: eliminate this class (and just use InputTag).'''
  def __init__(self, 
      record_type, record_namespace, 
      module_label, instance_name='', process_ID='', 
      vector=True
    ):
    self.record_namespace = record_namespace
    self.record_type = record_type
    self.module_label = module_label
    self.instance_name = instance_name
    self.process_ID = process_ID
    self.vector = vector
    self.input_tag = ROOT.art.InputTag(self.module_label,self.instance_name,self.process_ID)
  
  def __str__(self):
    #return self.cpp_type_string() + ' with InputTag=%s_%s'%(self.module_label,self.instance_name)
    return 'InputTag=%s_%s_%s_?'%(
      self.cpp_type_string(),self.module_label,self.instance_name)
  
  def cpp_type_string(self):
    '''Moved to module scope.'''
    return cpp_type_string(
      self.record_type, 
      self.record_namespace, 
      self.vector)
  
  def validhandle_type_string(self):
    '''Moved to module scope.'''
    return validhandle_type_string(
      self.record_type, 
      self.record_namespace, 
      self.vector)


# I was trying to make a nicer ArtRecordSpec, but
#   * I don't want to have to specify 'vector=True|False' and 'namespace=blah'
#   * I don't want to write logic to parse a C++ type
# So maybe I should try clang.cindex.  Or something in CLING?
#class InputTag(object):
#  '''Like art InputTag, but remembers type as well...'''
#  def __init__(self, dtype, modlabel, instname='', procID='', vector=None, namespace=None):
#    
#    # just make an input tag
#    self.input_tag = ROOT.art.InputTag(modlabel,instname,procID)
#    
#    # save this in case processing says it's not valid
#    self.dtype_arg = dtype
#    
#    # remove whitespace and std:: prefixes for a few things
#    dtype = dtype.strip().replace(' ','')
#    dtype = dtype.replace('std::vector','vector')
#    self.dtype = dtype
#    
#    # figure out if it's a vector (unless we were told explicitly)
#    if vector!=None: self.vector = vector
#    else: self.vector = self.dtype.startswith('vector<')
#    
#    # figure out if it has a namespace (unless we were told explicitly)
#    if namespace!=None: self.namespace = namespace
#    else:
#      if self.vector:
#        try:
#          assert self.dtype.find('vector<') == 0
#          end = self.dtype.rfind('>')
#          vector_type = self.dtype[7:end]
#        except: raise ValueError(self.dtype_arg+' is not a valid type!')
#      if 
#    
#  def __str__(self):
    






