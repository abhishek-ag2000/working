/*
Date Range Selection Modal Event Handling
*/
$(document).ready(function () {
  var ShowForm = function () {
    var btn = $(this)
    $.ajax({
      url: btn.attr('data-url'),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        jQuery.noConflict()
        $('#modal-book-date').modal('show')
      },
      success: function (data) {
        $('#modal-book-date .modal-content').html(data.html_form)
        if(data.is_error){
          $('modal_div_alert').html(data.error_message)
          $('modal_div_alert').show()
        }
      }
    })
  }

  var SaveForm = function () {
    var form = $(this)
    $.ajax({
      url: form.attr('data-url'),
      data: form.serialize(),
      type: form.attr('method'),
      dataType: 'json',
      error: function(xhr, error){
        $('#modal_div_alert').html('<b>Request Status: </b>' + xhr.status + '<br /><b>Status Text: </b>' + xhr.statusText + '<br /><b>Response: </b>' + xhr.responseText)
        $('#modal_div_alert').show()
      },
      success: function (data) {
        jQuery.noConflict()
        if(data.is_error){
          $('#modal-book-date .modal-content').html(data.html_form)
          $('#modal_div_alert').html(data.error_message)
          $('#modal_div_alert').show()
        }
        else{
          $('#modal-book-date').modal('hide')
          
          window.location.reload();
        }
      }
    })
    return false
  }

  // create
  // $('.show-form').click(ShowForm)
  // $('#modal-book-date').on('submit', '.create-form', SaveForm)

  // update
  $('.show-form-update').click(ShowForm)
  $('#modal-book-date').on('submit', '.update-form', SaveForm)
})
