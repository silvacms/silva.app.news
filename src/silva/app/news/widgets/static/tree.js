(function ($) {

    function create_trees() {
        var $trees = $(this).find(".field-tree-widget");

        $trees.each(function () {
            var $tree = $(this);
            var $input = $tree.siblings('input.field-tree');

            $tree.jstree({
                core: {
                    animation: 100
                },
                plugins: ["html_data", "ui", "checkbox"]
            });

            $tree.delegate('a', 'click', function() {
                var values = [];

                $.each($tree.jstree('get_checked'), function() {
                    values.push($(this).attr('id'));
                });
                $input.val(values.join('|'));
                $input.change();
            });
        });
    };

    $('.form-fields-container').live('loadwidget-smiform', function(event) {
        $(this).invoke(create_trees);
        event.stopPropagation();
    });

    $(document).ready(create_trees);

})(jQuery);
