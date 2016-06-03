
setInterval(function() {
	var reload = false;
	$.ajax({
		url: 'http://www.overwatchflair.com',
		type: "GET",
		statusCode: {
			404: function() {
				alert( "page not found" );
			},
			304: function() { 
				alert( "page not updated" );
			},
			200: function() { 
				alert("page retrieved!");
				reload = true;
			},
		},
		error: function() {alert('success!')}
	});	
}, 5000);