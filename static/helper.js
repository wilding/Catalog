///////////////     GOOGLE SIGN IN    //////////////////////////////////////////////

var state = $("#helper").attr('data-state');
var route = $("#helper").attr('data-route');
/*
handle response that google api server sends to client
successful response
one time code to authorize server
access token client can use to make api calls in browser
*/
function signInCallback(authResult) {
	if (authResult['code']) {
		// Hide the sign in button now that the user is authorized
		$('#signinButton').attr('style', 'display: none');
		$('.flash').html('<i class="fa fa-spinner fa-spin"></i><strong> Connecting to Google</strong>');
		// Send the one-time-use code to the server.
		// If the server responds, write a 'login successful' message to the webpage and then redirect back to the main restaurants page
		$.ajax({
			type: 'POST',
			url: '/gconnect/?state=' + state,
			processData: false,
			contentType: 'application/octet-stream; charset=utf-8',
			data: authResult['code'],
			success: function(result) {
				if (result) {
					$('.flash').html(result);
					setTimeout(function() {
						window.location.href = route;
					}, 4000);
				} else if (authResult['error']) {
					console.log('There was an error: ' + authResult['error']);
				}
			}
		});
	}
	else {
		$('.flash').html('<strong>Failed to make a server-side call.  Check your configuration and console.</strong>');
	}
}


// Run after DOM tree loads
$(function() {

///////////////     RESPONSIVE FONTAWESOME ICONS    //////////////////////////////////////////////

	var w = $(window);
	var d = $(document);
	var icon = $("#github_icon");
	var sports = $('[id ^= "Sports_nav_item"]').children('i');
	var weather = $('[id ^= "Weather_nav_item"]').children('i');
	var economy = $('[id ^= "Economy_nav_item"]').children('i');
	var politics = $('[id ^= "Politics_nav_item"]').children('i');
	var food = $('[id ^= "Food_nav_item"]').children('i');
	var art = $('[id ^= "Art_nav_item"]').children('i');

	d.ready(function() {
		if (w.width() <= 475) {
			icon.removeClass('fa-lg');
			sports.addClass("fa fa-trophy fa-lg");
			weather.addClass("fa fa-umbrella fa-lg");
			economy.addClass("fa fa-balance-scale fa-lg");
			politics.addClass("fa fa-globe fa-lg");
			food.addClass("fa fa-cutlery fa-lg");
			art.addClass("fa fa-heart fa-lg");
		}
	})

	w.resize(function() {
		if (w.width() <= 475) {
			icon.removeClass('fa-lg');
			sports.addClass("fa fa-trophy fa-lg");
			weather.addClass("fa fa-umbrella fa-lg");
			economy.addClass("fa fa-balance-scale fa-lg");
			politics.addClass("fa fa-globe fa-lg");
			food.addClass("fa fa-cutlery fa-lg");
			art.addClass("fa fa-heart fa-lg");
		}
		if (w.width() > 475) {
			icon.addClass('fa-lg');
			sports.removeClass("fa fa-trophy fa-lg");
			weather.removeClass("fa fa-umbrella fa-lg");
			economy.removeClass("fa fa-balance-scale fa-lg");
			politics.removeClass("fa fa-globe fa-lg");
			food.removeClass("fa fa-cutlery fa-lg");
			art.removeClass("fa fa-heart fa-lg");
		}
	})

///////////////     PROFILE PIC DROPDOWN MENU    //////////////////////////////////////////////

	$(".profile_pic").on("click", function() {
		$(".dropdown_menu").toggleClass('show_dropdown');
	});

///////////////     DATE TIMEZONE/FORMATTING    //////////////////////////////////////////////

	var reformatDate = function(input_date) {
		var article_date = input_date;
		var datestring = article_date.attr("datetime");
		datestring = datestring.slice(0, 19);
		datestring = datestring.replace(" ", "T");
		article_date.attr("datetime", datestring);
		var d = new Date(datestring);
		d = d.toString();
		d = d.slice(4, 10) + "," + d.slice(10,15) + " (" + d.slice(16,21) + "\xa0" + d.slice(35);
		article_date.text(d);
	}

	var i = 1;
	var count = $('.article_date').length;
	if (count > 0) {
		while (i <= count) {
			var iterated_date = $("#article_date_" + i);
			reformatDate(iterated_date);
			i++;
		}
	}

	var full_article_date = $(".full_article_date");
	if (full_article_date.length > 0) {
		reformatDate(full_article_date);
	}

});