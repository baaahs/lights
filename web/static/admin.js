(function() {

    var words = [
        "Merino",
        "BAAAHS",
        "Flocker",
        "Cheviot",
        "Suffolk",
        "Pearl",
        "Bibrik"
    ];

    var resetWord = "oops";

    function chooseNewResetWord() {
        var newWord = resetWord;
        while(newWord == resetWord) {
            newWord = words[Math.floor((Math.random() * words.length))];
        }
        resetWord = newWord;

        $("#resetWord").text(newWord);
    }        

    function checkReset() {
        var val = $("#resetWordEntry").val();

        if (val != resetWord) {
            B.showError("That's the wrong reset word.");
            return
        }

        var el = $(this);
        el.addClass("loading");
        B.api("/server_reset", {
            data: {please: true}
            , success: function(data) {
                if (data.ok) {
                    B.showMessage("Success. The server said ok. This will take a couple of seconds.");
                    document.location.reload();
                } else {
                    msg = data.msg || "No message from the sever";

                    B.showError(msg);
                }

            }
            , error: function(j,s,err) {
                B.showError("Failed to reset: "+err);
            }
            , complete: function() {
                el.removeClass("loading");
                chooseNewResetWord();
            }
        });
    }

    $(document).ready(function() {
        chooseNewResetWord();
        $(".ui.reset.button").on("click", checkReset);
    })

})()