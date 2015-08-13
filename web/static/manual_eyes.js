(function() {

    var presets = [];

    function loadEffectPresets() {
        B.api("/effect_presets", {        
            success: function(data, status, xhr) {
                console.log("Loaded presets ", data);
                presets = data;

                selection = 0;
                selectPreset();
            }

            , error: function(xhr, status, err) {
                B.showError("Unable to load presets: "+ err);
            }
        });
    }

    var selection = 0;

    function selectPreset() {
        var ix = selection

        preset = presets[ix];

        console.log("Selecting ", preset);

        shutter_type = preset.shutter_type || "open"
        $("input[name=shutter_type][value="+shutter_type+"]").parent().checkbox("check");

        shutter_speed = preset.shutter_speed || 0.0;
        $("input[name=shutter_speed]").val(shutter_speed);


        gobo_rotation = preset.gobo_rotation || 0.0;
        $("input[name=gobo_rotation]").val(gobo_rotation);
        gobo = preset.gobo || 0;
        $(".dropdown.gobo").dropdown("set selected", gobo);

        gobo_shake = preset.gobo_shake_speed || 0.0;
        $("input[name=gobo_shake]").val(gobo_shake);

        effect_mode = preset.effect_mode || "none";
        $("input[name=effect_mode][value="+effect_mode+"]").parent().checkbox("check");
        effect_rotation = preset.effect_rotation || 0.0;
        $("input[name=effect_rotation]").val(effect_rotation);

        focus = preset.focus || 0.0;
        $("input[name=focus]").val(focus);

        frost = preset.frost || "none";
        $("input[name=frost_type][value="+frost+"]").parent().checkbox("check");
        frost_speed = preset.frost_speed || 0.0;
        $("input[name=frost_speed]").val(frost_speed);

        external = preset.external_speed_modifies || "nothing";
        $(".dropdown.external").dropdown("set selected", external);
    }

    function btnSelectPreset() {
        var el = $(this);

        $(".ui.icon.effect.button").removeClass("active");
        //$(".ui.icon.effect.button[data-ix="+ix+"]").addClass("active");
        el.addClass("active");


        selection = parseInt(el.data("ix"));
        // selectPreset();
    }

    function effectToJSON() {
        var data = {}

        data.shutter_type = $("input:radio[name=shutter_type]:checked").val()
        data.shutter_speed = parseFloat($("input[name=shutter_speed]").val());

        data.gobo_rotation = parseFloat($("input[name=gobo_rotation]").val());
        data.gobo = $(".dropdown.gobo").dropdown("get value")
        data.gobo_shake_speed = parseFloat($("input[name=gobo_shake]").val());

        data.effect_mode = $("input:radio[name=effect_mode]:checked").val()
        data.effect_rotation = parseFloat($("input[name=effect_rotation]").val());

        data.focus = parseFloat($("input[name=focus]").val());
        if (data.focus == 0) {
            data.focus = null;
        }

        data.frost = $("input:radio[name=frost_type]:checked").val()
        data.frost_speed = parseFloat($("input[name=frost_speed]").val());

        data.external_speed_modifies = $(".dropdown.external").dropdown("get value")

        return data;
    }



    function save() {
        var data = effectToJSON();
        console.log("Saving ", data, " to selection ", selection);

        data.effect_index = selection;

        var el = $(this);
        el.addClass("loading");
        B.api("/save_effect", {
            data: data
            , success: function() {
                console.log("Success!")

                delete data.effect_index;
                presets[selection] = data;
            }
            , error: function(j,s,err) {
                B.showError("Failed to save: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
            }
        });
    }

    function load() {
        selectPreset();
    }

    function grab() {
        var data = {};

        try {
            data["enabled"] = true;

            data["pos_is_xyz"] = $("#pos_is_xyz").checkbox("is checked");
            data["x_pos"] = parseFloat($("#x_pos").val());
            data["y_pos"] = parseFloat($("#y_pos").val());
            data["z_pos"] = parseFloat($("#z_pos").val());
            data["dimmer"] = parseFloat($("#dimmer").val());
            data["color_pos"] = parseInt($("#color_pos").val());

            data["effect"] = effectToJSON();


            if ( $("#btnParty").hasClass("active") || $("#btnBoth").hasClass("active")) {
                data["set_party"] = true;
            }

            if ( $("#btnBusiness").hasClass("active") || $("#btnBoth").hasClass("active")) {
                data["set_business"] = true;
            }

            var el = $(this);
            el.addClass("loading");
            B.api("/manual_eyes", {
                data: data
                , success: function() {
                    console.log("Success!")
                }
                , error: function(j,s,err) {
                    B.showError("Failed to grab: "+err);
                }
                , complete: function() {
                    el.removeClass("loading");
                }
            });
        } catch (e) {
            B.showError("Can't grab :" + e)
        }
    }


    function release() {
        var data = {};

        data["enabled"] = false;

        var el = $(this);
        el.addClass("loading");
        B.api("/manual_eyes", {
            data: data
            , success: function() {
                console.log("Success!")
            }
            , error: function(j,s,err) {
                B.showError("Failed to grab: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
            }
        });
    }

    function setActive() {
        var el = $(this);

        $(".ui.eye.button").removeClass("active");
        el.addClass("active");
    }



    function storePosition() {
        var el = $(this);
        if (el.hasClass("disco")) {
            which = "disco";
        } else {
            which = "headlights";
        }

        var data = {
            position: which
        }

        try {
            data["pos_is_xyz"] = $("#pos_is_xyz").checkbox("is checked");
            data["x_pos"] = parseFloat($("#x_pos").val());
            data["y_pos"] = parseFloat($("#y_pos").val());
            data["z_pos"] = parseFloat($("#z_pos").val());

            if ( $("#btnParty").hasClass("active") || $("#btnBoth").hasClass("active")) {
                data["set_party"] = true;
            }

            if ( $("#btnBusiness").hasClass("active") || $("#btnBoth").hasClass("active")) {
                data["set_business"] = true;
            }

            el.addClass("loading");
            B.api("/store_position", {
                data: data
                , success: function() {
                    console.log("Success!")
                }
                , error: function(j,s,err) {
                    B.showError("Failed to store: "+err);
                }
                , complete: function() {
                    el.removeClass("loading");
                }
            });
        } catch (e) {
            B.showError("Can't store :" + e)
        }    
    }


    $(document).ready(function() {
        loadEffectPresets();

        // $("tbody").on("click", "tr.shutter", clickShutter);
        $(".ui.checkbox").checkbox();
        $(".ui.dropdown").dropdown();

        $(".ui.eye.button").on("click", setActive);

        $(".ui.grab.button").on("click", grab);
        $(".ui.release.button").on("click", release);

        $(".ui.store.disco.button").on("click", storePosition);
        $(".ui.store.headlights.button").on("click", storePosition);

        $(".ui.save.preset.button").on("click", save);
        $(".ui.load.preset.button").on("click", load);

        $(".ui.icon.effect.button").on("click", btnSelectPreset)
    })

})()