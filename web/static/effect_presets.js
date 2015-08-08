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

        $(".ui.icon.effect.button").removeClass("active");
        $(".ui.icon.effect.button[data-ix="+ix+"]").addClass("active");


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

        selection = parseInt(el.data("ix"));
        selectPreset();
    }

    function toJSON() {
        data = {}

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

    // function makePresets() {
    //     for(var i=0; i<presets.length; i++) {
    //         s = [];
    //         preset = presets[i];

    //         s.push("<div class='ui item preset' data-ix='");
    //         s.push(i);
    //         s.push("'>");

    //         s.push("")

    //         s.push(JSON.stringify(preset));


    //         s.push("</div>");
    //         $("#presetList").append(s.join(""))
    //     }
    // }

    // function clickShutter(evt) {
    //     //alert("Shutter on "+$(this).data("ix"))

    //     $(".ui.shutter.modal").modal("show");
    // }

    // function clickGobo(evt) {
    //     alert("Gobo on "+$(this).data("ix"))
    // }


    function save() {
        data = toJSON();
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

    $(document).ready(function() {
        loadEffectPresets();

        // $("tbody").on("click", "tr.shutter", clickShutter);
        $(".ui.checkbox").checkbox();
        $(".ui.dropdown").dropdown();

        $(".ui.primary.save.button").on("click", save);

        $(".ui.icon.effect.button").on("click", btnSelectPreset)
    })

})()