tinyMCE.init({
	width:622,
	height: 400,
	mode : "textareas",
	theme : "advanced",
	relative_urls : false,
	convert_urls : false,
	inline_styles : true,
	convert_fonts_to_spans : true,
	content_css : "/media/default.css",
	editor_selector : "vSmartPageTextField",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "cut,copy,paste,pasteword,separator,undo,redo,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor,separator,djangoimage,image,separator,cleanup,separator,code,previewonsite",
	theme_advanced_buttons2 : "formatselect,fontselect,fontsizeselect,bold,italic,underline,strikethrough,separator,forecolor,backcolor,removeformat",
	theme_advanced_buttons3 : "search,replace,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,charmap,djangohelp",
	auto_cleanup_word : true,
	plugins : "table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,zoom,flash,searchreplace,print,contextmenu,fullscreen,djangoimage,paste,previewonsite,djangohelp",
	plugin_insertdate_dateFormat : "%m/%d/%Y",
	plugin_insertdate_timeFormat : "%H:%M:%S",
	extended_valid_elements : "a[name|href|target|title|onclick],img[style|class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style],form[action|method],input[type|name|value|src|alt]",
	fullscreen_settings : {
		theme_advanced_path_location : "top",
		theme_advanced_buttons1 : "fullscreen,separator,preview,separator,cut,copy,paste,separator,undo,redo,separator,search,replace,separator,code,separator,cleanup,separator,bold,italic,underline,strikethrough,separator,forecolor,backcolor,separator,justifyleft,justifycenter,justifyright,justifyfull,separator,help",
		theme_advanced_buttons2 : "removeformat,styleselect,formatselect,fontselect,fontsizeselect,separator,bullist,numlist,outdent,indent,separator,link,unlink,anchor",
		theme_advanced_buttons3 : "sub,sup,separator,image,insertdate,inserttime,separator,tablecontrols,separator,hr,advhr,visualaid,separator,charmap,emotions,iespell,flash,separator,print"
	}
});

