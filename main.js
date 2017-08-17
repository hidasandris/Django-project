$(document).ready(function (){

  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });

  $("#id_date").datepicker({
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd"
  });

  $("#main-form").submit(function (event) {
      var serializedData = $("#main-form").serializeArray();
      serializedData.push({name: "multiplier", value: multiplier()});
      bootbox.confirm({
          title: "Ellenőrizted az adatokat?",
          message: "Biztos vagy benne, hogy elküldöd az adatbázisba?",
          buttons: {
              cancel: {
                  label: 'Mégse',
                  className: 'btn-danger'
              },
              confirm: {
                  label: 'Megerősít',
                  className: 'btn-success'
              }
          },
          callback: function (result) {
              console.log('This was logged in the callback: ' + result);
              if (result) {
                  $.ajax({
                      url : window.location.href, // the endpoint
                      type : "POST",
                      data : serializedData, // data sent with the post request

                      success: function(json) {
                          console.log(json);
                          bootbox.confirm({
                              title: "Folytatás",
                              message: "Folytatod az adatbevitelt?",
                              buttons: {
                                  cancel: {
                                      label: '<i class="fa fa-times"></i> Elég volt mára'
                                  },
                                  confirm: {
                                      label: '<i class="fa fa-check"></i> Új minta'
                                  }
                              },
                              callback: function (result) {
                                  if (result) {
                                      location.reload()
                                      // $("form")[0].reset()
                                  }
                                  else {
                                      window.location.replace("http://algaduna.okologia.mta.hu")
                                  }
                              }
                          })
                      },
                      error: function (xhr) {
                          bootbox.alert({
                              message: "Hibás adatbevitel!",
                              size: 'small',
                              backdrop: true
                          });
                          console.log(xhr.status + ": " + xhr.responseText);
                      }
                  })
              }
          }
      });
      event.preventDefault();
  });

  function multiplier() {
      var n = $("#multiuplier, #id_n").val(),
          d = $("#multiuplier, #id_d").val(),
          a = $("#multiuplier, #id_a").val(),
          V = $("#multiuplier, #id_V").val();
      return d*d/4 * 3.14 / (2*n * d/2 * a/1000 * V);
  }

  // final check
  $("#check").click(function () {
      var sum = 0;
      $(".count").each(function () {
          sum += Number($(this).val());
      });
      $("#sum").text("Az egyedszám és sejtszám összege: " + sum);
  });

  // multiplier check
  $("#multiplier-form").find(":input").change(function () {
      if ($.isNumeric(multiplier()))
          $("#multiplier").text("Szorzó: " + multiplier().toFixed(2));
  });
  
  // new taxon
  $("#taxon-form").submit(function (event) {
      event.preventDefault();
      var taxon_serialized = $("#taxon-form").serialize();
      $.ajax({
          url: window.location.href,
          type: "POST",
          data: taxon_serialized,

          success: function (json) {
              console.log(json);
              $(".modal-loader").css("display", "block");
              $("#formset").find("select").append($("<option></option>").attr("value", json.taxon_id)
                  .text(json.taxon_name));
              var my_options = $("#formset").find("select:first option");
              var selected = $('form select option:selected').map(function (){
                  return this.value
              }).get();
              my_options.sort(function(a,b) {
                  if (a.text > b.text) return 1;
                  if (a.text < b.text) return -1;
                  return 0
              });
              $("#formset").find("select").empty().append(my_options);
              $("#formset").find("select").each(function (index){
                  $(this).val(selected[index])
              });
              $("#myModalHorizontal").modal('hide');
              $(".modal-loader").css("display", "none");
              $("#myModalHorizontal").find('form')[0].reset();
          },
          error: function (xhr) {
              bootbox.alert({
                  message: "Hibás adatbevitel!",
                  size: 'small',
                  backdrop: true
              });
              console.log(xhr.status + ": " + xhr.responseText);
          }
      })
  });


  // scrolling
  (function($) {
      $.fn.fixMe = function() {
          return this.each(function() {
              var $this = $(this),
                  $t_fixed;

              function init() {
                  $this.wrap('<div class="container" />');
                  $t_fixed = $this.clone();
                  $t_fixed.find("tbody").remove().end().addClass("fixed").attr('id', 'scroll-header')
                      .insertBefore($this);
                  resizeFixed();
              }

              function resizeFixed() {
                  $t_fixed.find("th").each(function(index) {
                      $(this).css("width", $this.find("th").eq(index).outerWidth() + "px");
                  });
              }

              function scrollFixed() {
                  var offset = $(this).scrollTop(),
                      tableOffsetTop = $this.offset().top,
                      tableOffsetBottom = tableOffsetTop + $this.height() - $this.find("thead").height();
                  if (offset < tableOffsetTop || offset > tableOffsetBottom)
                      $t_fixed.hide();
                  else if (offset >= tableOffsetTop && offset <= tableOffsetBottom && $t_fixed.is(":hidden"))
                      $t_fixed.show();
              }
              $(window).resize(resizeFixed);
              $(window).scroll(scrollFixed);
              init();
          });
      };
  })(jQuery);

  $("table").fixMe();


  // add new form row
  function cloneMore(selector, type) {
      var newElement = $(selector).clone(true);
      var total = $('#id_' + type + '-TOTAL_FORMS').val();
      newElement.find(':input').each(function() {
          var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
          var id = 'id_' + name;
          $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
      });
      newElement.find('label').each(function() {
          var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
          $(this).attr('for', newFor);
      });
      total++;
      $('#id_' + type + '-TOTAL_FORMS').val(total);
      $(selector).after(newElement);
  }

  $('#add_more').click(function(event) {
      event.preventDefault();
      var selector = '#formset>tbody>tr:last-child';
      cloneMore(selector, 'samtax_set');
      $("html, body").animate({
          scrollTop: $(selector).offset().top + $(selector).outerHeight(true)
      }, 500);
  });


  $(window).scroll(function () {
      if ($(this).scrollTop() > 50) {
          $('#back-to-top').fadeIn();
      } else {
          $('#back-to-top').fadeOut();
      }
  });
  // scroll body to 0px on click
  $('#back-to-top').click(function () {
      $('#back-to-top').tooltip('hide');
      $('body,html').animate({
          scrollTop: 0
      }, 800);
      return false;
  });

  $('#back-to-top').tooltip('show');

});
