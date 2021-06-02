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

        editor: null,   //codemirror editor object

        procedure_code: "",
        procedure_last_updated: "",
        is_proc_saved: false,
        is_proc_deployed: false,

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

//    app_device.add_procedure = function () {
//        axios.post(add_proc_url, {
//                device_id: app_device.vue.device_id,
//                procedure_name: app_device.vue.procedure_name,
//
//            }).then(function (response) {
//            app_device.vue.rows.push({
//                id: response.data.id,
//                device_id: app_device.vue.device_id,
//                procedure_name: app_device.vue.procedure_name,
//                _state: {device_id: "clean", procedure_name: "clean"},
//            });
//            app_device.enumerate(app_device.vue.rows);
//            app_device.reset_form();
//            app_device.set_add_status(false);
//        });
//    };


    // LOAD LATEST PROCEDURE
    app_device.load_procedure = function(){
        axios.get(load_procedure_url)
        .then(function (response) {
            // console.log(response.data.proc);

            app_device.vue.procedure_code = response.data.proc.procedure_code;
            app_device.vue.procedure_last_updated = response.data.proc.last_updated;

            console.log("procedure_code: " + app_device.vue.procedure_code);
            console.log("procedure_last_updated: " +app_device.vue.procedure_last_updated);

            app_device.vue.editor.setValue(""+app_device.vue.procedure_code);

        });
    }


    // SAVE PROCEDURE
    app_device.save_procedure = function(){
        // get value from editor
        app_device.vue.procedure_code = app_device.vue.editor.getValue();
        console.log("\nupdated code");
        console.log(app_device.vue.procedure_code);

        // add to procedure table
            axios.post(add_updated_procedure_url, {
                device_id: app_device.vue.device_id,
                procedure_code: app_device.vue.procedure_code

            }).then(function (response) {
                console.log("inserted event into procedure table");

                console.log(response.data.proc_last_updated);
                app_device.vue.procedure_last_updated = response.data.proc_last_updated;
                app_device.vue.is_proc_saved = true;

            });
        // enable deploy button?

    }


    // DEPLOY PROCEDURE
    app_device.deploy_procedure = function(){
        // options:
        // 1. send post request to client
        // 2. update status here, client will keep polling and get latest details

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

        // load code editor component:
        app_device.vue.editor = CodeMirror.fromTextArea(document.getElementById('codearea'), {
            lineNumbers: true,
            styleActiveLine: true,
            matchBrackets: true,
            mode: 'python'
           });

        app_device.vue.editor.on('change', function(cm) {
            app_device.procedure_code = cm.getValue();
        });

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
