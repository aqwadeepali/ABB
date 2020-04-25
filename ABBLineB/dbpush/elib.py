from datetime import datetime, timedelta
from datetime import date as datetime_date
import math
import random
import re

EPOCH_DATE = datetime.strptime( "1970-01-01", "%Y-%m-%d" )
EPOCH_TIME = datetime.strptime( "1970-01-01 00:00:01", "%Y-%m-%d %H:%M:%S" )
weekday_index = dict( MONDAY = 0, TUESDAY = 1, WEDNESDAY = 2, THURSDAY = 3, FRIDAY = 4, SATURDAY = 5, SUNDAY = 6 )

class Ddict( dict ):
    """ Define a two-dimensional dictionary """
    def __init__( self, default = None ):
        self.default = default

    def __getitem__( self, key ):
        if not self.has_key( key ):
            self[key] = self.default()
        return dict.__getitem__( self, key )

def get_epoch_date():
    return EPOCH_DATE

def time_stamp( grain, sep = "" ):
    '''
        Convention to be documented
    '''
    t = datetime.now()
    ( y, m, d, h, mi, s ) = ( str( t.year ), str( t.month ), str( t.day ), str( t.hour ), str( t.minute ), str( t.second ) )
    if grain == 'year':
        stamp = y
    elif grain == 'month':
        stamp = y + sep + m
    elif grain == 'day':
        stamp = y + sep + m + sep + d
    elif grain == 'hour':
        stamp = y + sep + m + sep + d + sep + h
    elif grain == 'minute':
        stamp = y + sep + m + sep + d + sep + h + sep + mi
    elif grain == 'second':
        stamp = y + sep + m + sep + d + sep + h + sep + mi + sep + s
    else:
        stamp = ""
    return stamp


def smartFmt( s ):
    result = s
    r = tonum( s, "float", "Error" )
    if r != "Error":
        if ( ( '.' in s ) or ( '%' in s ) ):
            result = tonum( s, "float" )
        else:
            result = tonum( s, "int" )
    return( result )

def tonum( s, num_type = "float", *args ):
    """
    Convert string s to a number.
    Handles text with leading "$"s, and trailing "%"s.
    Handles comma-separators in text
    $s and commas are removed
    "%"s are converted to float by division by 100
    Optional arguments (*args):
        args[0] -> value_if_fail -> (Default "0" or "0.0")
    """

    # strip $ signs, comma-separators and trailing %s if any
    s = str( s )
    div = 1.0
    s = s.replace( ",", "" ).rstrip().lstrip()
    s = s.lstrip( '$' )
    if s.endswith( '%' ):
        div = 100.0
        s = s.rstrip( '%' ).rstrip()

    # read arguments
    if len( args ) > 0:
        value_if_fail = args[0]
    else:
        if num_type == "int":
            value_if_fail = 0
        else:
            value_if_fail = 0.0

    # convert string to number
    if ( s == '' ):
        r = value_if_fail
    else:
        try:
            if ( num_type == "int" ):
                r = int( float( s ) / div )
            elif ( num_type == "long" ):
                r = long( float( s ) / div )
            else:
                r = float( s ) / div
        except ValueError:
            r = value_if_fail
    return( r )

def is_date( d, fmt = "%Y-%m-%d" ):
    """ Check if argument is a date """
    try:
        datetime.strptime( d, fmt )
        r = True
    except ( TypeError, ValueError ), e:  # nmc
        r = False
    return r

def is_datetime( d, fmt = "%Y-%m-%d %H:%M:%S" ):
    """ Check if argument is a datetime """
    try:
        datetime.strptime( d, fmt )
        r = True
    except ( TypeError, ValueError ), e:  # nmc
        r = False
    return r


def valid_date( d, fmt = "%Y-%m-%d", default = None ):
    try:
        datetime.strptime( d, fmt )
        r = d
    except ( TypeError, ValueError ), e:  # nmc
    # except (TypeError), e: #nmc
        r = default
    return r

def valid_datetime( d, fmt = "%Y-%m-%d %H:%M:%S", default = None ):
    try:
        datetime.strptime( d, fmt )
        r = d
    except ( TypeError, ValueError ), e:  # nmc
    # except (TypeError), e: #nmc
        r = default
    return r

def str2datetime( dt, fmt = "%Y-%m-%d %H:%M:%S" ):
    t = datetime.strptime( dt, fmt )
    return( t )


