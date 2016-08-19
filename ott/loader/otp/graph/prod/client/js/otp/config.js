// make sure we have otp.config and otp.config.locale defined
if(typeof(otp) == "undefined" || otp == null) otp = {};
if(typeof(otp.config) == "undefined" || otp.config == null) otp.config = {};
if(typeof(otp.locale) == "undefined" || otp.locale == null) otp.locale = {};
if(typeof(otp.locale.English) == "undefined" || otp.locale.English == null) otp.locale.English = {};

otp_consts = {
    /**
     * The OTP web service locations
     */
    hostname       : "http://maps8.trimet.org:55555",
    restService    : "otp/routers/default",
    solrService    : "http://maps.trimet.org/solr/select",
    center         : new L.LatLng(45.494833,-122.670376),
    maxWalk        : 804.672, // 1/2 mile walk
    //maxWalk        : 1207.008, // 3/4 mile walk
    //maxWalk        : 1609.344, // 1 mile walk
    attribution    : 'Map data &copy; 2016 Oregon Metro and <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a> and contributors.'
};

otp.config = {

    debug: false,
    debug_layers: false,
    locale: otp.locale.English,

    //All avalible locales
    //key is translation name. Must be the same as po file or .json file
    //value is name of settings file for localization in locale subfolder
    //File should be loaded in index.html
    locales : {
        'en': otp.locale.English,
        'de': otp.locale.German,
        'pl': otp.locale.Polish,
        'sl': otp.locale.Slovenian,
        'fr': otp.locale.French,
        'it': otp.locale.Italian,
        'ca_ES': otp.locale.Catalan
    },

    languageChooser : function() {
        var active_locales = _.values(otp.config.locales);
        var str = "<ul>";
        var localesLength = active_locales.length;
        var param_name = i18n.options.detectLngQS;
        for (var i = 0; i < localesLength; i++) {
            var current_locale = active_locales[i];
            var url_param = {};
            url_param[param_name] = current_locale.config.locale_short;
            str += '<li><a href="?' + $.param(url_param) + '">' + current_locale.config.name + ' (' + current_locale.config.locale_short + ')</a></li>';
        }
        str += "</ul>";
        return str;
    },

    /**
     * The OTP web service locations
     */
    hostname       : otp_consts.hostname,
    restService    : otp_consts.restService,
    datastoreUrl   : otp_consts.datastoreUrl,

    /**
     * Base layers: the base map tile layers available for use by all modules.
     * Expressed as an array of objects, where each object has the following 
     * fields:
     *   - name: <string> a unique name for this layer, used for both display
     *       and internal reference purposes
     *   - tileUrl: <string> the map tile service address (typically of the
     *       format 'http://{s}.yourdomain.com/.../{z}/{x}/{y}.png')
     *   - attribution: <string> the attribution text for the map tile data
     *   - [subdomains]: <array of strings> a list of tileUrl subdomains, if
     *       applicable
     *       
     */
    baseLayers: [
        {
            name: 'TriMet Map',
            tileUrl: 'http://{s}.trimet.org/tilecache/tilecache.py/1.0.0/currentOSM/{z}/{x}/{y}',
            subdomains : ["tilea","tileb","tilec","tiled"],
            attribution : otp_consts.attribution
        },
        {
            name: 'TriMet Aerials',
            tileUrl: 'http://{s}.trimet.org/tilecache/tilecache.py/1.0.0/hybridOSM/{z}/{x}/{y}',
            subdomains : ["tilea","tileb","tilec","tiled"],
            attribution : otp_consts.attribution
        },
        {
            name: 'OSM Tiles',
            tileUrl: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            subdomains : ['a','b'],
            attribution : 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
        }
    ],


    /**
     * Map start location and zoom settings: by default, the client uses the
     * OTP routerInfo API call to center and zoom the map. The following
     * properties, when set, override that behavioir.
     */
    initLatLng : otp_consts.center,
    initZoom : 11,
    minZoom : 10,
    maxZoom : 22,
    zoomToFitResults    : true,

    /**
     * Site name / description / branding display options
     */
    siteName            : "PROD Single Agency OTP",
    siteDescription     : "PROD Single Agency OTP",
    logoGraphic         : 'images/agency_logo.png',
    agencyStopLinkText  : "Real Time Arrivals",
    fareDisplayOverride : "$2.50 (A), $1.25 (H), $1.25 (Y)",
    bikeshareName       : "BIKETOWN",

    showLogo            : true,
    showTitle           : true,
    showModuleSelector  : true,
    showWheelchairOption: false,
    infoWidgets         : [],     // turns off about and contact top-nav items

    metric              : false,


    /**
     * Modules: a list of the client modules to be loaded at startup. Expressed
     * as an array of objects, where each object has the following fields:
     *   - id: <string> a unique identifier for this module
     *   - className: <string> the name of the main class for this module; class
     *       must extend otp.modules.Module
     *   - [defaultBaseLayer] : <string> the name of the map tile base layer to
     *       used by default for this module
     *   - [isDefault]: <boolean> whether this module is shown by default;
     *       should only be 'true' for one module
     *
     * @see: http://trimet.dev.conveyal.com/js/otp/config.js
     */
    modules : [
        {
            id : 'planner',
            defaultBaseLayer : 'TriMet Map',
            isDefault: true,
            className : 'otp.modules.multimodal.MultimodalPlannerModule'
        },
        {
            id : 'analyst',
            defaultBaseLayer : 'TriMet Map',
            className : 'otp.modules.analyst.AnalystModule'
        }
    ],
    
    
    /**
     * Geocoders: a list of supported geocoding services available for use in
     * address resolution. Expressed as an array of objects, where each object
     * has the following fields:
     *   - name: <string> the name of the service to be displayed to the user
     *   - className: <string> the name of the class that implements this service
     *   - url: <string> the location of the service's API endpoint
     *   - addressParam: <string> the name of the API parameter used to pass in
     *       the user-specifed address string
     */
    geocoders : [
        {
            name : 'SOLR',
            className    : 'otp.core.SOLRGeocoder',
            url          : otp_consts.solrService,
            addressParam : 'q'
        }
    ],


    //This is shown if showLanguageChooser is true
    infoWidgetLangChooser : {
        title: '<img src="/images/language_icon.svg" onerror="this.onerror=\'\';this.src=\'/images/language_icon.png\'" width="30px" height="30px"/>', 
        languages: true
    },


    /**
     * Support for the "AddThis" display for sharing to social media sites, etc.
     */
    showAddThis     : false,
    //addThisPubId    : 'your-addthis-id',
    //addThisTitle    : 'Your title for AddThis sharing messages',


    /**
     * Formats to use for date and time displays, expressed as ISO-8601 strings.
     */
    timeFormat  : "h:mma",
    dateFormat  : "MMM Do YYYY"
};
var options = {
    resGetPath: 'js/otp/locale/__lng__.json',
    fallbackLng: 'en',
    nsseparator: ';;', //Fixes problem when : is in translation text
    keyseparator: '_|_',
    preload: ['en'],
    //TODO: Language choosing works only with this disabled
    /*lng: otp.config.locale_short,*/
    /*postProcess: 'add_nekaj', //Adds | around every string that is translated*/
    /*shortcutFunction: 'sprintf',*/
    /*postProcess: 'sprintf',*/
    debug: true,
    getAsync: false, //TODO: make async
    fallbackOnEmpty: true
};
var _tr = null; //key
var ngettext = null; // singular, plural, value
var pgettext = null; // context, key
var npgettext = null; // context, singular, plural, value

