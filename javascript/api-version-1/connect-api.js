var ws;
//var serverLocation = "ws://" + window.location.host + "/connect/1/services";
var serverLocation = "ws://connect.aerius.nl/connect/1/services";

function sendData() {
  validationPanel.innerHTML = "";
  if (setupConnection()) {
      selectedFile = document.getElementById("files").files[0];
      if (selectedFile) {
    	  readFileAndSend(selectedFile);
      } else {
    	  validationPanel.textContent = "Geen bestand gekozen";
      }
  } else {
     validationPanel.appendChild(document.createElement("div")).appendChild(document.createTextNode('Websocket connection not available.'));    
  }
}

function setupConnection() {
  var webSocketValid = true;
  if ("WebSocket" in window) {
    ws = new WebSocket(serverLocation);
    
    ws.onerror = function (event) {
    	alert("Verbinding verbroken :" + event.code  );
    }
    
    ws.onclose = function (event) {
      alert("Verbinding verbroken :" + event.code  );
      webSocketValid = false;
    }
    
    ws.onmessage = function helloCallback(event) {
	  var response = JSON.parse(event.data);
	  console.log(response);
	  if (response.result) {
	    if (response.result.successfull) {
	    	validationPanel.textContent = "GML document is in orde."
	    		
	    } else {
	      var errors = ["GML Document is niet correct."];
	      var i, il = response.result.errors.length;
	      
	      for (i = 0; i < il; i++) {
	        var error = response.result.errors[i];
	        var errorText = error.errorDescription + "(" + error.errorCode + ")";
	        
	        if (error.data) {
	          errorText += " {" + error.data.join(",") + "}.";
	        }
	        errors.push(errorText);
	      }
	      validationPanel.textContent = errors.join("\n");
	    }
	  } else if (response.error) {
	    validationPanel.textContent = "Error: " + response.error.message;
	    
	  } else {
	    validationPanel.textContent = "Onverwachte fout: " + response;
	    
	  }
	};
    	
  } else {
    alert("Geen websocket support in deze browser");
    webSocketValid = false;
  }
  return webSocketValid;
}

function readFileAndSend(file) {
   var reader = new FileReader();
   reader.onload = function(event) {
       var dataurl = event.target.result;
       var encodedData = dataurl.substring(dataurl.lastIndexOf(",") + 1);
       var fileDto = {
           "name": file.name,
           "data": encodedData
       };
       validateGml(fileDto);
   };
   reader.readAsDataURL(file);
}

function validateGml(fileDto) {
	var rpcRequest = {	
		"jsonrpc" : "2.0",
    	"id" : Date.now(),
    	"method" : "gmlconvert.convert",
    	"params" : {
    	"file" : fileDto,
    	}
	};
	var request = JSON.stringify(rpcRequest);
	console.log(request);
	validationPanel.textContent = "Bezig met verzenden.";
	this.send(request, function () {
		validationPanel.textContent = "Document verzonden, bezig met verwerken."
	});
}

this.send = function (message, callback) {
    this.waitForConnection(function () {
        ws.send(message);
        if (typeof callback !== 'undefined') {
          callback();
        }
    }, 1000);
};

this.waitForConnection = function (callback, interval) {
    if (ws.readyState === 1) {
        callback();
    } else {
        var that = this;
        setTimeout(function () {
            that.waitForConnection(callback, interval);
        }, interval);
    }
};