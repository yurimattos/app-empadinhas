$(document).ready(function() {
    $('.phone-mask').mask('(00) 00000-0000');
    $('.cep-mask').mask('00000-000');
    $('.cnpj-mask').mask('00.000.000/0000-00');
    $(".brl-mask").maskMoney({prefix:'R$ ', allowNegative: false, thousands:'.', decimal:',', affixesStay: false});
  });