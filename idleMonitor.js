var IdleMonitor = Class.create({

    debug: false,
    idleInterval: 30000, // idle interval, in milliseconds
    active: null,
    initialize: function() {
        document.observe("mousemove", this.sendActiveSignal.bind(this));
        document.observe("keypress", this.sendActiveSignal.bind(this));
        this.timer = setTimeout(this.sendIdleSignal.bind(this), this.idleInterval);
    },

    // use this to override the default idleInterval
    useInterval: function(ii) {
        this.idleInterval = ii;
        clearTimeout(this.timer);
        this.timer = setTimeout(this.sendIdleSignal.bind(this), ii);
    },

    sendIdleSignal: function(args) {
        // console.log("state:idle");
        document.fire('state:idle');
        this.active = false;
        clearTimeout(this.timer);
    },

    sendActiveSignal: function() {
        if(!this.active){
            // console.log("state:active");
            document.fire('state:active');
            this.active = true;
            this.timer = setTimeout(this.sendIdleSignal.bind(this), this.idleInterval);
        }
    }
});




// Some other object :
Event.observe(document, 'state:idle', your-on-idle-functionality);
Event.observe(document, 'state:active', your-on-active-functionality);
