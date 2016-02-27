///////////////     RESPONSIVE GITHUB SOURCE    //////////////////////////////////////////////

$(function() {
	var w = $(window);
	var d = $(document);
	var icon = $("#github_icon");

	d.ready(function() {
		if (w.width() <= 475) {
			icon.removeClass('fa-lg');
		}
	})

	w.resize(function() {
		if (w.width() <= 475) {
			icon.removeClass('fa-lg');
		}
		if (w.width() > 475) {
			icon.addClass('fa-lg');
		}
	})
});



