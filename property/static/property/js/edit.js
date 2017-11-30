function send_post(destination, data, cb_success, cb_fail) {
    "use strict";
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        let DONE = 4; // readyState 4 means the request is done.
        let OK = 200; // status 200 is a successful return.
        if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
                cb_success(xhr.responseText, xhr); // "This is the returned text."
            } else {
                cb_fail("Error: " + xhr.status, xhr); // An error occurred during the request.
            }
        }
    };

    let packaged_data = JSON.stringify(data);
    xhr.open("POST", destination);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.send(packaged_data);
}

function objectifyForm(formElement) {
  let formArray = $(formElement).serializeArray();
  let returnObj = {};
  for (var i = 0; i < formArray.length; i++){
    returnObj[formArray[i]['name']] = formArray[i]['value'];
  }
  return returnObj;
}

(function () {
    "use strict";
    let prop = {
        property_id: "",
        edit_endpoint: "",
    };

    prop.init = function () {
        prop.property_id = document.getElementById("property_id").value;
        prop.edit_endpoint = document.getElementById("edit_property").action;

        //Hook up handlers to buttons everywhere!
        $(".saveform").click(prop.save_form);
        $(".additem").click(prop.add_item);
    };

    prop.test_action = function (data) {
        console.log("Msg to", prop.property_id, ":", data);
    };

    prop.send_post = function (data) {
        send_post(prop.edit_endpoint, data, prop.post_success, prop.post_fail);
    }

    prop.post_success = function (response, cb_success) {
        let cb = cb_success || prop.post_success;
        let data = JSON.parse(response);
        console.log("response:", data.result);
        if (data.result === "success") {
            console.log(data.successes);
        } else {
            console.warn(data.errors);
        }
    };

    prop.post_fail = function (response, xhr) {
        console.error(response);
        console.log(xhr);
    };

    prop.save_form = function (action) {
        let form = action.target.form;
        let data = objectifyForm(form);
        //prop.test_action(data);
        prop.send_post(data);
    };

    prop.add_item = function (action) {
        let btn = action.target;
        let data = {
            type: "action",
            action: "add",
            model: btn.dataset.model,
            pk: btn.dataset.parent,
        };
        //prop.test_action(data);
        prop.send_post(data);
    };

    prop.remove_item = function (action) {
        let btn = action.target;
        let data = {
            type: "action",
            action: "remove",
            model: btn.dataset.model,
            pk: btn.dataset.parent,
        };
        //prop.test_action(data);
        prop.send_post(data);
    };

    //install layout
    window.prop = prop;
    window.onload = function () {
        prop.init();
    };
}());
