(function() {
    var shows = {};
    var showNames = [];

    function loadShows() {
        B.api("/shows", {        
            success: function(data, status, xhr) {
                console.log("Loaded shows ", data);
                shows = data;

                showNames = [];
                for(var name in shows) {
                    showNames.push(name);
                }
                showNames.sort();

                makeShows();
            }

            , error: function(xhr, status, err) {
                B.showError("Unable to load shows: "+ err);
            }
        });
    }

    function makeShows() {

        for(var i=0; i<showNames.length; i++) {
            var name = showNames[i];
            var show = shows[name];
            var s = "<div class='ui segment show ";
            if (show.random) {
                s += "random ";
            }
            s += show.type;
            s += "'><div class='ui header'>"+name+"";


            if (show.type == "master") {
                s += "<button class='ui right floated primary start button' data-name='"+name+"'>Start</button>"
            }
            if (show.controls_eyes) {
                s += "<button class='ui right floated secondary eyes button' data-name='"+name+"'>Eyes Only</button>"
            }

            "</div></div>";

            $("#showList").append(s)
        }

        $(".start.button").bind("click", startShow);
        $(".eyes.button").bind("click", startEOShow);
    }

    function startShow(evt) {
        console.log("start show this=",this," evt=",evt);
        var el = $(this);
        var name = el.data("name")

        el.addClass("loading");
        B.api("/start_show", {
            data: {
                name: name
            }
            , error: function(xhr, status, err) {
                B.showError("Unable to run show: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
                updateStatus();
            }
        })
    }

    function startEOShow(evt) {
        console.log("start EO show this=",this," evt=",evt);
        var el = $(this);
        var name = el.data("name")

        el.addClass("loading");
        B.api("/start_eo_show", {
            data: {
                name: name
            }
            , error: function(xhr, status, err) {
                B.showError("Unable to run EO show: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
                updateStatus();
            }
        })
    }

    var statusTimeout = null;

    function formatDuration(d) {
        if (!d) return "0s";

        d = parseInt(d);

        var tSecs = parseInt(d / 1000);
        var tMins = parseInt(tSecs / 60);

        var hours = parseInt(tMins / 60);
        var mins = tMins % 60;
        var secs = tSecs % 60;

        var out = [];
        if (hours > 0) {
            out.push(""+hours);
            out.push("h ");
        }
        if (mins > 0) {
            out.push(""+mins);
            out.push("m ");
        }
        out.push(secs);
        out.push("s");

        return out.join("");
    }

    function updateResetState(isParty, d) {
        $(".ui.eye.button."+(isParty ? "left": "right")).removeClass("active");

        if (d.mode) {
            $(".ui.eye.button." + (isParty ? "left": "right") + "." + d.mode).addClass("active");
            $("#"+(isParty ? "left": "right")+"State").text(d.mode.toUpperCase());
        }

        $("#"+(isParty ? "left": "right")+"ResetTime").text(formatDuration(d.duration));
    }

    function updateStatus() {
        if (statusTimeout) {
            clearTimeout(statusTimeout);
            statusTimeout = null;
        }

        B.api("/status", {
            success: function(data) {
                console.log("Got status data ", data);
                if (data.show) {
                    $("#currentShowName").text(data.show.name);

                    $("#currentShowRunTime").text(formatDuration(data.show.run_time))
                }

                if (data.eo_show) {
                    $("#currentEOShowName").text(data.eo_show.name);
                    $("#eoShowItem").show();
                } else {
                    $("#eoShowItem").hide();
                }

                $("#maxShowRuntime").text(formatDuration(data.max_time));

                if (data.reset_state) {
                    updateResetState(true, data.reset_state.party);
                    updateResetState(false, data.reset_state.business);
                }
            }
            , error: function(xhr, status, err) {
                console.log("Status err ", err);
            }
            , complete: function() {
                if (!statusTimeout) {
                    statusTimeout = setTimeout(updateStatus, 5000);
                }
            }
        });
    }

    function stopEOShow() {
        B.api("/stop_eo_show", {
            success:function() {
                updateStatus();
            }
        });
    }

    function setEyeState() {
        var el = $(this);

        var mode = "none";
        if (el.hasClass("on")) {
            mode = "on";
        } else if (el.hasClass("off")) {
            mode = "off"
        } else if (el.hasClass("reset")) {
            mode = "reset"
        }

        var isParty = el.hasClass("left");

        var data = {
            is_party: isParty,
            mode: mode
        }

        el.addClass("loading");
        B.api("/set_reset_state", {
            data: data
            , success:function(d) {
                if (d.ok) {
                    // Do nothing
                } else {
                    B.showError("Something went wrong. That didn't work :(");
                }
                updateStatus();
            }
            , error: function(xhr, status, err) {
                B.showError("ERROR: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
            }
        })
    }

    $(document).ready(function() {
        console.log("document ready");

        $("i.eo.show.remove.icon").bind("click", stopEOShow);

        $(".eye.button").bind("click", setEyeState);

        // Load the show names
        loadShows();
        updateStatus();
    });

})();