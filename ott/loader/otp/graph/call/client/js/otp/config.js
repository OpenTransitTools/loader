// make sure we have otp.config and otp.config.locale defined
if(typeof(otp) == "undefined" || otp == null) otp = {};
if(typeof(otp.config) == "undefined" || otp.config == null) otp.config = {};
if(typeof(otp.locale) == "undefined" || otp.locale == null) otp.locale = {};
if(typeof(otp.locale.English) == "undefined" || otp.locale.English == null) otp.locale.English = {};

otp_consts = {
    /**
     * The OTP web service locations
     */
    trinetReDirect : "https://trinet.trimet.org/call_verify_login",
    datastoreUrl   : "https://call.trimet.org:9443",
    hostname       : "https://call.trimet.org",
    restService    : "otp/routers/default",
    solrService    : "https://ws.trimet.org/solrwrap/v1/select",
    center         : new L.LatLng(45.494833,-122.670376),
    maxWalk        : 804.672, // 1/2 mile walk
    //maxWalk        : 1207.008, // 3/4 mile walk
    //maxWalk        : 1609.344, // 1 mile walk
    attribution    : '&copy; Oregon Metro | &copy; <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>'
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
            tileUrl: '//{s}.trimet.org/tilecache/tilecache.py/1.0.0/currentOSM/{z}/{x}/{y}',
            subdomains : ["tilea","tileb","tilec","tiled"],
            attribution : otp_consts.attribution
        },
        {
            name: 'TriMet Aerials',
            tileUrl: '//{s}.trimet.org/tilecache/tilecache.py/1.0.0/hybridOSM/{z}/{x}/{y}',
            subdomains : ["tilea","tileb","tilec","tiled"],
            attribution : otp_consts.attribution
        },
        {
            name: 'OSM Tiles',
            tileUrl: '//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
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
    maxZoom : 19,
    zoomToFitResults    : true,

    /**
     * Site name / description / branding display options
     */
    siteName            : "TriMet Call Taker Tools",
    siteDescription     : "Call Taker Stuff",
    logoGraphic         : 'images/agency_logo.png',
    agencyStopLinkText  : "Real Time Arrivals",
    fareDisplayOverride : "$2.80 (A), $1.40 (H), $1.40 (Y)",
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
            id : 'call',
            className : 'otp.modules.calltaker.CallTakerModule',
            defaultBaseLayer : 'TriMet Map',
            isDefault: true,
            options:
            {
                trinet_verify_login_url : otp_consts.trinetReDirect,
                module_redirect_url     : otp_consts.hostname,

                defaultQueryParams : 
                {
                    maxWalkDistance : otp_consts.maxWalk
                    //,
                    //maxHours : 3
                },

                mailables : [
                    { name : 'Rte 1 Schedule (1-Vermont)', largePrint: true },
                    { name : 'Rte 2 Schedule (FX2-Division)', largePrint: true },
                    { name : 'Rte 4 Schedule (4-Fessenden)', largePrint: true },
                    { name : 'Rte 6 Schedule (6-Martin Luther King Jr Blvd)', largePrint: true },
                    { name : 'Rte 8 Schedule (8-Jackson Park/NE 15th)', largePrint: true },
                    { name : 'Rte 9 Schedule (9-Powell Blvd)', largePrint: true },
                    { name : 'Rte 10 Schedule (10-Harold St)', largePrint: true },
                    { name : 'Rte 11/16 Schedule (11-Rivergate/Marine Dr, 16-Front Ave/St Helens Rd)', largePrint: true },
                    { name : 'Rte 12 Schedule (12-Barbur/Sandy Blvd)', largePrint: true },
                    { name : 'Rte 14 Schedule (14-Hawthorne/Foster)', largePrint: true },
                    { name : 'Rte 15 Schedule (15-Belmont/NW 23rd)', largePrint: true },
                    { name : 'Rte 17 Schedule (17-Holgate/Broadway)', largePrint: true },
                    { name : 'Rte 18/63 Schedule (18-Hillside, 63-Washington Park/SW 6th)', largePrint: true },
                    { name : 'Rte 19 Schedule (19-Woodstock/Glisan)', largePrint: true },
                    { name : 'Rte 20 Schedule (20-Burnside/Stark)', largePrint: true },
                    { name : 'Rte 21 Schedule (21-Sandy Blvd/223rd)', largePrint: true },
                    { name : 'Rte 22/23 Schedule (22-Parkrose, 23-San Rafael)', largePrint: true },
                    { name : 'Rte 24 Schedule (24-Fremont/NW 18th)', largePrint: true },
                    { name : 'Rte 25 Schedule (25-Glisan/Troutdale Rd)', largePrint: true },
                    { name : 'Rte 26 Schedule (26-Thurman/NW 18th)', largerPrint: true },
                    { name : 'Rte 29/30 Schedule (29-Lake/Webster Rd, 30-Estacada)', largePrint: true },
                    { name : 'Rte 31/79 Schedule (31-Webster Rd/79-Clackamas/Oregon City)', largePrint: true },
                    { name : 'Rte 32/34 Schedule (32-Oatfield, 34-Linwood/River Rd)', largePrint: true },
                    { name : 'Rte 33 (33-McLoughlin/King Rd)', largePrint: true },
                    { name : 'Rte 35 Schedule (35-Macadam/Greeley)', largePrint: true },
                    { name : 'Rte 37 Schedule (37-Lake Grove)', largePrint: true },
                    { name : 'Rte 38 Schedule (38-Boones Ferry Rd)', largePrint: true },
                    { name : 'Rte 39 Schedule (39-Arnold Creek/Hillsdale)', largePrint: true },
                    { name : 'Rte 40 Schedule (40-Tacoma/Swan Island)', largePrint: true },
                    { name : 'Rte 43/45 Schedule (43-Taylors Ferry/Marquam Hill, 45-Garden Home)', largePrint: true },
                    { name : 'Rte 44 Schedule (44-Capitol Hwy/Mocks Crest)', largePrint: true },
                    { name : 'Rte 46 Schedule (46-North Hillsboro)', largePrint: true },
                    { name : 'Rte 47/48 Schedule (47-Main/Evergreen, 48-Cornell)', largePrint: true },
                    { name : 'Rte 51 Schedule (51-Vista/Sunset Blvd)', largePrint: true },
                    { name : 'Rte 52 Schedule (52-Farmington/185th)', largePrint: true },
                    { name : 'Rte 53 Schedule (53-Arctic/Allen)', largePrint: true },
                    { name : 'Rte 54 Schedule (54-Beaverton-Hillsdale Hwy)', largePrint: true },
                    { name : 'Rte 55 Schedule (55-Hamilton)', largePrint: true },
                    { name : 'Rte 56 Schedule (56-Scholls Ferry/Marquam Hill)', largePrint: true },
                    { name : 'Rte 57/59 Schedule (57-TV Hwy/Forest Grove, 59-Walker/Park Way)', largePrint: true },
                    { name : 'Rte 58 Schedule (58-Canyon Rd)', largePrint: true },
                    { name : 'Rte 62/67 Schedule (62-Murray Blvd, 67-Bethany/158th)', largePrint: true },
                    { name : 'Rte 70 Schedule (70-12th/NE 33rd Ave)', largePrint: true },
                    { name : 'Rte 71/73 Schedule (71-60th Ave, 73-122nd Ave)', largePrint: true },
                    { name : 'Rte 72 Schedule (72-Killingsworth/82nd Ave)', largePrint: true },
                    { name : 'Rte 74 Schedule (74-162nd Ave)', largePrint: true },
                    { name : 'Rte 75 Schedule (75-Cesar Chavez/Lombard)', largePrint: true },
                    { name : 'Rte 76/78 Schedule (76-Hall/Greenburg, 78-Denney/Kerr Pkwy', largePrint: true },
                    { name : 'Rte 77 Schedule (77-Broadway/Halsey)', largePrint: true },
                    { name : 'Rte 80/81 Schedule (80-Kane/Troutdale Rd, 81-Kane/257th)', largePrint: true },
                    { name : 'Rte 82 Schedule (82-South Gresham)', largePrint: true },
                    { name : 'Rte 84 Schedule (84-Powell Valley/Orient Dr)', largePrint: true },
                    { name : 'Rte 87 Schedule (87-Airport Way/181st)', largePrint: true },
                    { name : 'Rte 88 Schedule (88-Hart/198th)', largePrint: true },
                    { name : 'Rte 94 Schedule (94-Pacific Hwy/Sherwood)', largePrint: true },
                    { name : 'Rte 96/97 Schedule (96-Tualatin/I-5, 97-Tualatin-Sherwood Rd)', largePrint: true },
                    { name : 'Rte 152 Schedule (152-Milwaukie)', largePrint: true },
                    { name : 'Rte 153 Schedule (153-Stafford/Salamo)', largePrint: true },
                    { name : 'Rte 155/156 Schedule (155-Sunnyside, 156-Mather Rd)', largePrint: true },
                    { name : 'MAX Schedule: Blue, Green, Orange, Red, Yellow & Late Night/Early Morning Bus', largePrint: true },
                    { name : 'MAX Schedule: Red Line', largePrint: true },
                    { name : 'WES Schedule', largePrint: true },
                    { name : 'Destinations Brochure', largePrint: false},
                    { name : 'Accessible Services Brochure', largePrint: false},
                    { name : 'Bikes and TriMet ', largePrint: false},
                    { name : 'Bikes and TriMet (Spanish)', largePrint: false},
                    { name : 'Fares & How to Ride (multilingual)', largePrint: false},
                    { name : 'Multilingual Hop pamphlet', largePrint: false},
                    { name : 'Trip Tools', largePrint: false},
                    { name : 'System Map', largePrint: true},
                    { name : 'Honored Citizen Application', largePrint: false},
                    { name : 'LIFT Eligibility Packet', largePrint: false},
                    { name : 'Transit Access Flip-book for the Blind', largePrint: false},
                    { name : 'Lanyard', largePrint: false},
                    { name : 'Safety light', largePrint: false},
                    { name : 'Earl P. Nutt Safety Coloring Book', largePrint: false},
                    { name : 'Earl P. Nutt Safety Puzzle Book', largePrint: false},
                    { name : 'MAX Safety Posters', largePrint: false},
                    { name : 'Bus Safety Posters', largePrint: false},
                    { name : 'WES Safety Posters', largePrint: false},
                    { name : 'WES Safety Poster (Spanish)', largePrint: false},
                    { name : 'WES Safety Stickers', largePrint: false},
                    { name : 'WES Safety DVD', largePrint: false},
                    { name : 'MAX Train Bank', largePrint: false},
                    { name : 'Service Alert - Pamphlet A', largePrint: false},
                    { name : 'Service Alert - Pamphlet B', largePrint: false},
                    { name : 'Service Alert - Pamphlet C', largePrint: false},
                    { name : 'Survey (English)', largePrint: false},
                    { name : 'Survey (Spanish)', largePrint: false},
                    { name : 'Survey (Chinese)', largePrint: false},
                    { name : 'Survey (Russian)', largePrint: false},
                    { name : 'Survey (Vietnamese)', largePrint: false}
                ],

                // letter margins in points (1" on page = 72 points)
                mailables_horizontal_margin: 108,
                mailables_vertical_margin: 72,

                mailables_introduction : "Thank you for calling us to request TriMet information.  We have enclosed for you the following item(s):",
                mailables_conclusion : "For personalized trip planning, please call our Rider Support Team from 7:30 AM until 5:30 PM, seven days a week, at 238-RIDE (238-7433), TTY 238-5511.  We can also provide fare information, additional schedules, or brochures you may need.\n\nIt's a pleasure to serve your transit needs, and we thank you for riding TriMet.",

                mailables_footer : "Tri-County Metropolitan Transportation District of Oregon • 503-238-RIDE • TTY 503-238-5811 • trimet.org",

                // header graphic location
                mailables_header_graphic : "images/agency_logo.png",

                // dimensions to render signature graphic, in points (1" on page = 72 points)
                mailables_signature_graphic_height : 36,
                mailables_signature_graphic_width : 108
            }
        }
        ,
        {
            id : 'ft',
            className : 'otp.modules.fieldtrip.FieldTripModule',
            defaultBaseLayer : 'TriMet Map',
            isDefault: false,
            options:
            {
                trinet_verify_login_url : otp_consts.trinetReDirect,
                module_redirect_url     : otp_consts.hostname,
                defaultQueryParams :
                {
                    maxWalkDistance : otp_consts.maxWalk,
                    minTransferTime : 300
                }
            }
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

    showAddThis     : false,
    //addThisPubId    : 'your-addthis-id',
    //addThisTitle    : 'Your title for AddThis sharing messages',

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
    fallbackOnEmpty: true,
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
    "TRANSIT,WALK"                : _tr("Transit"),
    "BUS,WALK"                    : _tr("Bus Only"),
    "TRAM,RAIL,GONDOLA,WALK"      : _tr("Rail Only"),
    "BICYCLE"                     : _tr('Bicycle Only'),
    "TRANSIT,BICYCLE"             : _tr("Bicycle &amp; Transit"),
    //"AIRPLANE,WALK"             : _tr("Airplane Only"),
    //"CAR_PARK,WALK,TRANSIT"     : _tr('Park and Ride'),
    //"CAR,WALK,TRANSIT"          : _tr('Kiss and Ride'),
    //"BICYCLE_PARK,WALK,TRANSIT" : _tr('Bike and Ride')
    // uncomment only if bike rental exists in a map
    // TODO: remove this hack, and provide code that allows the mode array to be configured with different transit modes.
    //'WALK,BICYCLE_RENT'         :_tr('Rented Bicycle'),
    //'TRANSIT,WALK,BICYCLE_RENT' : _tr('Transit & Rented Bicycle'),
    //"CAR"                       : _tr('Drive Only'),
    "WALK"                        : _tr('Walk Only')
};
