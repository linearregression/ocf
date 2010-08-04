/**
 * @author: Jad Naous
 * 
 * Functions to add tooltips to things.
 */

/**
 * Add a tooltip to all (val, description) div class pairs that also
 * have the class listClass.
 * 
 * To use, include the tooltip.css, and add html like:
 *     
 *     ...
 *     <div class="list val">value1</div>
 *     <div class="list description">Description for value1</div>,
 *     <div class="list val">value2</div>
 *     <div class="list description">Description for value2</div>,
 *     ...
 *     
 * then call the function as addToolTip("list")
 *     
 * @param {String} listClass
 */
function addTooltipToClass(listClass){
	$("div." + listClass).css("display", "inline");
	
	$("div.description." + listClass).hide().addClass(function(index){
		return "description_" + index;
	}).addClass("tooltip");
	
	$("div.val." + listClass).each(function(index){
		$(this).wrap("<a class='noeffect' href='#' />").tooltip({
			effect: "fade",
			tip: "div." + listClass + ".description_" + index
		});
	});
	
	$("a.noeffect").click(function(event){
		event.preventDefault();
	});
}

/**
 * Put tooltips for some summary text.
 * To use, include the tooltip.css, and add html like:
 *     
 *     ...
 *     <div class="summarytext summary">list summary...</div>
 *     <div class="summarytooltip summary">
 *         <div class="summary val">value1</div>
 *         <div class="summary description">Description for value1</div> | 
 *         <div class="summary val">value2</div>
 *         <div class="summary description">Description for value2</div> | 
 *         ...
 *     </div>
 *     ...
 *     
 * then call the function as addToolTipToSummary("summary")
 *     
 * @param {String} summaryClass
 */
function addTooltipToSummary(summaryClass){
	$("div." + summaryClass).css("display", "inline");
	
	/* hide the description div and give it a class according to index */
	$("div.description." + summaryClass).hide().addClass(function(index){
		return "summarydescription_" + index;
	});
	
	/* add a div where the description will be displayed in the tooltip */
	$("div.summarytooltip." + summaryClass)
		.append("<div class='tooltip_desc " + summaryClass + "' />")
		.addClass("tooltip")
		.hide()
	;
	
	/* 
	 * whenever the mouse goes over a val, change the description in
	 * the tooltip
	 */
	$("div.val." + summaryClass).each(function(index){
		$(this).mouseenter(function(){
			$("div.tooltip_desc." + summaryClass)
				.html($("div." + summaryClass +
					".summarydescription_" + index).html());
		}).wrap("<a class='noeffect' href='#' />");
	});
	
	/* Add tooltip */
	$("div.summarytext." + summaryClass).each(function(index){
		$(this).wrap("<a class='noeffect' href='#' />");
		$(this).closest("a").tooltip({
			effect: "fade",
			tip: "div.summarytooltip." + summaryClass
		});
	});
	
	/* no events for tooltip anchors */
	$("a.noeffect").click(function(event){
		event.preventDefault();
	});
}
