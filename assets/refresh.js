
setInterval(function() {
	var reload = false;
	$.ajax({
		url: 'http://overwatchflair.com',
		type: "get",
		success: function(data, textStatus, xhr) {
			if (xhr.status == 200) {
				$('.ticker').html($(data).find('.ticker').html());
				$('.scoreboard').html($(data).find('.scoreboard').html());
				$('.user-counts').html($(data).find('.user-counts').html());
			}
		},
		error: function() {
			//alert('error!')
		},
	});	
}, 5000);