def str2date( d, fmt = "%Y-%m-%d" ):
    t = datetime.strptime( d, fmt )
    return t

def str2time( d, fmt = "%Y-%m-%d %H:%M:%S" ):
    """ Return a day index """
    t = datetime.strptime( d, fmt ) - EPOCH_TIME
    secs = t.days * 86400 + t.seconds
    return secs

def str2day( d, fmt = "%Y-%m-%d" ):
    """ Return a day index """
    t = datetime.strptime( d, fmt ) - EPOCH_DATE
    return t.days

def day2str( day, fmt = "%Y-%m-%d" ):
    dt = EPOCH_DATE + timedelta( int( day ) )
    str = dt.strftime( fmt )
    return str

def str2week( d, fmt = "%Y-%m-%d", wk_start = 'SUNDAY' ):
    wkday = weekday_index[wk_start]
    epoch = EPOCH_DATE
    shift = wkday - epoch.weekday()
    w = ( str2day( d, fmt ) - shift ) / 7
    return w

def week2str( w, fmt = "%Y-%m-%d", wk_start = 'SUNDAY', days_from_wk_start = '0' ):
    wkday = weekday_index[wk_start]
    epoch = EPOCH_DATE
    shift = wkday - epoch.weekday()
    day = epoch + timedelta( int( w ) * 7 + shift + int( days_from_wk_start ) )
    return day.strftime( fmt )

def datetime2date( s ):
    _fmt = '%Y-%m-%d %H:%M:%S'
    t = datetime.strptime( s, _fmt )
    return t.date()

def datetime2week( s ):
    if ( s == '' ):
        return -1
    else:
        _fmt = '%Y-%m-%d %H:%M:%S'
        # result = valid_datetime(s)
        result = str2week( s, fmt = _fmt )
        return( result )

def datetime2month( s ):
    if ( s == '' ):
        return -1
    else:
        _fmt = '%Y-%m-%d %H:%M:%S'
        # result = valid_datetime(s)
        result = str2month( s, fmt = _fmt )
        return( result )

def datetime2str( s, fmt = "%Y-%m-%d %H:%M:%S" ):
    if ( s == '' ):
        return ''
    else:
        days = int( s ) / 86400
        seconds = int( s ) % 86400
        dt = EPOCH_TIME + timedelta( days, seconds )
        return dt.strftime( fmt )

def date2str( dt, fmt = "%Y-%m-%d" ):
    return dt.strftime( fmt )

def today2str( fmt = "%Y-%m-%d" ):
    return datetime.today().strftime( fmt )

def str2month( d, fmt = "%Y-%m-%d" ):
    t = datetime.strptime( d, fmt )
    return( t.year * 12 + t.month * 1 )

def month2str( m, fmt = "%Y-%m-%d" ):
    day = 1
    month = m % 12
    year = ( m - month ) / 12
    if month == 0:
        month = 12
        year -= 1

    date = datetime( year, month, day )
    return( date.strftime( fmt ) )

def days_between( earliest_dt, latest_dt ):
    date_format = '%Y-%m-%d'
    dt_from = datetime.strptime( earliest_dt, date_format )
    dt_to = datetime.strptime( latest_dt, date_format )
    delta = dt_to - dt_from

    return delta.days

def dictCreate( _dict, key1, key2, value ):
    _dict.setdefault( key1, {} )[key2] = value

