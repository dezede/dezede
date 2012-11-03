function add_small_caps(ed) {

    ed.addButton('smallcaps', {
        title: 'Petites capitales',
        image: '/static/tiny_mce/themes/advanced/img/smallcaps.gif',
        onclick: function(){
            ed.focus();
            ed.formatter.toggle('smallcaps');
        }
    });

    ed.onNodeChange.add(function(ed, cm, e) {
        cm.setActive('smallcaps', ed.formatter.match('smallcaps'));
        ed.undoManager.add();
    });

}
