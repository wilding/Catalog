///////////////     GOOGLE SIGN IN    //////////////////////////////////////////////

var state = $("#g_signin_script").attr('data-state');
var route = $("#g_signin_script").attr('data-route');
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