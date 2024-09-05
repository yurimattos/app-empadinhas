//adicionar classes no form (prevent-double-click-form)
//adicionar botao com classe e onclick:
//<button class="btn btn-primary prevent-double-click-button" type="submit" onclick="javascript:submitForm();">Salvar</button>

function submitForm() {

    const form = $('.prevent-double-click-form');

    if (form[0].checkValidity()) {
        $('.prevent-double-click-button').prop("disabled", true);
        $('#overlay').fadeIn();
        form.submit();
    } else {
        //alert('invalido');
    }
  }