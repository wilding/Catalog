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

///////////////     GO TO ARTICLE    //////////////////////////////////////////////

// Given a category id and an article id, load the page for the full article
var loadArticle = function(category_id, article_id) {
	var url = 'http://localhost:8080/category/' + category_id + '/article/' + article_id;
	return window.location.assign(url);
}

///////////////     SHOW/HIDE COMMENT EDIT/DELETE FORMS    //////////////////////////////////////////////

// Show edit comment form
var showCommentEditForm = function(index) {
	var new_height = $('#comment_' + index).height();
	$('#edit_comment_' + index).css('height', new_height);
	$('.edit_comment').css('display', 'none');
	$('.comment').css('display', 'flex');
	$('#comment_' + index).css('display', 'none');
	$('#edit_comment_' + index).css('display', 'flex');
}
// Show delete comment form
var showCommentDeleteForm = function(index) {
	var new_height = $('#comment_' + index).height();
	$('#delete_comment_' + index).css('height', new_height);
	$('.edit_comment').css('display', 'none');
	$('.comment').css('display', 'flex');
	$('#comment_' + index).css('display', 'none');
	$('#delete_comment_' + index).css('display', 'flex');
}
// Hide edit comment form
var hideCommentEditForm = function(index) {
	$('#comment_' + index).css('display', 'flex');
	$('#edit_comment_' + index).css('display', 'none');
}
// Hide delete comment form
var hideCommentDeleteForm = function(index) {
	$('#comment_' + index).css('display', 'flex');
	$('#delete_comment_' + index).css('display', 'none');
}

///////////////     CLEAR NEW COMMENT TEXT AREA    //////////////////////////////////////////////

var clearTextArea = function () {
	$('#new_comment_textarea').val('');
}

