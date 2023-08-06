(function($) {

	"use strict";

	const base_href = $("#base_href").val() ;

	/**
	 * The `fullHeight` function sets the height of elements with the class `js-fullheight` to match the
	 * height of the element with the id `base`, and updates the height whenever the window is resized.
	 */
	const fullHeight = function(){
		$('.js-fullheight').css('height', $("#base").outerHeight()) ;

		$(window).resize(function(){
			$('.js-fullheight').css('height', $("#base").outerHeight()) ;
		}) ;
	} ;
	fullHeight() ;


	/**
	 * The code is adding a click event listener to the element with the id `sidebarCollapse`. When this element is 
	 * clicked, it toggles the class `active` on the element with the id `sidebar`. This is typically used 
	 * to show or hide a sidebar menu when a button or icon is clicked.
	 */
	$('#sidebarCollapse').on('click', function (){
    	$('#sidebar').toggleClass('active') ;
  	}) ;


	/**
	 * The function `get_archive_models` sends a POST request to the "/get-archive-models" endpoint with a
	 * formatted date as the payload, and if the request is successful, it redirects the user to the value
	 * returned in the response.
	 * 
	 * @param v The parameter `v` is a Date object representing a specific date.
	 */
	const get_archive_models = (v) => { 

		const formatted_date = v.getFullYear().toString() + ( '0' + (v.getMonth()+1) ).slice( -2 ).toString() + ( '0' + v.getDate() ).slice( -2 ).toString() ;

		$.ajax({
			url: (base_href == "/") ? "/get-archive-models/" : base_href + "/get-archive-models/",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({ "formatted_date": formatted_date }),
			success: function(r) {
				if(r.success){
					window.location.href = r.value ;
				}	
			},
			error: function(error){
				console.log(error) ;
			}
		}) ;	
    }


	/**
	 * The code is adding an event listener to the `window` object for the "load" event. When the window finishes 
	 * loading all its content, the function inside the event listener is executed. In this case, the 
	 * function is hiding the element with the id `loader-container` by calling the `hide()` method on it.
	 * This is typically used to hide a loading spinner or display a page content after it has finished loading. 
	*/
	window.addEventListener("load", function (){
		$("#loader-container").hide() ;
	}) ;


	/**
	 * The code is initializing the lightGallery plugin on the element with the id "gallery-container". 
	 * The plugin is being configured with various options: 
	 */
	lightGallery(document.getElementById("gallery-container"), {
		speed: 400,
		thumbnail: true,
		fullScreen: true,
		animateThumb: false,
		zoomFromOrigin: false,
		toggleThumb: true,
		slideShowInterval:100,
		speed:0,
		plugins: [lgZoom, lgThumbnail, lgFullscreen, lgAutoplay],
	}) ;


	/** 
	 * The code is making an AJAX POST request to the "get-availables-date" endpoint with the `async`
	 * option set to `false`, which means the request will be synchronous. The response from the request
	 * is stored in the `data` variable. 
	 */
	const data = $.ajax({
		type: "POST",
		url : (base_href == "/") ? "/get-availables-date/" : base_href + "/get-availables-date/",
		async:false
	}).responseText ;

	const dirlist = JSON.parse(data).dirlist ;

	const options = $.extend({
		onSelect: function(){ 
			get_archive_models( $(this).datepicker( 'getDate') ) ; 
			}
		},

		$.datepicker.regional["it"],{
			changeMonth: true,
			changeYear: true,	
			beforeShowDay: function(date){

				var string = jQuery.datepicker.formatDate('yymmdd', date) ;

				if(dirlist.indexOf(string) == -1){
					return [false, ""] ;
				} else{
					return [true, ""] ;
				}
			}	
	}) ;
	$("#datepicker").datepicker(options) ;  

	const pathname = window.location.pathname.replaceAll("/", " ").trim().split(" ")[0] ;
	const selected_day = new Date(pathname.slice(0,4), (pathname.slice(4,6)-1), pathname.slice(6,8)) ;
	$("#datepicker").datepicker("setDate", selected_day) ;


	/**
	 * The function `models_run_checkbox` toggles the visibility of a div element based on the value of a
	 * checkbox.
	 * 
	 * @param e The parameter "e" is the event object that is passed to the event handler function. It
	 * represents the event that triggered the function, in this case, a click event on a form check label
	 * with the class "run".
	 */
	const models_run_checkbox = (e) =>{
		const target = e.attr("for") ;
		$("div").find("[data-id=" + target + "]").toggle() ;
	} ;

	$('.form-check-label.run').on('click', function (){
    	models_run_checkbox( $(this)) ;
  	}) ;

})(jQuery) ;
