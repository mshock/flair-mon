
setInterval(function() {
	var reload = false;
	$.ajax({
		url: 'http://overwatchflair.com',
		type: "get",
		statusCode: {
			404: function() {
				//alert( "page not found" );
			},
			304: function() { 
				//alert( "page not updated" );
			},
			200: function() { 
				//alert("page retrieved!");
				reload = true;
			},
		},
		success: function() {
			//alert('success!')
			if(reload) {
				$('.ticker').text('');
				$('.scoreboard').text('');
			}
		},
		error: function() {
			//alert('error!'
		)},
	});	
}, 5000);