/////////////////////////////////////////////////////////////////////////////////////////////
///////////////    RUN AFTER DOM TREE LOADS    //////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
$(function() {

///////////////     RESPONSIVE ELEMENTS    //////////////////////////////////////////////

	// Jquery assignments
	var w = $(window);
	var d = $(document);
	var signin = $('.g-signin');
	var github = $("#github_icon");
	var atom = $("#feed_icon");
	var sports = $('[id ^= "Sports_nav_item"]').children('i');
	var weather = $('[id ^= "Weather_nav_item"]').children('i');
	var economy = $('[id ^= "Economy_nav_item"]').children('i');
	var politics = $('[id ^= "Politics_nav_item"]').children('i');
	var food = $('[id ^= "Food_nav_item"]').children('i');
	var art = $('[id ^= "Art_nav_item"]').children('i');
	// Load page on mobile widths
	d.ready(function() {
		if (w.width() <= 475) {
			github.removeClass('fa-lg');
			atom.removeClass('fa-lg');
			sports.addClass("fa fa-trophy fa-lg");
			weather.addClass("fa fa-umbrella fa-lg");
			economy.addClass("fa fa-balance-scale fa-lg");
			politics.addClass("fa fa-globe fa-lg");
			food.addClass("fa fa-cutlery fa-lg");
			art.addClass("fa fa-heart fa-lg");
			signin.attr('data-height', 'short');
		}
	})
	w.resize(function() {
		// Resize window below mobile widths
		if (w.width() <= 475) {
			github.removeClass('fa-lg');
			atom.removeClass('fa-lg');
			sports.addClass("fa fa-trophy fa-lg");
			weather.addClass("fa fa-umbrella fa-lg");
			economy.addClass("fa fa-balance-scale fa-lg");
			politics.addClass("fa fa-globe fa-lg");
			food.addClass("fa fa-cutlery fa-lg");
			art.addClass("fa fa-heart fa-lg");
		}
		// Resize window above mobile widths
		if (w.width() > 475) {
			github.addClass('fa-lg');
			atom.addClass('fa-lg');
			sports.removeClass("fa fa-trophy fa-lg");
			weather.removeClass("fa fa-umbrella fa-lg");
			economy.removeClass("fa fa-balance-scale fa-lg");
			politics.removeClass("fa fa-globe fa-lg");
			food.removeClass("fa fa-cutlery fa-lg");
			art.removeClass("fa fa-heart fa-lg");
		}
		// Resize comment forms
		if (w.width() <= 1070 && w.width() > 475) {
			for (n in $('.edit_comment')) {
				var edit_form = $('#edit_comment_' + n);
				if (edit_form.height() < 97 && edit_form.height() > 0) {
					edit_form.css('height', 97);
				}
				var delete_form = $('#delete_comment_' + n);
				if (delete_form.height() < 97 && delete_form.height() > 0) {
					delete_form.css('height', 97);
				}
			}
		}
	})

///////////////     DATE TIMEZONE/FORMATTING    //////////////////////////////////////////////

	// Reformat date string, convert it to javascript date object, add it to <time> tag
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
	// Article cards
	var i = 1;
	var count = $('.article_date').length;
	if (count > 0) {
		while (i <= count) {
			var iterated_date = $("#article_date_" + i);
			reformatDate(iterated_date);
			i++;
		}
	}
	// Full articles
	var full_article_date = $(".full_article_date");
	if (full_article_date.length > 0) {
		reformatDate(full_article_date);
	}
	// Last edited
	var last_edited = $(".full_article_last_edited");
	if (last_edited.length > 0) {
		reformatDate(last_edited);
	}
	// Comment date
	var comment_date = $(".comment_date");
	var i = 1;
	var count = comment_date.length;
	if (count > 0) {
		while (i <= count) {
			var iterated_date = $("#comment_date_" + i);
			reformatDate(iterated_date);
			i++;
		}
	}
	// Comment last edited
	var comment_last_edited = $(".comment_last_edited");
	var i = 1;
	var count = comment_last_edited.length;
	if (count > 0) {
		while (i <= count) {
			var iterated_date = $("#comment_last_edited_" + i);
			reformatDate(iterated_date);
			i++;
		}
	}

///////////////     COMMENTS    //////////////////////////////////////////////

	// Toggle hiding comment section
	var carrot = $('#comment_indicator');
	var comment_content = $('.comment_content');
	var comment_header = $('.comment_header');
	var toggleComments = function() {
		comment_content.toggleClass('comments_active');
		carrot.toggleClass('fa-angle-down');
	}
	comment_header.click(toggleComments);
	// Alternating light/dark comment background colors
	var comments = $('.comment');
	for (comment in comments) {
		if (comment % 2 ==0) {
			$('#comment_' + comment).css('background-color', 'rgba(125, 110, 79, 0.3)');
		}
	}
	// Alternating light/dark edit form background colors
	var edit_forms = $('.edit_comment');
	for (form in edit_forms) {
		if (form % 2 ==0) {
			$('#edit_comment_' + form).css('background-color', 'rgba(125, 110, 79, 0.3)');
			$('#delete_comment_' + form).css('background-color', 'rgba(125, 110, 79, 0.3)');
		}
	}
	// Reveal comment edit/delete buttons when the owner hovers over the comment
	var revealCommentOptions = function() {
		var author = $(this).parent('.comment').attr('data-author');
		var user = $(this).parent('.comment').attr('data-user');
		if (author === user) {
			$(this).children('#comment_crud').css('opacity', '1');
			$(this).children('#comment_crud').css('transform', 'translate3d(0,0,0)');
		}
	}
	// Hide comment edit/delete buttons when the mouse leaves the comment area on larger devices
	var hideCommentOptions = function () {
		if (w.width() > 768) {
			$(this).children('#comment_crud').css('opacity', '0');
			$(this).children('#comment_crud').css('transform', 'translate3d(0,15px,0)');
		}
	}
	$(".comment_metadata").hover(revealCommentOptions, hideCommentOptions);
	// Hide edit/delete buttons for everyone but the owner
	for (comment in comments) {
		var current_comment = $('#comment_' + comment);
		if (current_comment.attr('data-author') !== current_comment.attr('data-user')) {
			console.log(current_comment.attr('id'));
			var crud = current_comment.children().children('#comment_crud');
			crud.css('opacity', '0');
			crud.css('transform', 'translate3d(0,15px,0)');
		}
	}

///////////////     HIDE FOOTER BUTTONS    //////////////////////////////////////////////

	// Hide edit/delete buttons in category menu and full article page if not the creator
	var user_info = $('.user_information');
	var user = user_info.attr('data-user');
	var creator = user_info.attr('data-creator');
	if (user !== creator) {
		$('.footer_button').css('display', 'none');
	}
	// Hide new category button if not the site owner
	if (user !== '1') {
		$('.mainmenu_footer_button').css('display', 'none');
	}
});