i18n.addPostProcessor('add_nekaj', function(val, key, opts) {
    return "|"+val+"|";
});

i18n.init(options, function(t) {
    //Sets locale and metric based on currently selected/detected language
    if (i18n.lng() in otp.config.locales) {
        otp.config.locale = otp.config.locales[i18n.lng()];
        otp.config.metric = otp.config.locale.config.metric;
        //Conditionally load datepicker-lang.js?
    } 

    //Use infoWidgets from locale
    //Default locale is English which has infoWidgets
    if ("infoWidgets" in otp.config.locale) {
        otp.config.infoWidgets=otp.config.locale.infoWidgets;
    } else {
        otp.config.infoWidgets=otp.locale.English.infoWidgets;
    }

    if (otp.config.showLanguageChooser) {
        otp.config.infoWidgets.push(otp.config.infoWidgetLangChooser);
    }
    //Accepts Key, value or key, value1 ... valuen
    //Key is string to be translated
    //Value is used for sprintf parameter values
    //http://www.diveintojavascript.com/projects/javascript-sprintf
    //Value is optional and can be one parameter as javascript object if key
    //has named parameters
    //Or can be multiple parameters if used as positional sprintf parameters
    _tr = function() {
        var arg_length = arguments.length;
        //Only key
        if (arg_length == 1) {
            key = arguments[0];
            return t(key); 
        //key with sprintf values
        } else if (arg_length > 1) {
            key = arguments[0];
            values = [];
            for(var i = 1; i < arg_length; i++) {
                values.push(arguments[i]);
            }
            return t(key, {postProcess: 'sprintf', sprintf: values}); 
        } else {
            console.error("_tr function doesn't have an argument");
            return "";
        }
    };
    ngettext = function(singular, plural, value) {
        return t(singular, {count: value, postProcess: 'sprintf', sprintf: [value]});
    };
    pgettext = function(context, key) {
        return t(key, {context: context});
    };
    npgettext = function(context, singular, plural, value) {
        return t(singular, {context: context,
                 count: value,
                 postProcess: 'sprintf',
                 sprintf: [value]});
    };

});

otp.config.modes = {
    "TRANSIT,WALK"              : _tr("Transit"),
    "BUS,WALK"                  : _tr("Bus Only"),
    "TRAM,RAIL,GONDOLA,WALK"    : _tr("Rail Only"),
    "BICYCLE"                   : _tr('Bicycle Only'),
    "TRANSIT,BICYCLE"           : _tr("Bicycle &amp; Transit"),
    //"AIRPLANE,WALK"           : _tr("Airplane Only"),
    "CAR_PARK,WALK,TRANSIT"     : _tr('Park and Ride'),
    "CAR,WALK,TRANSIT"          : _tr('Kiss and Ride'),
    "BICYCLE_PARK,WALK,TRANSIT" : _tr('Bike and Ride'),
    // uncomment only if bike rental exists in a map
    // TODO: remove this hack, and provide code that allows the mode array to be configured with different transit modes.
    //'WALK,BICYCLE_RENT'       :_tr('Rented Bicycle'),
    'TRANSIT,WALK,BICYCLE_RENT' : _tr('Transit & Rented Bicycle'),
    "CAR"                       : _tr('Drive Only'),
    "WALK"                      : _tr('Walk Only')
};
