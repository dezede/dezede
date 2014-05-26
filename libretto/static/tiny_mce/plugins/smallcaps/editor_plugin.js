(function() {

  tinymce.create('tinymce.plugins.SmallCapsPlugin', {
    init : function(ed, url) {
      ed.onInit.add(function(ed) {
        ed.formatter.register('smallcaps', {inline : 'span', classes: 'sc'});
      });

      ed.addCommand('mceSmallCaps', function() {
        ed.focus();
        ed.formatter.toggle('smallcaps');
      });

      ed.addButton('smallcaps', {
        title: 'Petites capitales',
        cmd: 'mceSmallCaps',
        image: url + '/img/smallcaps.gif'
      });

      ed.onNodeChange.add(function(ed, cm, n) {
        cm.setActive('smallcaps', ed.formatter.match('smallcaps'));
        ed.undoManager.add();
      });
    }
  });

  // Register plugin
  tinymce.PluginManager.add('smallcaps', tinymce.plugins.SmallCapsPlugin);
})();
