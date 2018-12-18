
//illumiCloud constructor
    let illumiCloud = {
        //vars
        name: "illumiCloud",
        recording: false,
        hasLocation: false,
        hasLightSensor: false,
        lat_y : null,
        lon_x : null,
        sensor: null,
        illuminance: null,
        rec_interval: null,

        //init
        init : function() {
            //if location access report success
            if (navigator.geolocation) {
                navigator.geolocation.watchPosition(function (position) {
                    illumiCloud.updateLocation(position);
                }, error, options = {
                    timeout: 0, enableHighAccuracy: true, maximumAge: Infinity
                });
            }
            //check browser compatibilitiy
            /*if ("AmbientLightSensor" in window) {
                try {
                    this.hasLightSensor = true;
                    sensor = new AmbientLightSensor();
                    sensor.addEventListener("reading", function (event) {
                        this.illuminance = sensor.illuminance;
                        this.update();
                    });
                    sensor.start();
                    this.hasLightSensor = true;
                } catch (e) {
                    console.error(e);
                }
            }*/
            console.log("Checking for light sensor");
            if ("ondevicelight" in window) {
                console.log("Light Sensor found");
                this.hasLightSensor = true;

                window.addEventListener('devicelight', function(event) {
                    illumiCloud.illuminance = event.value;
                    console.log(illumiCloud.illuminance + "=" + event.value);
                    illumiCloud.update();}
                );
            }
            //else{
            //    alert("Your browser does not support the light sensor API.")
            //}
			this.update();
            console.log(this.name + " initialized");
        },

        //report lat and lon to console on success
        updateLocation : function(position){
            this.lat_y = position.coords.latitude.toFixed(5);
            this.lon_x = position.coords.longitude.toFixed(5);
            this.hasLocation = true;
            display_loc(this.lon_x, this.lat_y);
        },

        //on update
        update : function(){
            //console.log("updated");
            display_loc(this.lon_x, this.lat_y);
            display_lux(this.illuminance);

			/*if(gatherLux.recording){
				if((illumiCloud.illuminance > 0) && (illumiCloud.illuminance < 5000)){
						illumiCloud.rec_interval = setInterval(gatherLux.collect, 250);
						gatherLux.record();
						gatherLux.record();
				} else if ((illumiCloud.illuminance <= 0) || (illumiCloud.illuminance >= 5000)) {
						illumiCloud.rec_interval = setInterval(gatherLux.collect, 5000);
						gatherLux.record();
						gatherLux.record();
				}
			}*/
			
			if (gatherLux.recording){
				if((gatherLux.record_id % 2) == 1){
					document.getElementById("rec_button").innerHTML = "<span color = 'magenta'>pause</span>";
				}
			}
			
            if(gatherLux.record_id > 0){
                if(illumiCloud.recording){
                    document.getElementById("status").innerHTML = "Recorded " + (gatherLux.record_id) + " points.";
                    //document.getElementById("clr_button").innerHTML = "<span style = 'color: gray'>clear</span>";
					document.getElementById("exp_button").innerHTML = "<span style = 'color: gray'>export</span>";
                }
                else {
                    document.getElementById("status").innerHTML = "Continue recording or export " + (gatherLux.record_id) + " points.";
                    //document.getElementById("clr_button").innerHTML = "<span style = 'color: magenta'>clear</span>";
					document.getElementById("exp_button").innerHTML = "<span style = 'color: cyan'>export</span>";
					if (gatherLux.list == []){
						document.getElementById("rec_button").innerHTML = "<span style = 'color: white'>record</span>";
					}
                }
            }
            else {
				document.getElementById("status").innerHTML = "Press record to start logging.";    
                //document.getElementById("clr_button").innerHTML = "<span style = 'color: gray'>clear</span>";
				document.getElementById("exp_button").innerHTML = "<span style = 'color: gray'>export</span>";
            }

        },


        //toggle recording and report to console
        record : function() {
            if(illumiCloud.hasLocation /*&& illumiCloud.hasLightSensor*/) {
                this.recording = !this.recording;
            }
			//move to display_update
            if (this.recording) {
                illumiCloud.rec_interval = setInterval(gatherLux.collect, 1000);
				document.getElementById("rec_button").innerHTML = "<span style = 'color: magenta'>pause</span>";
            }
            else {
                clearInterval(this.rec_interval);
                document.getElementById("rec_button").innerHTML = "<span style = 'color: yellow'>continue</span>";
            }
            this.update();
            console.log("Recording: " + this.recording);
        }

    };

    //gatherLux constructor
    //reads sensor values into json lists to be uploaded
    let gatherLux = {
        //vars
        name: "gatherLux",
        record_id: 0,
        timestamp_ISO: null,
        list: [],
		csv_list: [], 
		csv_head: ["FID","datetime","lat_y","lon_x","lux"], //printing on single line; not field names print each time
		head_content: "",
        row_content: "",
		csv_content: "",
        json_list: null,
		encoded_uri: null,

        //init
        init: function(){
            console.log(this.name + " initialized");
            //console.log(this.list);
        },
        //collect
        collect: function() {
            gatherLux.timestamp_ISO = new Date().toISOString();
            gatherLux.list[gatherLux.record_id] = [gatherLux.record_id, gatherLux.timestamp_ISO, illumiCloud.lat_y, illumiCloud.lon_x, illumiCloud.illuminance];
            console.log(gatherLux.list[gatherLux.record_id]);
            gatherLux.record_id++;
        },
        //upload
        upload: function(){
            if(!illumiCloud.recording){
                gatherLux.json_list = JSON.stringify(gatherLux.list);
                console.log(gatherLux.json_list);
            }
		},
		        
		//export: exp_csv()
		exp_csv: function(){
            if(!illumiCloud.recording & gatherLux.record_id != 0){
				gatherLux.csv_list = gatherLux.list;
				
				var h = 0;
				var i = 0;
				var j = 0;
				
				//console.log(gatherLux.list);
				//console.log(gatherLux.csv_list);
				//console.log(gatherLux.row_content);
				//console.log(gatherLux.csv_head.length);
				//console.log(gatherLux.csv_head[0]);
				//console.log(gatherLux.csv_list.length);
				//console.log(gatherLux.csv_list[0]);
				//console.log(gatherLux.csv_list[0].length);
				//console.log(gatherLux.csv_list[0][2]);
				
				for (h; h < gatherLux.csv_head.length; h++){
					if(h == gatherLux.csv_head.length-1){		
						gatherLux.head_content += gatherLux.csv_head[h] + ';';
					} else {
						gatherLux.head_content += gatherLux.csv_head[h] + ',';
					}
				}
				//console.log(gatherLux.head_content);
				
				for (i; i < gatherLux.csv_list.length; i++){
					j = 0;
					for (j; j < gatherLux.csv_list[i].length; j++){
						//console.log(gatherLux.csv_list[i]);
						//console.log(gatherLux.csv_list[i][j]);
						if(j == gatherLux.csv_list[i].length-1){		
							gatherLux.row_content += gatherLux.csv_list[i][j] + ';';
						} else {
							gatherLux.row_content += gatherLux.csv_list[i][j] + ',';
						}
					}
				}
				//console.log(gatherLux.row_content);
				
				this.csv_content = this.head_content + this.row_content;
				
				//console.log(gatherLux.head_content);
				//console.log(gatherLux.row_content);
				//console.log(gatherLux.csv_content);
				encoded_uri = encodeURI(gatherLux.csv_content);
				var a = document.createElement('a');
				var dt =  Date.now();
				a.href = 'data:text/csv,' + gatherLux.csv_content;
				a.target = '_blank';
				a.download = 'gatherLux' + dt + '.csv';
				document.getElementById("exp_button").innerHTML = "downloading";
				document.getElementById("rec_button").innerHTML = "<span style = 'color: white'>record</span>";
				document.body.appendChild(a);
				a.click();
				gatherLux.clear();
			}
        },
	
		//clear
        clear: function(){            
			document.getElementById("exp_button").innerHTML = "empty";
			//document.getElementById("clr_button").innerHTML = "cleared";
			gatherLux.record_id = 0;
			gatherLux.list = [];
			gatherLux.csv_list = [];
			gatherLux.csv_head, gatherLux.csv_row, gatherLux.csv_content = "";
			encoded_uri = null;
			location.reload(true);
   		},

    };

    //global functions
    function error(err) {
        console.warn('ERROR(' + err.code + '): ' + err.message);
    }

    function display_loc(x,y) {
        document.getElementById("x").innerHTML = x;
        document.getElementById("y").innerHTML = y;
    }

    function display_lux(l) {
        document.getElementById("l").innerHTML = l + " lux";
    }

    function rec_button(){
        illumiCloud.record();
    }

    function clr_button(){
        gatherLux.clear();
    }

    function exp_button(){
        gatherLux.exp_csv();
    }

    function initialize(){
        console.log("initializing");
        illumiCloud.init();
        gatherLux.init();
        //brightMap.init();
		//console.log(illumiCloud.lat_y + ',' + illumiCloud.lon_x);
    }