def dictIncrement( _dict, key1, key2, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            _dict[key1][key2] += value
        else:
            _dict[key1][key2] = value
    else:
        _dict.setdefault( key1, {} )[key2] = value

def dictIncrement1D( _dict, key, value ):
    if key in _dict:
        _dict[key] += value
    else:
        _dict[key] = value


def dictIncrement2D( _dict, key1, key2, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            _dict[key1][key2] += value
        else:
            _dict[key1][key2] = value
    else:
        _dict.setdefault( key1, {} )[key2] = value

def dictIncrement3D( _dict, key1, key2, key3, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            if key3 in _dict[key1][key2]:
                _dict[key1][key2][key3] += value
            else:
                _dict[key1][key2][key3] = value
        else:
            _dict.setdefault( key1, {} )[key2] = {key3:value}
    else:
        _dict.setdefault( key1, {} )[key2] = {key3:value}

# Requested by dJoko - NMC
def dictIncrement4D( _dict, key1, key2, key3, key4, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            if key3 in _dict[key1][key2]:
                if key4 in _dict[key1][key2][key3]:
                    _dict[key1][key2][key3][key4] += value
                else:
                    _dict[key1][key2][key3][key4] = value
            else:
                _dict[key1][key2][key3] = {key4:value}
        else:
            _dict.setdefault( key1, {} )[key2] = {key3:{key4:value}}
    else:
        _dict.setdefault( key1, {} )[key2] = {key3:{key4:value}}

# DM- Network Velocity
def dictIncrement5D( _dict, key1, key2, key3, key4, key5, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            if key3 in _dict[key1][key2]:
                if key4 in _dict[key1][key2][key3]:
                    if key5 in _dict[key1][key2][key3][key4]:
                        _dict[key1][key2][key3][key4][key5] += value
                    else:
                        _dict[key1][key2][key3][key4][key5] = value
                else:
                    _dict[key1][key2][key3][key4] = {key5:value}
            else:
                _dict[key1][key2][key3] = {key4:{key5:value}}
        else:
            _dict.setdefault( key1, {} )[key2] = {key3:{key4:{key5:value}}}
    else:
        _dict.setdefault( key1, {} )[key2] = {key3:{key4:{key5:value}}}

# DM- MONT BLANC MARS
def dictIncrement6D( _dict, key1, key2, key3, key4, key5, key6, value ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            if key3 in _dict[key1][key2]:
                if key4 in _dict[key1][key2][key3]:
                    if key5 in _dict[key1][key2][key3][key4]:
                        if key6 in _dict[key1][key2][key3][key4][key5]:
                            _dict[key1][key2][key3][key4][key5][key6] += value
                        else:

                            _dict[key1][key2][key3][key4][key5][key6] = value
                    else:
                        _dict[key1][key2][key3][key4][key5] = {key6:value}
                else:
                    _dict[key1][key2][key3][key4] = {key5:{key6:value}}
            else:
                _dict[key1][key2][key3] = {key4:{key5:{key6:value}}}
        else:
            _dict.setdefault( key1, {} )[key2] = {key3:{key4:{key5:{key6:value}}}}
    else:
        _dict.setdefault( key1, {} )[key2] = {key3:{key4:{key5:{key6:value}}}}

def addToDict2( _dict, k1, k2, value ):
    _dict.setdefault( k1, {} )[k2] = value
    return ( _dict )

def addToDict3( _dict, k1, k2, k3, value ):
    try:
        _dict[k1][k2][k3] = value
    except:
        _dict.setdefault( k1, {} )[k2] = {k3:value}
    return _dict

def addToDict4( _dict, k1, k2, k3, k4, value ):
    try:
        _dict[k1][k2][k3][k4] = value
    except:
        addToDict3( _dict, k1, k2, k3, {k4:value} )
    return _dict

def addToDict5( _dict, k1, k2, k3, k4, k5, value ):
    try:
        _dict[k1][k2][k3][k4][k5] = value
    except:
        addToDict4( _dict, k1, k2, k3, k4, {k5:value} )
    return _dict

def addToDict6( _dict, k1, k2, k3, k4, k5, k6, value ):
    try:
        _dict[k1][k2][k3][k4][k5][k6] = value
    except:
        addToDict5( _dict, k1, k2, k3, k4, k5, {k6:value} )
    return _dict

def dictIncrement1DSet( _dict, key, value ):
    if key in _dict:
        _dict[key].add( value )
    else:
        _dict[key] = set( [value] )

def trim( s ):
    return( s.strip() )

def days2weeks( d, daysInWeek ):
    return float( d ) / daysInWeek

def watch_progress( x, n ):
    if x % n == 0:
        print x

def safe_ratio( num = 1.0, den = 1.0, value_if_error = "Inf", NaN = "NaN" ):
    if num == 0 and den == 0:
        result = NaN
    elif den == 0:
        result = value_if_error
    else:
        result = num / den
    return( result )

def in_between( x, low, high ):
    result = ( ( x >= low ) and ( x <= high ) )
    return( result )

def repeat_string( str, count = 2 ):
    return str * count

def dict2kv( _dict, key_type = 'str' ):
    if key_type == 'str':
        r = sorted( _dict.iteritems(), key = lambda ( k, v ): k )
        _keys = [e[0] for e in r]
        _values = [e[1] for e in r]
    elif ( key_type == 'int' or key_type == 'float' ):
        r = sorted( _dict.iteritems(), key = lambda ( k, v ): tonum( k ) )
        _keys = [tonum( e[0], key_type ) for e in r]
        _values = [e[1] for e in r]
    elif key_type == 'week':
        r = sorted( _dict.iteritems(), key = lambda ( k, v ): int( k ) )
        _keys = [str2date( week2str( e[0] ) ) for e in r]
        _values = [e[1] for e in r]
    elif key_type == 'date':
        # assumes yyyy-mm-dd format, which is sortable as a string
        r = sorted( _dict.iteritems(), key = lambda ( k, v ): k )
        _keys = [str2date( week2str( e[0] ) ) for e in r]
        _values = [e[1] for e in r]
    else:
        _keys = _dict.keys()
        _values = _dict.values()
    return( _keys, _values )

def weekly2daily( week_idx, qty, days = '12345' ):
    '''
        0 is Sunday
        1,2,3,4,5,6 is Mon-Sat
        12345 => split qty in 5, allocate equally to 1,2,3,4,5
    '''
    result = {}
    start_day = str2day( week2str( week_idx ) )
    n_days = len( days )
    for _d in days:
        d_idx = start_day + tonum( _d, 'int' )
        daily_qty = 1.0 * qty / n_days
        result[d_idx] = daily_qty
    return result

def fix_width( _str, _len, filler = ' ' ):
    fill = filler * ( _len - len( _str ) )
    _str = fill + _str
    return( _str )

def list2string( delim, _list ):
    if delim in ['\t', 'tab', 'Tab', 'TAB']:
        s = "\t".join( [str( i ) for i in _list] )
    else:
        s = delim.join( [str( i ) for i in _list] )
    return( s )

def dict2string( delim, _dict ):
    s = ""
    for k in sorted( _dict ):
        if delim in ['\t', 'tab', 'Tab', 'TAB']:
            s += str( _dict[k] ) + "\t"
        else:
            s += str( _dict[k] ) + delim
    return( s )

def aggregate( _dict, _key, _value ):
    if _dict.has_key( _key ):
        _dict[_key] += _value
    else:
        _dict[_key] = _value

def rnd( value, places ):
    v = tonum( value, 'float', '-' )
    if v != '-':
        if ( v - math.floor( v ) ) == 0.0:
            places = 0
        try:
            result = round( v, places )
            if places == 0:
                result = int( result )
        except:
            result = value
    else:
        result = value
    return( result )



def tabDelimit( _array, tab = True, length = 0 ):
    if tab:
        result = "\t".join( [fix_width( str( i ), length, " " ) for i in _array] )
    else:
        result = " ".join( [fix_width( str( i ), length, " " ) for i in _array] )
    return( result )

def tagText( _text ):
    '''
        Returns items tagged with *xyz and _xyz_:
            *<foo> will return 'foo' in result[0]
            _<bar>_ will return 'bar' in result[1]

    '''
    _items = re.findall( r"\*([a-zA-Z0-9\-]*)\b", _text )
    _context = re.findall( r"_(.*?)_", _text )
    result = {'items':_items, 'context':_context}
    return( result )

def debug_toggle( var, value ):
    if var in value:
        result = True
    else:
        result = False
    return( result )

def list_get( _list, _key, _default ):
    if _key < len( _list ):
        r = _list[_key]
    else:
        r = _default
    return( r )

def TRACE( dict, stage, v = 1 ):
    '''
        Trace a variable .. can be used to count number of times code
        enters a loop
    '''
    dictIncrement2D( dict, stage, 'COUNT', 1 )
    dictIncrement2D( dict, stage, 'SUM', v )

def TRACEResult( dict ):
    '''
        Print results of the trace function
    '''
    for stage in dict:
        print '**Trace**', stage, 'count: ', dict[stage]['COUNT'], 'sum: ', dict[stage]['SUM']


def classifier( v, d, _default ):
    # d = {(r1,r2):c1, ...}
    result = _default
    for r in d:
        ( low, high ) = r
        if ( v > low ) and ( v <= high ):
            result = d[r]
    return( result )

def rounded_classifier( v, d, _default ):
    if v == 'NA':
        return 'NA'
    else:
        rounded_result = '0%'
        is_negative = True if v < 0 else False
        abs_v = abs( v )
        result_str = classifier( abs_v, d, 'NA' )

        if result_str == '0%':
            return '0%'

        result = tonum( result_str.strip( '%' ) )

        the_dict = {20:[( 0, 0.1 ), ( '0%', '20%' )], 40:[( 0.21, 0.3 ), ( '20%', '40%' )], 60:[( 0.41, 0.5 ), ( '40%', '60%' )], \
                    80:[( 0.61, 0.7 ), ( '60%', '80%' )], 100:[( 0.81, 0.9 ), ( '80%', '100%' )]}

        if result > 0:
            virtual_d = the_dict[result]
            ( low, high ) = virtual_d[0]
            ( low_percnt, high_percnt ) = virtual_d[1]

            if abs_v >= low and abs_v <= high:
                rounded_result = low_percnt
            else:
                rounded_result = high_percnt

        if rounded_result != '0%':
            rounded_result = '-' + rounded_result if is_negative else '+' + rounded_result

        return rounded_result


def generate_demand( qty, mode = 'float' ):
    '''
    If mode = 'float' returns the qty as demand
    If mode = 'round' returns an integer demand by randomly rounding up or down as necessary
    '''
    if mode == 'float':
        result = qty
    elif mode == 'round':
        _base = math.floor( qty )
        _frac = qty - _base
        _add = 0
        if random.random() < _frac:
            _add = 1
        result = _base + _add
    else:
        result = 0
    return( result )

def nonull( stream ):
  for line in stream:
    yield line.replace( '\x00', '' )

def merge_demand( D_list ):
    # D_list is a list of demand dictionaries {t1:d1, t2:d2, ... , tn:dn}

    _merged_D = {}

    # sum demand in each time bucket
    for _D in D_list:
        for _t, _q in _D.iteritems():
            # _merged_D.setdefault(_t, 0) += _q
            _merged_D[_t] = _merged_D.get( _t, 0 ) + _q

    return( _merged_D )

def if_yes_no( condition, if_yes, if_no ):
    if condition:
        r = if_yes
    else:
        r = if_no
    return( r )

def today():
    today = datetime_date.today()
    s = str( today.year ) + "-" + fix_width( str( today.month ), 2, '0' ) + "-" + fix_width( str( today.day ), 2, '0' )
    return ( s )

def exists2D( _dict, key1, key2 ):
    exists = False
    if key1 in _dict:
        if key2 in _dict[key1]:
            exists = True
    return( exists )

def delFromDict2( _dict, key1, key2 ):
    if key1 in _dict:
        if key2 in _dict[key1]:
            del( _dict[key1][key2] )

def compact_dict(d, keys):
    for k in keys:
        del d[k]

def float2int( _qty, randomize_float = False, roundFactor = 0.5 ):
    _result = int( _qty )
    _dec = _qty % 1
    if randomize_float:
        if random.random() < _dec:
            _result += 1
    else:
        if _dec >= roundFactor:
            _result += 1
    return( _result )

def headers_as_list( theHdrs ):
    return [_col[0] for _col in theHdrs]

def apply_front_load(ts):
    """
    Front load a time series with integral demand
    :param ts: fractional demand to be front-loaded
    :return: list of front-loaded values
    """
    r = []
    exs = 0
    for v in ts:
        chk = v - exs
        if chk >= 0:
            v1 = int(math.ceil(v))
            r.append(v1)
            exs += (v1 - v)
        else:
            v1 = 0
            r.append(v1)
            exs -= v
    return r

def apply_back_load(ts):
    r = []
    exs = 0
    for v in ts:
        chk = v - exs
        if chk >= 0:
            pass
        else:
            v1 = int(math.floor(v))
            r.append(v1)
            exs += (v - v1)
    return r


if __name__ == '__main__':
    # print '2015-04-12 =', str2week('2015-04-12')
    # print '13WK = ',str2week('2015-04-12')-13,'=',week2str(str2week('2015-04-12')-13)
    # print '26WK = ',str2week('2015-04-12')-26,'=',week2str(str2week('2015-04-12')-26)
    # print '1YR = ',str2week('2015-04-12')-52,'=',week2str(str2week('2015-04-12')-52)
    # print '2YR = ',str2week('2015-04-12')-104,'=',week2str(str2week('2015-04-12')-104)
    ts = [1.2,1.3,1.7,1.3,1.3,1.5]
    print apply_front_load(ts)
