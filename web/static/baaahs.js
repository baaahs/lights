
console.log("baaahs started");


B = new function() { 

    var B = this;

    B.api = function(url, settings) {
        if (settings.data) {
            settings.data = JSON.stringify(settings.data)
            settings.type = "POST"
        }
        settings.dataType = "json";
        settings.processData = false;
        settings.url = url;
        settings.contentType = "application/json"

        return $.ajax(settings);
    }


    B.showError = function(msg) {
        alert(msg);
    }

    B.showMessage = function(msg) {
        alert(msg);
    }

}();