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

function toast(msg) {
    let x = document.getElementById("snackbar");
    x.innerText = msg;
    x.className = "show";
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
}

function get_confirmation(title, question, cb_yes, cb_no) {
    let dialog = $('#conf_modal')
    $('#conf_title').text = title;
    $('#conf_question').text = question;
    $('#conf_yes').off("click");
    if (typeof(cb_yes) === "function") {
        $('#conf_yes').click(cb_yes);
    }
    $('#conf_no').off("click");
    if (typeof(cb_no) === "function") {
        $('#conf_no').click(cb_no);
    }
    dialog.modal();
}

(function () {
    "use strict";
    let prop = {
        property_id: "",
        edit_endpoint: "",
        status: null,
        status_btn: null
    };

    prop.init = function () {
        prop.property_id = document.getElementById("property_id").value;
        prop.edit_endpoint = document.getElementById("edit_property").action;
        prop.assign_button_clicks();
        prop.status = document.getElementById("status");
        prop.status_btn = document.getElementById("toggle_status");
        prop.status_btn.addEventListener("click", prop.toggle_status);
    };

    prop.assign_button_clicks = function () {
        //Hook up handlers to buttons everywhere!
        $(".saveform").off("click");
        $(".saveform").click(prop.save_form);

        $(".additem").off("click");
        $(".additem").click(prop.add_item);

        $(".delitem").off("click");
        $(".delitem").click(prop.remove_item);
    };

    prop.toggle_status = function () {
        // send inverting action
        let data;
        if (prop.status_btn.value === "Publish") {
            data = {
                type: "action",
                action: "status",
                status: "A",
            }
        } else {
            data = {
                type: "action",
                action: "status",
                status: "U",
            }
        }
        // get response
        prop.send_post(data, function (response) {
            let parsed = JSON.parse(response);
            if (parsed.result === "success") {
                toast("Status updated");
                if (parsed.successes.status === "A") {
                    prop.status.innerText = "Listed";
                    prop.status_btn.value = "Unpublish";
                } else {
                    prop.status.innerText = "Unpublished";
                    prop.status_btn.value = "Publish";
                }
            } else {
                console.warn(parsed.errors);
                toast("Error saving! Did you fill in all the fields properly?");
            }
        });
    };

    prop.test_action = function (data) {
        console.log("Msg to", prop.property_id, ":", data);
    };

    prop.send_post = function (data, cb_success) {
        let cb = cb_success || prop.post_success;
        send_post(prop.edit_endpoint, data, cb, prop.post_fail);
    };

    prop.post_success = function (response) {
        let data = JSON.parse(response);
        console.log("response:", data.result);
        if (data.result === "success") {
            console.log(data.successes);
            if (data.errors) {
                console.warn(data.errors);
            }
        } else {
            console.warn(data.errors);
            if (data.successes) {
                console.log(data.successes);
            }
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
        prop.send_post(data, function (response) {
            let parsed = JSON.parse(response);
            if (parsed.result === "success") {
                // TODO: on success, use the returned data to replace the data in the form
                // (in case the ingestion changed anything)
                toast("Updates saved");
            } else {
                console.warn(parsed.errors);
                toast("Error saving! Did you fill in all the fields properly?");
            }
        });
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
        prop.send_post(data, function (response) {
            let parsed = JSON.parse(response);
            if (parsed.result === "success") {
                prop.add_html(data.pk, parsed.successes.model, parsed.successes.pk)
            }
        });
    };

    prop.add_html = function(parent_key, model, child_key) {
        // find host object
        console.log("parent_key", parent_key);
        console.log("model", model);
        console.log("child_key", child_key);
        let host;
        let markup;
        let child;
        if (model === "houseroom") {
            host = document.getElementById('house_' + parent_key + "_rooms");
            markup = templates.houseroom.replace(/000/g, child_key);
            child = document.createElement("tr");
            child.id = "houseroom_" + child_key + "_card";
            child.innerHTML = markup;
            host.appendChild(child);
        } else if (model === "suiteroom") {
            host = document.getElementById('suite_' + parent_key + "_rooms");
            markup = templates.suiteroom.replace(/000/g, child_key);
            child = document.createElement("tr");
            child.id = "suiteroom_" + child_key + "_card";
            child.innerHTML = markup;
            host.appendChild(child);
        } else if (model === "structure") {
            host = document.getElementById('lot_' + parent_key + "_structures");
            markup = templates.structure.replace(/000/g, child_key);
            child = document.createElement("div");
            child.id = "structure_" + child_key + "_card";
            child.className = "card"
            child.innerHTML = markup;
            host.appendChild(child);
        } else if (model === "lot") {
            host = document.getElementById('property_' + parent_key + "_lots");
            markup = templates.lot.replace(/000/g, child_key);
            child = document.createElement("div");
            child.id = "lot_" + child_key + "_card";
            child.className = "card"
            child.innerHTML = markup;
            host.appendChild(child);
        } else if (model === "house") {
            host = document.getElementById('property_' + parent_key + "_houses");
            markup = templates.house.replace(/000/g, child_key);
            child = document.createElement("div");
            child.id = "house_" + child_key + "_card";
            child.className = "card"
            child.innerHTML = markup;
            host.appendChild(child);
        } else if (model === "suite") {
            host = document.getElementById('property_' + parent_key + "_suites");
            markup = templates.suite.replace(/000/g, child_key);
            child = document.createElement("div");
            child.id = "suite_" + child_key + "_card";
            child.className = "card"
            child.innerHTML = markup;
            host.appendChild(child);
        }
        prop.assign_button_clicks();
    };

    prop.remove_item = function (action) {
        let btn = action.target;
        let data = {
            type: "action",
            action: "remove",
            model: btn.dataset.model,
            pk: btn.dataset.pk,
        };
        // get confirmation before proceeding (unless it's just a room)
        if (data.model !== "houseroom" && data.model !== "suiteroom") {
            get_confirmation("Please Confirm", "Are you sure you want to delete this " + data.model + "?", function () {
                prop.send_post(data, function (response) {
                    let parsed = JSON.parse(response);
                    if (parsed.result === "success") {
                        prop.remove_html(data.model, data.pk);
                    }
                });
            });
        } else {
            prop.send_post(data, function (response) {
                let parsed = JSON.parse(response);
                if (parsed.result === "success") {
                    prop.remove_html(data.model, data.pk);
                }
            });
        }
    };

    prop.remove_html = function (model, key) {
        if (model === "property") {
            window.location.replace("/")
        } else {
            let card = "#" + model + "_" + key + "_" + "card";
            $(card).remove();
        }
    };

    //install layout
    window.prop = prop;
    window.onload = function () {
        prop.init();
    };
}());
