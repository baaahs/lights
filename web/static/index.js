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

    function updateStatus() {
        if (statusTimeout) {
            clearTimeout(statusTimeout);
            statusTimeout = null;
        }

        B.api("/status", {
            success: function(data) {
                console.log("Got status data");
                if (data.show) {
                    $("#currentShowName").text(data.show.name);
                }

                if (data.eo_show) {
                    $("#currentEOShowName").text(data.eo_show.name);
                    $("#eoShowItem").show();
                } else {
                    $("#eoShowItem").hide();
                }
            }
            , error: function(xhr, status, err) {
                console.log("Status err ", err);
            }
            , complete: function() {
                if (!statusTimeout) {
                    statusTimeout = setTimeout(updateStatus, 1000);
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

    $(document).ready(function() {
        console.log("document ready");

        $("i.eo.show.remove.icon").bind("click", stopEOShow);

        // Load the show names
        loadShows();
        updateStatus();
    });

})();