$(document).ready(function(){

    var getUserStatus = function(numberArg){
            var modelNumber ='358480786506'
            $.getJSON('http://localhost:12000/api/start_tracking?addr_num=' + numberArg ,function(data){
                if(data ='STARTED'){
                    console.log(data);
                $.getJSON('http://localhost:12000/api/user_status?addr_num=' + numberArg ,function(newdata){
                    if(newdata = 'unreachable'){
                        alert('You child became unreachable!');
                    }
                })
            };
        });
    };

    var move = function() {
        var elem = document.getElementById("myBar"); 
        var progress = document.getElementById("myProgress"); 
        var phoneInputVal = document.getElementById("phoneInput").value;
        progress.style.display = 'block';
        elem.style.display='block';  
        var width = 1;
        
        function frame() {
          if (width >= 100) {
              elem.style.display='none';
              setInterval(upDateLocation,1000);
              clearInterval(id);
              getUserStatus(phoneInputVal);
            $( "#dialog" ).dialog( "open" );
          } else {
            width++; 
            elem.style.width = width + '%'; 
          }
        }
        var id = setInterval(frame, 25);
      }

      document.getElementById("subBtn").addEventListener("click",move);

    var globalLat;
    var globalLong;

    var ourMap = new Maplace({
        map_options: {
            locations: [{lat :60.17072,lon:24.943043,icon:'http://maps.google.com/mapfiles/markerB.png'}],
            set_center: [60.17072, 24.943043],
            zoom: 15,
            mapTypeControl:false,
            clickableIcons:false,
           // panControl:false,
            scaleControl:false,
            streetViewControl:false,
            zoomControl:false,
            fullscreenControl : false,
        }
    }).Load();

    var currentLoc = ourMap.oMap.locations[0]
    globalLat = currentLoc.lat + ((Math.random() * 0.0005)-0.00025);
    globalLong = currentLoc.lon + ((Math.random() * 0.0005)-0.00025);

    var upDateLocation = function(){
        var currentLoc = ourMap.oMap.locations[0]
        globalLat += ((Math.random() * 0.001)-0.0005);
        globalLong += ((Math.random() * 0.001)-0.0005);

        ourMap.SetLocations([{lat:globalLat,lon:globalLong}],true)
    }
});