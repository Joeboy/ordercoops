var AJAX_ERROR_TEXT = "Sorry, there was an error getting your basket information from the server. Please try again, and if it still doesn't work leave it a while and hopefully the problem will get fixed.";
var username;
var order_id;

function update_basket_display() {
    if (!username) {
        $('#basket-contents').html('<p>No basket - not logged in.</p>');
        return;
    }

    $.getJSON("/order-"+order_id+"/basket-contents-json/", function(data, textStatus) {
        if (textStatus=='success') {
            if (data['items'].length ==0) {
                basketText="<p>Nowt, zilch, nada</p>";
            } else {
                basketText='';
                for (i=0;i<data['items'].length;i++) {
                    basketText+='<p><a href="./?code='+data['items'][i].code+'">'+data['items'][i].description + ' ' + data['items'][i].size+'</a> x'+data['items'][i].quantity+'</p>';
                }
            }
            $('#basket-contents').html(basketText);
            $('#id_total_basket_price').html(data['total_basket_price']);

            $('input.quantityinput').each( function() {
                var product_id=this.id.substring(20);
                iteminfo = hack_from_array(product_id, data['items']);
                if (iteminfo) {
                    $(this).attr('value',iteminfo['quantity']);
                    $('#rem_product_'+product_id).html('Remove');
                    $('#id_product_total_price_'+product_id).html('&pound;'+iteminfo['total']);
                } else {
                    this.value='0';
                    $('#rem_product_'+product_id).empty();
                    $('#id_product_total_price_'+product_id).empty();
                }
            } );
        } else {
            alert(AJAX_ERROR_TEXT);
        }
    } );
}
function hack_from_array(id, thearray) {
    for (j=0;j<thearray.length;j++) {
        if (thearray[j]['id'] == id) {
            return thearray[j];
        }
    }
    return null;
}

function amend_basket_quantity_ajax(user_id, product_id, increment, new_value){
    // if increment is a positive or negative number, we'll add it to
    // the quantity and ignore new_value. If it's 0, we'll use new_value instead.
    if (username == '') {
        return;
    }
    var url='/order-'+order_id+'/amend-basket-quantity/'+product_id+'/'+increment+'/'+new_value+'/';
    $.getJSON(url, function(data, textStatus) {
        if (textStatus=='success') {
            update_basket_display();
        } else {
            alert(AJAX_ERROR_TEXT);
        }
    });
}

function submit_productCategory_form() {
    $('#id_productCategory_form').submit();
}

function submit_brand_form() {
    $('#id_brand_form').submit();
}

function on_submit() {
    code_searchbox=$('#id_code_searchbox');
    if (code_searchbox.attr('value').length && !code_searchbox.attr('value').match(/^[a-z][a-z][0-9]{0,3}$/i)) {
        alert('Sorry, you put a dodgy product code in the box');
        return false;
    }
}

function add_to_basket() {
    var product_id=this.id.substring(12);
    amend_basket_quantity_ajax(username, product_id, +1, 0);
    return false;
}

function remove_from_basket() {
    var product_id=this.id.substring(12);
    amend_basket_quantity_ajax(username, product_id, -1, 0);
    return false;
}

var timed_event = null;
function change_product_quantity() {   
    var product_id = this.id.substring(20);
    new_quantity = this.value;
    if (!new_quantity.match(/^\d+$/)) {
        return;
    }
    if (timed_event) {
        clearTimeout(timed_event);
    }
    timed_event = setTimeout("amend_basket_quantity_ajax('"+username+"', "+product_id+",0, "+new_quantity+")", 700);
}

$(document).ready( function() {
    username = $('#id_username').val();
    order_id = $('#id_order_id').val();

    if ($('#id_productCategory_selector').length) {
        // We're browsing the catalogue
        $('#id_productCategory_selector').change(submit_productCategory_form);
        $('#id_brand_selector').change(submit_brand_form);
        $('#id_code_form').submit(on_submit);
    } else {
        // we're browsing the basket contents
    }

    if (username) {
        $('a.add_to_basket_link').click(add_to_basket);
        $('a.remove_from_basket_link').click(remove_from_basket);
    } else {
        $('a.add_to_basket_link').remove();
        $('a.remove_from_basket_link').remove();
    }

    $('input.quantityinput').keyup(change_product_quantity);

    update_basket_display();
} );
