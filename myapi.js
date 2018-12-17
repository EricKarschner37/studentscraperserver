var http = require('http');
var express = require('express');

var app = express();

var services = {
"Cengage" : {}
"Yabla" : {}
}

var csv = require("fast-csv");
var fs = require('file-system');

function addService(name, user, pass){
  var csvStream = csv.createWriteStream({headers: true}),
    writableStream = fs.createWriteSTream("services.csv");

  writableStream.on("finish", function(){
    console.log("done writing");
  });

  csvStream.pipe(writableStream);
  csvStream.write({"Name": name, "Username": user, "Password": pass, "Assignments": "0", "Date": "N/A"});
  csvStream.end();
}

function readServices(){
  csv
   .fromPath("services.csv", { headers : ["Name","Username",,"Assignments","Date"]})
   .on("data", function(data){
     try {
       services[data["Name"]][data["Username"]] = data;
     }
   })
   .on("end", function(){
       console.log(services)
       console.log("done");
   });
}



app.use(express['static'](__dirname ));

// Get information for the specified service/username combo
app.get('/service/:name/:user', function(req, res) {
  res.status(200).send(services[req.params.name][req.params.user]);
});

// Add a user to the list
app.get('/add/:name/:user/:pass', function(req, res) {
  if (req.params.name in services){
    if !(req.params.user in services[req.params.name] || req.params.pass != services[req.params.name][req.params.user]["Password"]){
      addService(req.params.name, req.params.user, req.params.pass);
      readServices();
    res.status(200).send(services[req.params.name][req.params.user]);
  } else {
    res.status(500).send('Oops, Something went wrong!')
  }
});

// Express route for any other unrecognised incoming requests
app.get('*', function(req, res) {
  res.status(404).send('Unrecognised API call');
});

// Express route to handle errors
app.use(function(err, req, res, next) {
  if (req.xhr) {
    res.status(500).send('Oops, Something went wrong!');
  } else {
    next(err);
  }
});

app.listen(3000);
console.log('App Server running at port 3000');
