
  
  /* Adicionar Conta */
  document.addEventListener("DOMContentLoaded", function() {
    var addButton = document.getElementById("adicionar-conta");
    var formContainer = document.getElementById("form-container");
  
    addButton.addEventListener("click", function() {
      formContainer.style.display = formContainer.style.display === "block" ? "none" : "block";
    });
  });
  
  
  /* Restante dos scripts */
  document.addEventListener("DOMContentLoaded", function() {
    var searchInput = document.getElementById("search-input");
  
    searchInput.addEventListener("keydown", function(event) {
      if (event.key === "Enter") {
        event.preventDefault();
        performSearch(searchInput.value);
      }
    });
  
    function performSearch(query) {
      console.log("Pesquisar:", query);
    }
  });
  
  document.addEventListener("DOMContentLoaded", function() {
    var dropdownButtons = document.querySelectorAll(".dropdown-btn, .btn-table");
  
    dropdownButtons.forEach(function(button) {
      var dropdownContent = button.nextElementSibling;
  
      button.addEventListener("click", function() {
        dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
      });
    });
  });
  
  (function($) {
    "use strict";
  
    var input = $(".validate-input .input100");
  
    $(".validate-form").on("submit", function() {
      var check = true;
  
      for (var i = 0; i < input.length; i++) {
        if (validate(input[i]) == false) {
          showValidate(input[i]);
          check = false;
        }
      }
  
      return check;
    });
  
    $(".validate-form .input100").each(function() {
      $(this).focus(function() {
        hideValidate(this);
      });
    });
  
    function validate(input) {
      if ($(input).attr("type") == "email" || $(input).attr("name") == "email") {
        if (
          $(input)
            .val()
            .trim()
            .match(
              /^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/
            ) == null
        ) {
          return false;
        }
      } else {
        if (
          $(input)
            .val()
            .trim() == ""
        ) {
          return false;
        }
      }
    }
  
    function showValidate(input) {
      var thisAlert = $(input).parent();
  
      $(thisAlert).addClass("alert-validate");
    }
  
    function hideValidate(input) {
      var thisAlert = $(input).parent();
  
      $(thisAlert).removeClass("alert-validate");
    }
  })(jQuery);
  
  var messages = document.querySelectorAll(".message");
  
  var timeout = 5000;
  
  messages.forEach(function(message) {
    setTimeout(function() {
      message.style.display = "none";
    }, timeout);
  });
  
  $(document).ready(function() {
    $(".pedido").click(function() {
      $(".pedido").removeClass("selected");
      $(this).addClass("selected");
      $(".btn-preparo, .btn-finalizado").hide();
      if ($(this).hasClass("em-preparo")) {
        $(this)
          .find(".btn-finalizado")
          .show();
      } else {
        $(this)
          .find(".btn-preparo, .btn-finalizado")
          .show();
      }
    });
  
    $(".btn-preparo").click(function(event) {
      event.stopPropagation();
      var pedidoId = $(this).data("pedido-id");
      $(this)
        .closest(".pedido")
        .addClass("em-preparo");
      $(this).hide();
      $(this)
        .siblings(".btn-finalizado")
        .show();
    });
  
    $(".btn-finalizado").click(function(event) {
      event.stopPropagation();
      $(this)
        .closest(".pedido")
        .removeClass("em-preparo");
      $(this).hide();
    });
  });
  