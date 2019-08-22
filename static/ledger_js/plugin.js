
$(document).ready(function () {
  var ShowForm = function () {
    var btn = $(this)
    $.ajax({
      url: btn.attr('data-url'),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        jQuery.noConflict()
        $('#modal-book').modal('show')
        $('#modal-book .modal-content').html('<div style="padding-top:3px; padding-bottom:3px"><div class="text-center">Please wait...</div><div class="sk-spinner sk-spinner-three-bounce"><div class="sk-bounce1"></div><div class="sk-bounce2"></div><div class="sk-bounce3"></div></div></div>')
      },
      success: function (data) {
        $('#modal-book .modal-content').html(data.html_form)
        if (data.is_error) {
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
      beforeSend: function () {
        jQuery.noConflict()
        $('#modal_div_alert').html('<div style="padding-top:3px; padding-bottom:3px;"><div class="text-center">Please wait...</div><div class="sk-spinner sk-spinner-three-bounce"><div class="sk-bounce1"></div><div class="sk-bounce2"></div><div class="sk-bounce3"></div></div></div>')
        $('#modal_div_alert').show()
      },
      error: function (xhr, error) {
        $('#modal_div_alert').html('<b>Request Status: </b>' + xhr.status + '<br /><b>Status Text: </b>' + xhr.statusText + '<br /><b>Response: </b>' + (xhr.responseText || "").substring(0, 256) + "...")
        $('#modal_div_alert').show()
      },
      success: function (data) {
        jQuery.noConflict()
        if (data.is_error) {
          $('#modal-book-date .modal-content').html(data.html_form)
          $('#modal_div_alert').html(data.error_message)
          $('#modal_div_alert').show()
        }
        else {
          $('#book-table tbody').html(data.ledger_list)
          $('#modal_div_alert').hide()
          $('#modal-book').modal('hide')
        }
      }
    })
    return false
  }

  // delete
  $('#book-table').on('click', '.show-form-delete', ShowForm)
  $('#modal-book').on('submit', '.delete-form', SaveForm)
})
