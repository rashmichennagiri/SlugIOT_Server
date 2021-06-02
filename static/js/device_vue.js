// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app_device = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app_device) => {

    // all the vue data:
    app_device.data = {
        add_mode: false,

        device_id: "",

        procedure_code: "",
        procedure_last_updated: "",

        rows: [],   //contains list of all procedures
        outputs:[], //contains list of all outputs
        logs:[]     //contains list of all logs
    };

    app_device.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // This decorates the rows (e.g. that come from the server)
    // adding information on their state:
    // - clean: read-only, the value is saved on the server
    // - edit : the value is being edited
    // - pending : a save is pending.
    app_device.decorate = (a) => {
        a.map((e) => {e._state = {device_id: "clean", procedure_name: "clean"} ;});
        return a;
    }

    app_device.add_procedure = function () {
        axios.post(add_proc_url, {
                device_id: app_device.vue.device_id,
                procedure_name: app_device.vue.procedure_name,

            }).then(function (response) {
            app_device.vue.rows.push({
                id: response.data.id,
                device_id: app_device.vue.device_id,
                procedure_name: app_device.vue.procedure_name,
                _state: {device_id: "clean", procedure_name: "clean"},
            });
            app_device.enumerate(app_device.vue.rows);
            app_device.reset_form();
            app_device.set_add_status(false);
        });
    };


    // LOAD LATEST PROCEDURE
    app_device.load_procedure = function(){
        axios.get(load_procedure_url)
        .then(function (response) {
            app_device.vue.procedure_code = response.data.code;
            app_device.vue.procedure_last_updated = response.data; //TODO

            //app_device.decorate(app_device.enumerate(response.data.rows));
            console.log(app_device.vue.procedure_code);
        });
    }


    // SAVE PROCEDURE
    app_device.save_procedure = function(){

    }


    // DEPLOY PROCEDURE
    app_device.deploy_procedure = function(){

    }

    // LOAD OUTPUTS
    app_device.load_outputs = function(){
        // console.log("in js function: load_outputs");
        axios.get(load_outputs_url)
        .then(function (response) {
            app_device.vue.outputs = app_device.decorate(app_device.enumerate(response.data.rows));
            console.log(app_device.vue.outputs);
        });
    }


    // LOAD LOGS
    app_device.load_logs = function(){
        axios.get(load_logs_url)
        .then(function (response) {
            app_device.vue.logs = app_device.decorate(app_device.enumerate(response.data.rows));
            console.log(app_device.vue.logs);
        });
    }


    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app_device.methods = {
        save_procedure: app_device.save_procedure,
        deploy_procedure: app_device.deploy_procedure
    };

    // This creates the Vue instance.
    app_device.vue = new Vue({
        el: "#vue-target-individual-device",
        data: app_device.data,
        methods: app_device.methods
    });


    // Initialization: to load data from the database
    // Can also be a network call to the server to load data
    app_device.init = () => {

        // TODO remove this extra call, and get data from rows_devices in view_devices.html
        // load device details

        // load procedure details
        app_device.load_procedure();

        // load device outputs
        app_device.load_outputs();

        // load device logs
        app_device.load_logs();
    };

    // Call to the initializer.
    app_device.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app_device);







//        add_procedure: app_device.add_procedure,

//        set_add_status: app_device.set_add_status,
//        delete_contact: app_device.delete_contact,
//        start_edit: app_device.start_edit,
//        stop_edit: app_device.stop_edit,



//    app_device.reset_form = function () {
//        app_device.vue.device_id = "";
//        app_device.vue.procedure_name = "";
//    };

//    app_device.delete_contact = function(row_idx) {
//        let id = app_device.vue.rows[row_idx].id;
//        axios.get(delete_contact_url, {params: {id: id}}).then(function (response) {
//            for (let i = 0; i < app_device.vue.rows.length; i++) {
//                if (app_device.vue.rows[i].id === id) {
//                    app_device.vue.rows.splice(i, 1);
//                    app_device.enumerate(app_device.vue.rows);
//                    break;
//                }
//            }
//            });
//    };

//    app_device.set_add_status = function (new_status) {
//        app_device.vue.add_mode = new_status;
//    };

//    app_device.start_edit = function (row_idx, fn) {
//        app_device.vue.rows[row_idx]._state[fn] = "edit";
//    };

//    app_device.stop_edit = function (row_idx, fn) {
//        let row = app_device.vue.rows[row_idx];
//
//        if (row._state[fn] === "edit") {
//            row._state[fn] = "pending";
//            axios.post(edit_proc_url, {
//                    id: row.id,
//                    field: fn,
//                    value: row[fn], // row.first_name
//                }).then(function (result) {
//                row._state[fn] = "clean";
//            });
//        }
//        // If I was not editing, there is nothing that needs saving.
//    }
