import emcli
import re
import operator

class updateProps():
    """
       The updateProps() class is used in conjuction with
       EM CLI and  allows the user to apply a defined set
       of target properties to a target list filtered at
       multiple levels with regular expressions. These
       target list filter levels include the target name,
       the target type and the parent agent name. The
       properties can be applied to the targets using the
       class directly or using an instance of the class.

       The filtered list can be specified:
         - as class parameters and have the defined
           properties applied directly to them
         - as class parameters when creating an instance
           of the class
         - with the filt() function as part of an instance

       The defined set of target properties can specified:
         - as the class dictionary parameter 'propdict'
           and have the defined properties applied
           directly to the target list
         - as the class dictionary parameter 'propdict'
           when creating an instance of the class
         - with the props() function as part of an instance
    """
    def __init__(self, agentfilter='.*', typefilter='.*',
                 namefilter='.*', propdict={}):
        self.targs = []
        self.reloadtargs = True
        self.props(propdict)
        self.__loadtargobjects()
        self.filt(agentfilter=agentfilter, typefilter=typefilter,
                  namefilter=namefilter)
    def __loadtargobjects(self):
        """
           __loadtargobjects() queries the OMS for the full
           target list. The target list is then cached in the
           instance variable 'fulltargs' and each target's
           corresponding properties are assigned to the
           'targprops' instance variable. These variables
           are refreshed only when target properties have been
           applied.

           This function is called by other functions and
           should never be called directly. 
        """
        if self.reloadtargs == True:
            self.reloadtargs = False
            self.fulltargs = \
              emcli.list(resource='Targets').out()['data']
            self.targprops = \
              emcli.list(resource='TargetProperties'
                        ).out()['data']
    def props(self, propdict):
        """
           props() can be called from an instance directly or
           will be called by __init__() when defining the
           instance or using the class directly. This function
           defines a dictionary object of the property names
           and values that will be applied to the defined
           target list.
        """
        assert isinstance(propdict, dict), \
               'propdict parameter must be ' + \
               'a dictionary of ' + \
	       '{"property_name":"property_value"}'
        self.propdict = propdict
    def filt(self, agentfilter='.*', typefilter='.*',
             namefilter='.*',
             sort=('TARGET_TYPE','TARGET_NAME'), show=False):
        """
           filt() can be called from an instance directly or
           will be called by __init__() when defining the
           instance or using the class directly. This function
           limits the target list by only including those targets
           whose properties match the defined filters.

           This function accepts the following parameters:
             agentfilter - regular expression string applied
               to the parent agent of the target
             typefilter - regular expression string applied
               to the target type value
             namefilter - regular expression string applied
               to the target name value
        """
        self.targs = []
        __agentcompfilt = re.compile(agentfilter)
        __typecompfilt = re.compile(typefilter)
        __namecompfilt = re.compile(namefilter)
        self.__loadtargobjects()
        for __inttarg in self.fulltargs:
            if __typecompfilt.search(__inttarg['TARGET_TYPE']) \
               and __namecompfilt.search(
                   __inttarg['TARGET_NAME']) \
               and (__inttarg['EMD_URL'] == None or \
               __agentcompfilt.search(__inttarg['EMD_URL'])):
                self.targs.append(__inttarg)
        __myoperator = operator
        for __myop in sort:
            __myoperator = operator.itemgetter(__myop)
        self.targssort = sorted(self.targs, key=__myoperator)
        if show == True:
            self.show()
    def show(self):
        """
           show() can be called from an instance directly or
           as a parameter from some of the other functions.
           Prints a neatly formatted display of the target name
           and type along with all of the target's currently
           defined property names and values.
        """
        print('%-5s%-40s%s' % (
              ' ', 'TARGET_TYPE'.ljust(40, '.'),
              'TARGET_NAME'))
        print('%-15s%-30s%s\n%s\n' % (
              ' ', 'PROPERTY_NAME'.ljust(30, '.'),
              'PROPERTY_VALUE', '=' * 80))
        for __inttarg in self.targssort:
            print('%-5s%-40s%s' % (
                  ' ', __inttarg['TARGET_TYPE'].ljust(40, '.'),
                  __inttarg['TARGET_NAME']))
            self.__showprops(__inttarg['TARGET_GUID'])
            print('')
    def __showprops(self, guid):
        """
           __showprops() prints the target properties for the
           target with the unique guid matching the 'guid'
           variable passed to the function. This function is
           called by the show() function for each target to
           print out the corresponding properties of the target.

           This function is called by other functions and
           should never be called directly. 
        """
        self.__loadtargobjects()
        for __inttargprops in self.targprops:
            __intpropname = \
              __inttargprops['PROPERTY_NAME'].split('_')
            if __inttargprops['TARGET_GUID'] == guid and \
               __intpropname[0:2] == ['orcl', 'gtp']:
                print('%-15s%-30s%s' %
                      (' ', ' '.join(__intpropname[2:]).ljust(
                       30, '.'),
                       __inttargprops['PROPERTY_VALUE']))
    def setprops(self, show=False):
        """
           setprops() is called directly from the class or
           from an instance and calls the EM CLI function that
           applies the defined set of properties to each target
           in the filtered list of targets. The 'show' boolean
           parameter can be set to True to call the show()
           function after the properties have been applied.
        """
        assert len(self.propdict) > 0, \
               'The propdict parameter must contain ' + \
               'at least one property. Use the ' + \
               'props() function to modify.'
        self.reloadtargs = True
        __delim = '@#&@#&&'
        __subseparator = 'property_records=' + __delim
        for __inttarg in self.targs:
            for __propkey, __propvalue \
                in self.propdict.items():
                __property_records = __inttarg['TARGET_NAME'] + \
                  __delim + __inttarg['TARGET_TYPE'] + \
                  __delim + __propkey + __delim + __propvalue
                print('Target: ' + __inttarg['TARGET_NAME'] +
                      ' (' + __inttarg['TARGET_TYPE'] +
                      ')\n\tProperty: '
                      + __propkey + '\n\tValue: ' +
		      __propvalue + '\n')
                emcli.set_target_property_value(
                  subseparator=__subseparator,
                  property_records=__property_records)
        if show == True:
            self.show()
