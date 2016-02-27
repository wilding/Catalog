///////////////     DATE TIMEZONE/FORMATTING    //////////////////////////////////////////////

$(function() {
	var article_date = $(".article_date");
	var datestring = article_date.attr("datetime");
	datestring = datestring.slice(0, 19);
	datestring = datestring.replace(" ", "T");
	article_date.attr("datetime", datestring);
	var d = new Date(datestring);
	d = d.toString();
	d = d.slice(4, 10) + "," + d.slice(10,15) + " (" + d.slice(16,21) + "\xa0" + d.slice(35);
	article_date.text(d);
});